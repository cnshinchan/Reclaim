import Queue
import httplib
import json
import socket
import threading
import time
import re
import urllib2

MAX_TIME_OUT = 3
MAX_THREAD_NUM = 80
RANGE_DB_FILE = 'range_db.json'
COUNTRY_DB_FILE = 'country.json'


# noinspection PyBroadException
class GoogleIPChecker:
    def __init__(self):
        self._lib = dict()
        self.handle_post_load_lib()

        self._lock = threading.Lock()
        self._max_check_thread_num = MAX_THREAD_NUM

        self._threads = []
        self._country_thread = None

        self._ip_pool = Queue.Queue()
        self._country_pool = Queue.Queue()

        self._ip_found = dict()
        self._total_num = 0
        self._checked_num = 0
        self._is_running = False
        self._is_canceling = True

        self._country_lib = dict()
        self.load_country_lib()

    @staticmethod
    def ip_to_int(ip):
        return reduce(lambda a, b: a << 8 | b, map(int, ip.split('.')))

    @staticmethod
    def int_to_ip(_int):
        return '.'.join(map(lambda n: str(_int >> n & 0xFF), [24, 16, 8, 0]))

    @staticmethod
    def ip_to_range(ip):
        return '%s.0/24' % ip[0:ip.rfind('.')]

    @staticmethod
    def is_valid_location(loc):
        return loc == 'http://www.google.com/'

    @staticmethod
    def is_valid_server(srv):
        return srv == 'gws'

    @staticmethod
    def get_server(cn):
        if cn == '*.googlevideo.com' or cn == '*.c.docs.google.com':
            return 'gvs'
        else:
            return 'gws'

    @staticmethod
    def check_ip_cert(ip):
        socket.setdefaulttimeout(MAX_TIME_OUT)
        conn = httplib.HTTPSConnection(ip)
        try:
            conn.request('GET', '/')
        except Exception, e:
            m = re.search(r'doesn\'t match either of \'(.*?)\'', e.message)
            if m is not None:
                return m.group(1)
        return ''

    @staticmethod
    def get_split(method):
        if 'VB' in method:
            end = '|'
        elif 'QC' in method:
            end = ","
        else:
            if 'CM' in method:
                end = ',\r\n'
            else:
                end = '\r\n'
        return end

    @staticmethod
    def get_format(method, item, end):
        if 'QC' in method:
            return '"%s"%s' % (item, end)
        else:
            return '%s%s' % (item, end)

    def check_country(self, rng):
        try:
            r = urllib2.urlopen('http://ipinfo.io/%s.1/country' % rng[0:rng.rfind('.')])
            result = r.read()
            if len(result) == 3:
                self._lock.acquire()
                self._lib[rng]['CC'] = result[0:2]
                self._lock.release()
        except:
            return

    def import_ip_from_range(self, rng):
        if rng in self._lib and self._lib[rng]['CC'] != '':
            pass
        else:
            self._country_pool.put(rng)
        if rng in self._lib:
            self._lib[rng]['FC'] = 0
            self._lib[rng]['MAX'] = -9999
            self._lib[rng]['MIN'] = 9999
            self._lib[rng]['TP'] = ''
        else:
            self._lib[rng] = {
                'FC': 0,
                'MAX': -9999,
                'MIN': 9999,
                'TP': '',
                'CC': '',
                'NF': True
            }
        _start = self.ip_to_int('%s.1' % rng[0:rng.rfind('.')])
        _end = self.ip_to_int('%s.255' % rng[0:rng.rfind('.')])
        for ip in range(_start, _end):
            self._ip_pool.put(self.int_to_ip(ip))

    def check_ip(self, ip):
        socket.setdefaulttimeout(MAX_TIME_OUT)
        result = self._lib[self.ip_to_range(ip)]
        conn = httplib.HTTPConnection(ip, port=80)
        try:
            conn.request('GET', '/')
            st = time.time()
            res = conn.getresponse(buffering=True)
            speed = int((time.time() - st) * 1000)
            loc = res.getheader('location')
            server = res.getheader('Server')
            if self.is_valid_location(loc) and self.is_valid_server(server):
                cn = self.check_ip_cert(ip)
                if cn != '':
                    self._lock.acquire()
                    result['FC'] += 1
                    result['NF'] = False
                    result['MAX'] = speed if speed > result['MAX'] else result['MAX']
                    result['MIN'] = speed if speed < result['MIN'] else result['MIN']
                    ir = {
                        'IP': ip,
                        'SP': speed,
                        'CN': cn,
                        'TP': self.get_server(cn)
                    }
                    if result['TP'] == '':
                        result['TP'] = ir['TP']
                    else:
                        if result['TP'] != 'gws/gvs':
                            if result['TP'] != ir['TP']:
                                result['TP'] = 'gws/gvs'

                    self._ip_found[ip] = ir
                    self._lock.release()
                    return True
            return False
        except:
            # # [Errno 10054] An existing connection was forcibly closed by the remote host
            return False
        finally:
            self._lock.acquire()
            self._checked_num += 1
            if self._checked_num == self._total_num:
                self._is_running = False
            self._lock.release()
            if conn:
                conn.close()

    def do_check_range(self):
        while not self._is_canceling:
            try:
                ip = self._ip_pool.get_nowait()
                self.check_ip(ip)
            except:
                return

    def do_check_country(self):
        while not self._is_canceling:
            try:
                rng = self._country_pool.get_nowait()
                self.check_country(rng)
            except:
                return

    def check_countries(self):
        size = self._country_pool.qsize()
        if size > 0:
            self._country_thread = threading.Thread(target=self.do_check_country)
            self._country_thread.daemon = True
            self._country_thread.start()

    def load_country_lib(self):
        try:
            with open(COUNTRY_DB_FILE, 'r') as lib:
                l = lib.readline()
                self._country_lib = json.loads(l)
        except:
            return

    def handle_get_range_status(self):
        st = {
            'data': []
        }
        for r in self._lib:
            rng = []
            rng.append(self.ip_to_int('%s.1' % r[0:r.rfind('.')]))
            rng.append(r)
            rng.append(self._lib[r]['CC'])
            if self._lib[r]['CC'] in self._country_lib:
                rng.append(self._country_lib[self._lib[r]['CC']])
            else:
                rng.append('')
            rng.append(self._lib[r]['TP'])
            rng.append(self._lib[r]['FC'])
            rng.append(self._lib[r]['MIN'])
            rng.append(self._lib[r]['MAX'])
            rng.append(self._lib[r]['NF'])
            st['data'].append(rng)
        return json.dumps(st)

    def handle_get_ip_status(self):
        st = {
            'data': []
        }
        for ip in self._ip_found:
            ir = []
            ir.append(self.ip_to_int(self._ip_found[ip]['IP']))
            ir.append(self._ip_found[ip]['IP'])
            ir.append(self._ip_found[ip]['CN'])
            ir.append(self._ip_found[ip]['TP'])
            ir.append(self._ip_found[ip]['SP'])
            st['data'].append(ir)
        return json.dumps(st)

    def handle_get_running_status(self):
        return '{"Running": %s, "CurCount": %s, "TotalCount": %s}' % \
               (json.dumps(self._is_running), self._checked_num, self._total_num)

    def handle_post_check_ranges(self, rngs):
        if self._is_running:
            return
        self._ip_pool.queue.clear()
        self._country_pool.queue.clear()
        self._threads = []
        self._is_running = True
        self._is_canceling = False
        for rng in rngs:
            self.import_ip_from_range(rng)
        self.check_countries()
        self._total_num = self._ip_pool.qsize()
        self._checked_num = 0
        size = self._total_num
        size = size if size < self._max_check_thread_num else self._max_check_thread_num
        if size == 0:
            self._is_running = False
            self._is_canceling = True
        for i in range(size):
            t = threading.Thread(target=self.do_check_range)
            self._threads.append(t)
            t.daemon = True
            t.start()

    def handle_post_delete_ranges(self, rngs):
        for rng in rngs:
            if rng in self._lib:
                del self._lib[rng]

    def handle_post_delete_ips(self, ips):
        for ip in ips:
            if ip in self._ip_found:
                del self._ip_found[ip]

    def handle_post_load_lib(self):
        try:
            with open(RANGE_DB_FILE, 'r') as lib:
                l = lib.readline()
                self._lib = json.loads(l)
        except:
            return

    def handle_post_save_lib(self):
        try:
            with open(RANGE_DB_FILE, 'w') as lib:
                lib.write(json.dumps(self._lib))
        except:
            return

    def handle_post_cancel(self):
        self._is_canceling = True
        if self._country_thread is not None:
            self._country_thread.join()
        for t in self._threads:
            if t is not None:
                t.join()
        self._checked_num = self._total_num
        self._is_running = False

    def handle_post_export_range(self, method):
        end = self.get_split(method)
        rngs = ''
        for rng in self._lib:
            rngs += self.get_format(method, rng, end)
        if rngs.endswith('|'):
            return rngs[:-1]
        if rngs.endswith('\r\n'):
            return rngs[:-2]
        return rngs

    def handle_post_export_ip(self, method):
        end = self.get_split(method)
        ips = ''
        for ip in self._ip_found:
            ips += self.get_format(method, ip, end)
        if ips.endswith('|'):
            return ips[:-1]
        if ips.endswith('\r\n'):
            return ips[:-2]
        return ips

    def handle_post_import_ranges(self, rngs):
        for rng in rngs:
            if rng not in self._lib:
                self._lib[rng] = {
                    'FC': 0,
                    'MAX': -9999,
                    'MIN': 9999,
                    'TP': '',
                    'CC': '',
                    'NF': True
                }

if __name__ == '__main__':
    pass
