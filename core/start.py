import ast
import os
import sys
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
from urlparse import parse_qs

from checker import GoogleIPChecker

PORT_NUM = 9494

cur_path = os.path.dirname(os.path.abspath(__file__))
ui_path = os.path.join(cur_path, os.path.pardir, 'ui')
checker = GoogleIPChecker()


# noinspection PyBroadException
class HTTPRequestHandler(BaseHTTPRequestHandler):
    def __init__(self, request, client_address, server):
        BaseHTTPRequestHandler.__init__(self, request, client_address, server)
        self.path = '/'

    def send_file(self, filepath, mimetype):
        try:
            f = open(filepath, 'rb')
            self.send_response(200)
            self.send_header('Content-type', mimetype)
            self.end_headers()
            self.wfile.write(f.read())
            f.close()
        except:
            self.send_error(404, 'File Not Found: %s' % filepath)

    def do_GET(self):
        if self.path == '/':
            self.path = '/index.html'
        if self.path.startswith('/range_status'):
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(checker.handle_get_range_status())
            return
        if self.path.startswith('/ip_status'):
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(checker.handle_get_ip_status())
            return
        if self.path.startswith('/running_status'):
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(checker.handle_get_running_status())
            return
        if self.path.endswith('.html'):
            mimetype = 'text/html'
        elif self.path.endswith('.png'):
            mimetype = 'image/png'
        elif self.path.endswith('.jpg') or self.path.endswith('.jpeg'):
            mimetype = 'image/jpeg'
        elif self.path.endswith('.gif'):
            mimetype = 'image/gif'
        elif self.path.endswith('.css'):
            mimetype = 'text/css'
        elif self.path.endswith('.js'):
            mimetype = 'application/javascript'
        else:
            mimetype = 'application/octet-stream'
        file_path = os.path.abspath(os.path.join(ui_path, '/'.join(self.path.split('/')[1:])))
        self.send_file(file_path, mimetype)
        return

    def do_POST(self):
        if self.path.startswith('/check'):
            length = int(self.headers['content-length'])
            params = parse_qs(self.rfile.read(length), keep_blank_values=1)
            checker.handle_post_check_ranges(ast.literal_eval(params['ranges'][0]))
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write('{"Status": "START"}')
            return
        if self.path.startswith('/delete'):
            length = int(self.headers['content-length'])
            params = parse_qs(self.rfile.read(length), keep_blank_values=1)
            checker.handle_post_delete_ranges(ast.literal_eval(params['ranges'][0]))
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write('{"Status": "OK"}')
            return
        if self.path.startswith('/save'):
            checker.handle_post_save_lib()
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write('{"Status": "OK"}')
            return
        if self.path.startswith('/cancel'):
            checker.handle_post_cancel()
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write('{"Status": "OK"}')
            return
        if self.path.startswith('/reload'):
            checker.handle_post_load_lib()
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write('{"Status": "OK"}')
            return
        if self.path.startswith('/export_range'):
            length = int(self.headers['content-length'])
            params = parse_qs(self.rfile.read(length), keep_blank_values=1)
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(checker.handle_post_export_range(params['method'][0]))
            return
        if self.path.startswith('/export_ip'):
            length = int(self.headers['content-length'])
            params = parse_qs(self.rfile.read(length), keep_blank_values=1)
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(checker.handle_post_export_ip(params['method'][0]))
            return
        if self.path.startswith('/import'):
            length = int(self.headers['content-length'])
            params = parse_qs(self.rfile.read(length), keep_blank_values=1)
            checker.handle_post_import_ranges(ast.literal_eval(params['ranges'][0]))
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write('{"Status": "OK"}')
            return

if __name__ == '__main__':
    try:
        httpd = HTTPServer(('', PORT_NUM), HTTPRequestHandler)
        httpd.serve_forever()
    except KeyboardInterrupt:
        httpd.shutdown()
        httpd.server_close()
        sys.exit(0)