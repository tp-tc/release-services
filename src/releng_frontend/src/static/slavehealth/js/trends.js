var build_slavetypes = [
    'bld-linux64-spot',
    'bld-lion-r5',
    'b-2008-spot',
];

var try_slavetypes = [
    'try-linux64-spot',
    'bld-lion-r5',
    'y-2008-spot',
];

var test_slavetypes = [
    'tst-emulator64-spot',
    'talos-linux64-ix',
    'tst-linux32-spot',
    'tst-linux64-spot',
    't-r4-snow',
    't-yosemite-r7',
    'g-w732-spot',
    't-w732-ix',
    't-w732-spot',
    't-w864-ix',
    't-w1064-ix',
    't-xp32-ix',
];

function display_chart(json_data, div_id, height, width) {
    zingchart.render({
        id : div_id,
        height : height,
        width : width,
        data : json_data
    });
}

function display_chart_from_url(json_file, div_id, height, width) {
    $.ajax({
        async: false,
        type: 'GET',
        url:  json_file,
        success: function (chart_json) {
            display_chart(chart_json, div_id, height, width);
        },
        error: function () {
            alert('Error retrieving ' + json_file);
        }
    });
}

function capitalize(string) {
    return string.charAt(0).toUpperCase() + string.slice(1);
}

function get_month_from_delta(month_delta) {
    var d = new Date();
    d.setMonth(d.getMonth() + month_delta);
    return dateToYM(d);
}

function get_last_month() {
    return get_month_from_delta(-1);
}

function get_date_from_delta(date_delta) {
    var d = new Date();
    d.setDate(d.getDate() + date_delta);
    return dateToYMD(d);
}

function get_yesterday() {
    return get_date_from_delta(-1);
}

function get_trend_dir(date_to_process) {
    var a = date_to_process.split('-');
    var year, month, day;
    if (a.length === 3) {
        year = a[0]; month = a[1]; day = a[2];
        return './json/trend_data/' + year + '/' + month + '/' + day + '/';
    } else if (a.length === 2) {
        year = a[0]; month = a[1];
        return './json/trend_data/' + year + '/' + month + '/';
    }
    return undefined;
}

function prepend_date(date_string, json_data) {
    var i, l;
    for (i = 0, l = json_data['graphset'][0]['scaleX']['values'].length; i < l; i++) {
        json_data['graphset'][0]['scaleX']['values'][i] = date_string + "\n" + json_data['graphset'][0]['scaleX']['values'][i];
    }
}

var weekly_charts = {};
function append_daily_data(slaveclass, date_string, json_data) {
    prepend_date(date_string, json_data);
    if ($.isEmptyObject(weekly_charts) || (weekly_charts[slaveclass] === 'undefined')) {
        weekly_charts[slaveclass] = json_data;
    } else {
        var i, l;
        for (i = 0, l = json_data['graphset'][0]['series'].length; i < l; i++) {
            if (typeof weekly_charts[slaveclass]['graphset'][0]['series'][i] !== 'undefined') {
                weekly_charts[slaveclass]['graphset'][0]['series'][i]['values'].push.apply(weekly_charts[slaveclass]['graphset'][0]['series'][i]['values'], json_data['graphset'][0]['series'][i]['values']);
            }
        }
        weekly_charts[slaveclass]['graphset'][0]['scaleX']['values'].push.apply(weekly_charts[slaveclass]['graphset'][0]['scaleX']['values'], json_data['graphset'][0]['scaleX']['values']);
    }
}

function generate_monthly_charts(slavetypes, slaveclass) {
    var month_to_process = getParameterByName('month');
    if (month_to_process === "" || (!month_to_process.match(/^\d\d\d\d-\d\d$/))) {
        month_to_process = get_last_month();
    }
    document.title = capitalize(slaveclass) + ' slave usage trends - ' + month_to_process;

    var trend_dir = get_trend_dir(month_to_process);
    var json_file = trend_dir + slaveclass + '_' + month_to_process + '.json';
    var div_id = slaveclass + 'Trend';
    display_chart_from_url(json_file, div_id, 700, 900);
    var parent_div = '#' + slaveclass + 'Trend';
    var j;
    for (j = 0; j < slavetypes.length; j++) {
        div_id = slavetypes[j] + 'Trend';
        json_file = trend_dir + slaveclass + '_' + slavetypes[j] + '_' + month_to_process + '.json';
        display_chart_from_url(json_file, div_id, 225, 300);
    }
}

function generate_weekly_charts(slavetypes, slaveclass) {
    // Reset weekly chart.
    weekly_charts = {};

    // We do this in two batches:
    // Batch 1: combined chart
    // Batch 2: per-platform charts
    // This is done so the per-platform charts are loaded *after* the combined chart is displayed.

    // Get last 7 days.
    var start_date = get_date_from_delta(-7);
    var end_date = get_date_from_delta(-1);
    var date_to_process, trend_dir, json_file;
    var i, j;
    for (i = 7; i > 0; i--) {
        date_to_process = get_date_from_delta(-i);
        trend_dir = get_trend_dir(date_to_process);
        json_file = trend_dir + slaveclass + '_' + date_to_process + '.json';
        $.ajax({
            async: false,
            type: 'GET',
            url:  json_file,
            success: function (chart_json) {
                append_daily_data(slaveclass, date_to_process, chart_json);
            },
            error: function () {
                alert('Error retrieving ' + json_file);
            }
        });
    }
    weekly_charts[slaveclass]['graphset'][0]['title']['text'] = slaveclass + ' slave trend - ' + start_date + ' to ' + end_date;
    var div_id = slaveclass + 'Trend';
    display_chart(weekly_charts[slaveclass], div_id, 700, 900);

    // Iterate over the individual slavetypes now that the aggregate is displayed
    for (i = 7; i > 0; i--) {
        date_to_process = get_date_from_delta(-i);
        trend_dir = get_trend_dir(date_to_process);
        for (j = 0; j < slavetypes.length; j++) {
            json_file = trend_dir + slaveclass + '_' + slavetypes[j] + '_' + date_to_process + '.json';
            $.ajax({
                async: false,
                type: 'GET',
                url:  json_file,
                success: function (chart_json) {
                    append_daily_data(slavetypes[j], date_to_process, chart_json);
                },
                error: function () {
                    alert('Error retrieving ' + json_file);
                }
            });
        }
    }
    for (j = 0; j < slavetypes.length; j++) {
        weekly_charts[slavetypes[j]]['graphset'][0]['title']['text'] = slavetypes[j] + ' slave trend - ' + start_date + ' to ' + end_date;
        div_id = slavetypes[j] + 'Trend';
        display_chart(weekly_charts[slavetypes[j]], div_id, 225, 300);
    }
}

function generate_daily_charts(slavetypes, slaveclass) {
    var date_to_process = getParameterByName('date');
    if (date_to_process === "" || !date_to_process.match(/^\d\d\d\d-\d\d-\d\d$/)) {
        date_to_process = get_yesterday();
    }
    document.title = capitalize(slaveclass) + ' slave usage trends - ' + date_to_process;

    var trend_dir = get_trend_dir(date_to_process);
    var json_file = trend_dir + slaveclass + '_' + date_to_process + '.json';
    var div_id = slaveclass + 'Trend';
    display_chart_from_url(json_file, div_id, 700, 900);
    var parent_div = '#' + slaveclass + 'Trend';
    var j;
    for (j = 0; j < slavetypes.length; j++) {
        div_id = slavetypes[j] + 'Trend';
        json_file = trend_dir + slaveclass + '_' + slavetypes[j] + '_' + date_to_process + '.json';
        display_chart_from_url(json_file, div_id, 225, 300);
    }
}
