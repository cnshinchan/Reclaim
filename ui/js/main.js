var ajax_get_status_is_running = false;

var timer_get_status;
var dt_table_range;
var dt_table_ip;
$(function () {
    $.ajax({
        type: 'GET',
        url: '/running_status'
    }).done(function (data) {
        if (!data['Running']) {
            showStartSearch();
        } else {
            showCancelSearch();
            timer_get_status = setInterval(getStatus, 1000);
        }
    })

    dt_table_range = $('#table_range').DataTable({
        "oLanguage": {
            "oPaginate": {
                "sNext": ">",
                "sPrevious": "<"
            }
        },
        "ajax": '../range_status',
        "deferRender": true,
        "iDisplayLength": 25,
        "order": [[1, "asc"]],
        "aoColumnDefs": [
            {
                "mData": 0,
                "aTargets": [0],
                "bVisible": false
            },
            {
                "mData": 1,
                "iDataSort": 0,
                "aTargets": [1],
                "sWidth": "120px"
            },
            {
                "mData": function (data) {
                    if (data[2] != "") {
                        return '<div class="country-container"><image src="images/flags/' + data[2] + '.png"></image></div>' + data[3];
                    } else {
                        return '';
                    }
                },
                "aTargets": [2],
            },
            {
                'mData': 4,
                'aTargets': [3],
                "sWidth": "30px"
            },
            {
                'mData': 5,
                'aTargets': [4],
                "sWidth": "20px",
                "sClass": "right"
            },
            {
                'mData': function (data) {
                    return data[6] == '9999' ? 0 : data[6];
                },
                'aTargets': [5],
                "sWidth": "20px",
                "sClass": "right"
            },
            {
                'mData': function (data) {
                    return data[7] == '-9999' ? 0 : data[7];
                },
                'aTargets': [6],
                "sWidth": "20px",
                "sClass": "right"
            },
            {
                'mData': function (data) {
                    return data[8] ? "X." : "";
                },
                'aTargets': [7],
                "sWidth": "20px",
                "sClass": "right"
            }
        ]
    });

    $('#table_range tbody').on('click', 'tr', function () {
        $(this).toggleClass('selected');
        updateSearchButtonStatus();
    });

    dt_table_ip = $('#table_ip').DataTable({
        "oLanguage": {
            "oPaginate": {
                "sNext": ">",
                "sPrevious": "<"
            }
        },
        "ajax": '../ip_status',
        "deferRender": true,
        "iDisplayLength": 25,
        "order": [[1, "asc"]],
        "aoColumnDefs": [
            {
                "mData": 0,
                "aTargets": [0],
                "bVisible": false
            },
            {
                "mData": 1,
                "iDataSort": 0,
                "aTargets": [1],
                "sWidth": "120px"
            },
            {
                "mData": 2,
                "aTargets": [2]
            },
            {
                'mData': 3,
                'aTargets': [3],
                "sWidth": "20px"
            },
            {
                'mData': 4,
                'aTargets': [4],
                "sWidth": "20px",
                "sClass": "right"
            }
        ]
    });

    updateSearchButtonStatus();
});

// button Handler
function handlerSelectAllRange() {
    $('#table_range tbody tr').addClass('selected');
    updateSearchButtonStatus();
}

function handlerDeselectAllRange() {
    $('#table_range tbody tr').removeClass('selected');
    updateSearchButtonStatus();
}

function handlerDeleteRange() {
    var rngs = new Array()
    var len = dt_table_range.rows('.selected').data().length;
    for (var i = 0; i < len; i++) {
        rngs.push(dt_table_range.rows('.selected').data()[i][1]);
    }
    $.ajax({
        type: 'POST',
        url: '/delete?_dc=' + new Date().getTime(),
        dataType: 'json',
        contentType: 'application/json',
        data: {
            'ranges': JSON.stringify(rngs)
        }
    }).done(function () {
        reloadTableRange();
    });
}

function handlerSaveRange() {
    $.ajax({
        type: 'POST',
        url: '/save?_dc=' + new Date().getTime()
    });
}

function handlerReload() {
    $.ajax({
        type: 'POST',
        url: '/reload?_dc=' + new Date().getTime(),
        dataType: 'json',
        contentType: 'application/json',
    }).done(function () {
        reloadTableRange();
    });
}

function handlerImportRange() {
    var rngs = getRanges();
    $.ajax({
        type: 'POST',
        url: '/import?_dc=' + new Date().getTime(),
        dataType: 'json',
        contentType: 'application/json',
        data: {
            'ranges': JSON.stringify(rngs)
        }
    }).done(function () {
        reloadTableRange();
    });
}

function handlerExportRange() {
    $.ajax({
        type: 'POST',
        url: '/export_range?_dc=' + new Date().getTime(),
        contentType: 'text/html',
        data: {
            'method': "LB"
        }
    }).done(function (data) {
        $('#txt_range').val(data);
    });
}

function handlerShowRangeContainer() {
    $('#range_container').css('display', 'block');
    $('#ip_container').css('display', 'none');
    $('#switch_range').removeClass('btn-default');
    $('#switch_range').addClass('btn-warning');
    $('#switch_ip').removeClass('btn-warning');
    $('#switch_ip').addClass('btn-default');
    dt_table_range.columns.adjust().draw();
}

function handlerShowIPContainer() {
    $('#range_container').css('display', 'none');
    $('#ip_container').css('display', 'block');
    $('#switch_range').removeClass('btn-warning');
    $('#switch_range').addClass('btn-default');
    $('#switch_ip').removeClass('btn-default');
    $('#switch_ip').addClass('btn-warning');
    dt_table_ip.columns.adjust().draw();
}

function handlerStartSearch() {
    var rngs = new Array()
    var len = dt_table_range.rows('.selected').data().length;
    for (var i = 0; i < len; i++) {
        rngs.push(dt_table_range.rows('.selected').data()[i][1]);
    }
    if (rngs.length == 0) {
        return;
    }
    showCancelSearch();

    $.ajax({
        type: 'POST',
        url: '/check?_dc=' + new Date().getTime(),
        dataType: 'json',
        contentType: 'application/json',
        data: {
            'ranges': JSON.stringify(rngs)
        }
    });

    timer_get_status = setInterval(getStatus, 1000);
}

function handlerCancelSearch() {
    cancel_frozen();
    $.ajax({
        type: 'POST',
        url: '/cancel?_dc=' + new Date().getTime()
    })
}

function handlerExportIP() {
    $.ajax({
        type: 'POST',
        url: '/export_ip?_dc=' + new Date().getTime(),
        contentType: 'text/html',
        data: {
            'method': 'VB'
        }
    }).done(function (data) {
        $('#txt_ip').val(data);
    });
}

// UI Handler
function reloadTableRange() {
    handlerDeselectAllRange();
    dt_table_range.ajax.reload();
}

function reloadTableIP() {
    dt_table_ip.ajax.reload();
}

function showStartSearch() {
    $('#panel_search').css('display', 'block');
    $('#panel_cancel').css('display', 'none');
}

function showCancelSearch() {
    $('#panel_search').css('display', 'none');
    $('#panel_cancel').css('display', 'block');
}

function updateSearchButtonStatus() {
    if(dt_table_range.rows('.selected').data().length > 0) {
        $('#btn_search').prop('disabled', false);
    } else{
        $('#btn_search').prop('disabled', true);
    }
}

function cancel_frozen() {
    $('#txt_cancel').text('Canceling...');
    $('#btn_cancel').prop('disabled', true);
}

function cancel_normal() {
    $('#txt_cancel').text('Cancel');
    $('#btn_cancel').prop('disabled', false);
}

function getStatus() {
    if (!ajax_get_status_is_running) {
        ajax_get_status_is_running = true;
        $.ajax({
            type: 'GET',
            url: '/running_status?_dc=' + new Date().getTime()
        }).done(function (data) {
            ajax_get_status_is_running = false;
            if (!data['Running']) {
                $('#txt_progress').text('Searching in progress...');
                clearInterval(timer_get_status);
                reloadTableRange();
                reloadTableIP();
                cancel_normal();
                showStartSearch();
            } else {
                var cur = data['CurCount'];
                var total = data['TotalCount'];
                $('#txt_progress').text('Searching ' + cur + ' of ' + total + ' ...');
            }
        }).error(function () {
            ajax_get_status_is_running = false;
        })
    }
}

function parseRange(rng) {
    var x = rng.split(".");
    if (x.length == 4) {
        var x1 = parseInt(x[0], 10);
        var x2 = parseInt(x[1], 10);
        var x3 = parseInt(x[2], 10);
        var x4 = parseInt(x[3], 10);
        if (isNaN(x1) || isNaN(x2) || isNaN(x3) || isNaN(x4)) {
            return false;
        }
        if ((x1 >= 0 && x1 <= 255) && (x2 >= 0 && x2 <= 255) && (x3 >= 0 && x3 <= 255) && (x4 >= 0 && x4 <= 255)) {
            return x1 + "." + x2 + "." + x3 + ".0/24";
        }
    }
    return "";
}

function getRanges() {
    var rngs = new Array();
    var dict = {};
    var src = $('#txt_range').val();
    var tmp = src.replace(/\"/g, "");
    tmp = tmp.replace(/\r\n|\r|\n/g, "|");
    tmp = tmp.replace(/-/g, "|");
    var arr = tmp.split('|');
    for (var i = 0; i < arr.length; i++) {
        var item = parseRange(arr[i]);
        if (item != "") {
            dict[item] = 0;
        }
    }
    for (var rng in dict) {
        rngs.push(rng);
    }
    return rngs;
}

