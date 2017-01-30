#!/usr/bin/env python

import argparse
import copy
import datetime
import fnmatch
import glob
import json
import os
import re

import logging
log = logging.getLogger(__name__)

trend_dir = "/home/buildduty/slave_health/slave_health/json/trend_data"
raw_dir = "%s/raw" % trend_dir
broken_hex = "#FF3333"
stopped_hex = "#FFCC00"
working_hex = "#009933"
disabled_hex = "#87CEEB"
staging_hex = "#870F96"
slave_states = [
    {
        'text': 'Broken',
        "line-color": broken_hex,
        "background-color": broken_hex,
        "marker": {
            "type": "circle",
            "border-color":"#000",
            "border-width":"1px",
            "background-color": broken_hex
        },
        'values': []
    },
    {
        'text': 'Working',
        "line-color": working_hex,
        "background-color": working_hex,
        "marker": {
            "type": "circle",
            "border-color":"#000",
            "border-width":"1px",
            "background-color": working_hex
        },
        'values': []
    },
    {
        'text': 'Disabled',
        "line-color": disabled_hex,
        "background-color": disabled_hex,
        "marker": {
            "type": "circle",
            "border-color":"#000",
            "border-width":"1px",
            "background-color": disabled_hex
        },
        'values': []
    },
    {
        'text': 'Staging',
        "line-color": staging_hex,
        "background-color": staging_hex,
        "marker": {
            "type": "circle",
            "border-color":"#000",
            "border-width":"1px",
            "background-color": staging_hex
        },
        'values': []
    },
    {
        'text': 'Stopped',
        "line-color": stopped_hex,
        "background-color": stopped_hex,
        "marker": {
            "type": "circle",
            "border-color":"#000",
            "border-width":"1px",
            "background-color": stopped_hex
        },
        'values': []
    },
]


daily_trends = {
    'build': copy.deepcopy(slave_states),
    'try':   copy.deepcopy(slave_states),
    'test':  copy.deepcopy(slave_states),
}

slaveclass_trends = {
    'build': {},
    'try':   {},
    'test':  {},
}

base_chart = {
    "show-progress": False,
    "graphset": [
        {
            "type": "area",
            "stacked": True,
            "legend": {},
            "crosshairX": {},
            "scaleX": { "label": { "text": "Time of Day"},
                        "values": [] },
            "scaleY": { "label": { "text": "# of slaves"}},
            "plot": {
                "spline": True,
                "alpha-area": 0.5,
                },
            "series": [],
        }
    ]
}

AWSre = re.compile('(ec2|spot)')

def generate_monthly_rollup(month_to_process):
    month_dir = '/'.join([trend_dir] + month_to_process.split('-'))
    if not os.path.isdir(month_dir):
        log.error("Month dir not found: %s" % month_dir)
        return

    month_json = {}
    file_filter = "*" + month_to_process + "*.json"
    for root, dirs, files in os.walk(month_dir):
        dirs.sort()
        files.sort()
        for json_file in fnmatch.filter(files, file_filter):
            m = re.search('^(.*)(\d\d\d\d-\d\d-\d\d).json', json_file)
            if m:
                file_root = m.group(1)
                day = m.group(2)
            else:
                continue
            f = open(os.path.join(root,json_file))
            json_data = json.load(f)
            f.close()
            # Prepend date to for all scale values
            json_data['graphset'][0]['scaleX']['values'] = [day + "\n" + s for s in json_data['graphset'][0]['scaleX']['values']]
            if file_root in month_json:
                for i in range(len(json_data['graphset'][0]['series'])):
                    try:
                        month_json[file_root]['graphset'][0]['series'][i]['values'].extend(json_data['graphset'][0]['series'][i]['values'])
                    except:
                        pass
                month_json[file_root]['graphset'][0]['scaleX']['values'].extend(json_data['graphset'][0]['scaleX']['values'])
            else:
                month_json[file_root] = json_data
                m = re.search('^(.* - )\d\d\d\d-\d\d-\d\d', month_json[file_root]['graphset'][0]['title']['text'])
                if m:
                    month_json[file_root]['graphset'][0]['title']['text'] = m.group(1) + month_to_process

    for file_root in month_json:
        month_file = os.path.join(trend_dir, month_dir, file_root + month_to_process + ".json")
        with open(month_file, 'wb') as fp:
            json.dump(month_json[file_root], fp, indent=4)

def generate_daily_rollup(date_to_process):
    os.chdir(raw_dir)
    matching_files = glob.glob("slave_state_%sT*.json" % date_to_process)

    for matching_file in sorted(matching_files):
        m = re.search('slave_state_\d\d\d\d-\d\d-\d\dT(\d\d:\d\d:\d\d).json', matching_file)
        if m:
            ts = m.group(1)
        else:
            continue
        base_chart['graphset'][0]['scaleX']['values'].append(ts)

        f = open(matching_file)
        json_data = json.load(f)
        f.close()
        for slaveclass in json_data:
            if slaveclass == 'metadata':
                continue
            if not slaveclass_trends.has_key(slaveclass):
                print "Unknown slaveclass: %s - skipping" % slaveclass
                continue

            slaveclass_broken = 0
            slaveclass_working = 0
            slaveclass_disabled = 0
            slaveclass_staging = 0
            slaveclass_stopped = 0
            for slavetype in json_data[slaveclass]:
                if not slaveclass_trends[slaveclass].has_key(slavetype):
                    slaveclass_trends[slaveclass][slavetype] = copy.deepcopy(slave_states)
                slaveclass_trends[slaveclass][slavetype][1]['values'].append(json_data[slaveclass][slavetype]['working'])
                slaveclass_trends[slaveclass][slavetype][2]['values'].append(json_data[slaveclass][slavetype]['disabled'])
                slaveclass_trends[slaveclass][slavetype][3]['values'].append(json_data[slaveclass][slavetype]['staging'])
                if AWSre.search(slavetype):
                    slaveclass_trends[slaveclass][slavetype][0]['values'].append(0);
                    slaveclass_trends[slaveclass][slavetype][4]['values'].append(json_data[slaveclass][slavetype]['broken'])
                    slaveclass_stopped += json_data[slaveclass][slavetype]['broken']
                else:
                    slaveclass_trends[slaveclass][slavetype][0]['values'].append(json_data[slaveclass][slavetype]['broken'])
                    slaveclass_trends[slaveclass][slavetype][4]['values'].append(0);
                    slaveclass_broken += json_data[slaveclass][slavetype]['broken']
                slaveclass_working += json_data[slaveclass][slavetype]['working']
                slaveclass_disabled += json_data[slaveclass][slavetype]['disabled']
                slaveclass_staging += json_data[slaveclass][slavetype]['staging']
            daily_trends[slaveclass][0]['values'].append(slaveclass_broken)
            daily_trends[slaveclass][1]['values'].append(slaveclass_working)
            daily_trends[slaveclass][2]['values'].append(slaveclass_disabled)
            daily_trends[slaveclass][3]['values'].append(slaveclass_staging)
            daily_trends[slaveclass][4]['values'].append(slaveclass_stopped)

    m = re.search('(\d\d\d\d)-(\d\d)-(\d\d)', date_to_process)
    year = m.group(1)
    month = m.group(2)
    day = m.group(3)
    day_dir = '%s/%s/%s/%s' % (trend_dir, year, month, day)
    if not os.path.exists(day_dir):
        os.makedirs(day_dir)
    for slaveclass in ['build', 'try', 'test']:
        daily_chart = copy.deepcopy(base_chart)
        for index in range(len(daily_trends[slaveclass])):
            daily_chart['graphset'][0]['series'].append(daily_trends[slaveclass][index])
        daily_chart['graphset'][0]['title'] = {'text': '%s slave trend - %s' % (slaveclass, date_to_process)}
        daily_filename = "%s/%s_%s.json" % (day_dir, slaveclass, date_to_process)
        with open(daily_filename, 'wb') as fp:
            json.dump(daily_chart, fp, indent=4)
        for slavetype in slaveclass_trends[slaveclass]:
            slavetype_chart = copy.deepcopy(base_chart)
            slavetype_filename = "%s/%s_%s_%s.json" % (day_dir, slaveclass, slavetype, date_to_process)
            for index in range(len((slaveclass_trends[slaveclass][slavetype]))):
                slavetype_chart['graphset'][0]['series'].append(slaveclass_trends[slaveclass][slavetype][index])
                slavetype_chart['graphset'][0]['title'] = {'text': '%s %s slave trend - %s' % (slaveclass, slavetype, date_to_process)}
                with open(slavetype_filename, 'wb') as fp:
                    json.dump(slavetype_chart, fp, indent=4)

    # We can remove the raw data now that we've created the daily roll-ups.
    os.chdir(raw_dir)
    for matching_file in sorted(matching_files):
        os.remove(matching_file)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.set_defaults(
        log_level=logging.INFO,
        output_dir="/home/buildduty/slave_health/logs",
        logfile="generate_chart_objects.log",
    )
    parser.add_argument("-v", "--verbose", action="store_const", const=logging.DEBUG, dest="log_level")
    parser.add_argument("-q", "--quiet", action="store_const", const=logging.WARN, dest="log_level")
    parser.add_argument("-m", "--monthly", help="Collate a week's worth of data into a single chart",
                        action="store_true")
    parser.add_argument("-d", "--date", help="Date to process")
    parser.add_argument("-l", "--logfile", dest="logfile")
    parser.add_argument("-o", "--output-dir", dest="output_dir")
    args = parser.parse_args()

    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)

    logfile = os.path.join(args.output_dir, args.logfile)
    logging.basicConfig(level=args.log_level, format="%(asctime)s - %(levelname)s - %(message)s", filename=logfile)

    log.debug("Begin processing.")

    date_to_process = args.date
    if args.monthly:
        if not date_to_process or not re.match(r'^\d\d\d\d-\d\d$', date_to_process):
            date_to_process = (datetime.datetime.utcnow().replace(day=1) - datetime.timedelta(days=1)).strftime('%Y-%m')
        log.debug("Processing month: %s" % date_to_process)
        generate_monthly_rollup(date_to_process)
    else:
        if not date_to_process or not re.match(r'^\d\d\d\d-\d\d-\d\d$', date_to_process):
            date_to_process = (datetime.date.today() - datetime.timedelta(1)).strftime('%Y-%m-%d')
        log.debug("Processing day: %s" % date_to_process)
        generate_daily_rollup(date_to_process)
    log.debug("Done processing.")
