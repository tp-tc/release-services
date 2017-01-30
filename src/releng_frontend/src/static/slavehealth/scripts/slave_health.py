#!/usr/bin/env python
import argparse
import os
import re
import shutil
import simplejson as json

from sqlalchemy import *
from pytz import timezone
from datetime import datetime, date

from config_testers import SLAVES as TEST_SLAVES
from config_builders import SLAVES as BUILD_SLAVES, TRY_SLAVES

from last_build_creds import db_host, db_name, db_user, db_pass, \
  slavealloc_db_host, slavealloc_db_name, slavealloc_db_user, slavealloc_db_pass

import logging
log = logging.getLogger(__name__)

slavealloc_slavestate = {}
masters = {}
TALOS_SLAVES={}
STAGING={}
EC2={}
NOT_IN_SLAVEALLOC={}
DECOMM={}
NO_JOBS={}
NEED_REBOOT={}

# These are slave types for which we have no recent job data. This usually
# means the slave type has been retired.
IGNORE_SLAVE_TYPES = ['try-linux64-ec2',
                      'tst-linux64-ec2',
                      'tst-linux32-ec2',
                      't-mavericks-r5',
                      'b-2008-sm',
                      'tst-w64-ec2',
                      'av-linux64']

dthandler = lambda obj: obj.isoformat() + 'Z' if isinstance(obj, datetime) else None

def GetMasters():
    m = slavealloc_meta.tables['masters']

    q=select([m.c.nickname,
              m.c.fqdn,
              m.c.http_port], from_obj=[m]);

    query_results = slavealloc_conn.execute(q)
    for r in query_results:
        masters[r['nickname']] = r['fqdn'] + ":" + str(r['http_port'])
    return True

def GetSlaveAllocNotes():
    s = slavealloc_meta.tables['slaves']
    m = slavealloc_meta.tables['masters']

    q=select([s.c.name,
              s.c.notes,
              s.c.enabled,
              s.c.envid,
              m.c.nickname,
              m.c.fqdn,
              m.c.http_port,
              ], from_obj=[s.outerjoin(m, s.c.current_masterid.__eq__(m.c.masterid))])

    query_results = slavealloc_conn.execute(q)
    for r in query_results:
        name = None
        this_result = {}
        for key,value in r.items():
            if key == 'name':
                name = value;
            else:
                this_result[key] = value
        if name is not None:
            slavealloc_slavestate[name] = this_result
    return True

def GetHistoricBuilds(slave, count=1):
    b  = meta.tables['builds']
    bs = meta.tables['builders']
    s  = meta.tables['slaves']
    m  = meta.tables['masters']
    q = select([
                s.c.name,
                b.c.starttime,
                b.c.endtime,
                bs.c.name.label('buildname'),
                b.c.result,
                m.c.name.label('master'),
            ])
    # joins
    q = q.where(and_(b.c.slave_id==s.c.id,
                     b.c.builder_id==bs.c.id,
                     b.c.master_id==m.c.id))
    # condition: right slave
    q = q.where(s.c.name == slave)
    # condition: jobs must be finished, avoids 1970 endtimes
    q = q.where(and_(b.c.result != None,
                     b.c.endtime > date(1971,1,1)))
    # limit
    q = q.order_by(b.c.id.desc()).limit(count)

    query_results = conn.execute(q)

    builds = []
    for r in query_results:
        this_result = {}
        for key,value in r.items():
            if key in ('starttime','endtime'):
                this_result[str(key)] = value.replace(tzinfo=utc).astimezone(pacific).replace(tzinfo=None)
            else:
                this_result[str(key)] = value
        if 'starttime' in this_result and 'endtime' in this_result:
            this_result['elapsed_on_job'] = this_result['endtime'] - this_result['starttime']
        if 'starttime' in this_result:
            this_result['elapsed_since_job'] = now - this_result['endtime']
            this_result['elapsed_since_job_secs'] = this_result['elapsed_since_job'].seconds + this_result['elapsed_since_job'].days*one_day
            if this_result['elapsed_since_job_secs'] < 0:
                this_result['elapsed_since_job_secs'] = 0
                this_result['elapsed_since_job'] = 0

        builds.append(this_result)

    return builds

def get_slave_type(slave_class, slave_name):
    for slave_type in slave_state_rollup[slave_class].keys():
        if slave_name.startswith(slave_type):
            return slave_type
    for ignore in IGNORE_SLAVE_TYPES:
        if ignore in slave_name:
            return None
    if 'golden' not in slave_name:
        log.warn("Unknown slave_type for %s: %s" % (slave_class, slave_name))
    return None

def write_file(filename, contents):
    f = open(filename, 'w')
    f.write(contents)
    f.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.set_defaults(
        log_level=logging.INFO,
        output_dir="./logs",
        logfile="slave_health.log",
    )
    parser.add_argument("-v", "--verbose", action="store_const", const=logging.DEBUG, dest="log_level")
    parser.add_argument("-q", "--quiet", action="store_const", const=logging.WARN, dest="log_level")
    parser.add_argument("-l", "--logfile", dest="logfile")
    parser.add_argument("-o", "--output-dir", dest="output_dir")
    args = parser.parse_args()

    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)

    logfile = os.path.join(args.output_dir, args.logfile)
    logging.basicConfig(level=args.log_level, format="%(asctime)s - %(levelname)s - %(message)s", filename=logfile)

    log.debug("Begin processing.")

    # init the timezone shenanigans
    pacific = timezone('US/Pacific')
    utc = timezone('UTC')
    now = datetime.now().replace(microsecond=0)
    generated = datetime.utcnow()
    five_hours = 60*60*5
    one_day = 60*60*24
    one_week = one_day*7
    all_slaves = {}

    # init the db
    engine = create_engine('mysql://%s:%s@%s/%s' % (db_user,
                                                    db_pass,
                                                    db_host,
                                                    db_name),
                           echo=False)
    meta = MetaData()
    meta.reflect(bind=engine)
    conn = engine.connect()

    # init the slavealloc db
    slavealloc_engine = create_engine('mysql://%s:%s@%s/%s' % (slavealloc_db_user,
                                                               slavealloc_db_pass,
                                                               slavealloc_db_host,
                                                               slavealloc_db_name),
                                      echo=False)
    slavealloc_meta = MetaData()
    slavealloc_meta.reflect(bind=slavealloc_engine)
    slavealloc_conn = slavealloc_engine.connect()
    GetSlaveAllocNotes()

    GetMasters()

    slave_state_rollup = {
        'metadata': {
            'generated': generated,
            },
        'build': {
            'bld-linux64-spot': {},
            'bld-lion-r5': {},
            'b-2008-spot': {},
            },
        'try': {
            'try-linux64-spot': {},
            'bld-lion-r5': {},
            'y-2008-spot': {},
            },
        'test': {
            'tst-emulator64-spot': {},
            'talos-linux64-ix': {},
            'tst-linux32-spot': {},
            'tst-linux64-spot': {},
            't-snow-r4': {},
            't-yosemite-r7': {},
            'g-w732-spot': {},
            't-w732-ix': {},
            't-w732-spot': {},
            't-w864-ix': {},
            't-xp32-ix': {},
            't-w1064-ix': {},
            },
        }

    slave_types = {}
    already_processed = {}

    for slave_class in slave_state_rollup:
      if slave_class == 'metadata':
        continue
      for slave_type in slave_state_rollup[slave_class]:
        for state in ['broken', 'hung', 'slow', 'working', 'disabled', 'staging', 'not_in_slavealloc', 'decommissioned', 'pending_builds']:
          slave_state_rollup[slave_class][slave_type][state] = 0

    for slave_class, SLAVES in [['try',   TRY_SLAVES],
                                ['build', BUILD_SLAVES],
                                ['test',  TEST_SLAVES],
                                ]:
        for opsys in SLAVES:
            for slave_name in SLAVES[opsys]:
                if already_processed.has_key(slave_name):
                    log.debug("Already processed in another class: %s" % slave_name)
                    continue
                else:
                    already_processed[slave_name] = 1;
                if 'tegra' in slave_name:
                    continue
                slave_type = get_slave_type(slave_class, slave_name)
                if not slave_type:
                    continue
                if (not slavealloc_slavestate.has_key(slave_name)):
                    slave_state_rollup[slave_class][slave_type]['not_in_slavealloc'] += 1;
                    continue
                if (slavealloc_slavestate[slave_name].has_key('envid') and
                    slavealloc_slavestate[slave_name]['envid'] == 5):
                    slave_state_rollup[slave_class][slave_type]['decommissioned'] += 1;
                    continue
                if ((slavealloc_slavestate[slave_name].has_key('envid') and
                     slavealloc_slavestate[slave_name]['envid'] == 3) or
                    (slavealloc_slavestate[slave_name].has_key('notes') and
                     slavealloc_slavestate[slave_name]['notes'] is not None and
                     'staging' in slavealloc_slavestate[slave_name]['notes'].lower())):
                    slave_state_rollup[slave_class][slave_type]['staging'] += 1;
                    continue
                b = GetHistoricBuilds(slave_name)
                if b:
                    b = b[0]
                else:
                    if id != 'nojobs':
                        NO_JOBS[slave_name] = True
                        continue
                    else:
                        b = {'name': slave_name, 'elapsed_since_job': 'No jobs yet', 'elapsed_since_job_secs': 0,
                             'master': '', 'starttime': '',
                             'elapsed_on_job': '', 'result': '', 'buildname': ''}

                row_class = "working"
                notes = ""
                b['enabled'] = 'Unknown'
                if b.has_key('elapsed_since_job_secs'):
                    if b['elapsed_since_job_secs'] > five_hours:
                        row_class = "broken"
                    #elif b['elapsed_since_job_secs'] > one_day:
                    #    row_class = "hung"
                    #elif b['elapsed_since_job_secs'] > five_hours:
                    #    row_class = "slow"
                if slavealloc_slavestate[slave_name]['enabled'] == 1:
                    b['enabled'] = 'Yes'
                else:
                    b['enabled'] = 'No'
                    row_class = 'disabled'
                if not slave_type in slave_state_rollup[slave_class]:
                    log.debug("Adding %s..." % slave_type)
                    slave_state_rollup[slave_class][slave_type] = {}
                if not row_class in slave_state_rollup[slave_class][slave_type]:
                    slave_state_rollup[slave_class][slave_type][row_class] = 1;
                else:
                    slave_state_rollup[slave_class][slave_type][row_class] += 1;
                slave_state = row_class

                if slave_name in slavealloc_slavestate:
                    if slavealloc_slavestate[slave_name]['fqdn'] != "":
                        link = '<a href="http://%s:%s/buildslaves/%s?numbuilds=0">%s</a>' % \
                               (slavealloc_slavestate[slave_name]['fqdn'],
                                slavealloc_slavestate[slave_name]['http_port'],
                                slave_name,
                                slavealloc_slavestate[slave_name]['nickname'])
                        b['master'] = link
                    if slavealloc_slavestate[slave_name]['notes'] is not None:
                        notes = slavealloc_slavestate[slave_name]['notes']
                        # Markup URLs with links.
                        notes = re.sub("(?<= )(https?://\S+)(?= )",
                                       lambda m: "<a href='%s'>%s</a>" % \
                                           (m.group(1),m.group(1)), notes)
                        # Markup bug numbers as links to bugzilla.
                        notes = re.sub("(?<=)(bug\#*\ *)(\d+)(?=.*)",
                                       lambda m: "<a href='https://bugzil.la/%s'>%s%s</a>" % \
                                           (m.group(2), m.group(1), m.group(2)), notes)
                b['notes'] = notes

                if b['elapsed_since_job_secs'] == 0:
                    slave_state = "no jobs"

                # Should we add this slave to the reboot list?
                if row_class not in ['working','no jobs']:
                    if b['notes'] == "":
                        NEED_REBOOT[b['name']] = b['enabled']

                slave_type_key = '%s-%s' % (slave_class, slave_type)
                if not slave_types.has_key("all_slaves"):
                    slave_types["all_slaves"] = {}
                if not slave_types.has_key(slave_type_key):
                    slave_types[slave_type_key] = {}

                if slave_types[slave_type_key].has_key(slave_name):
                    log.debug("Already processed in this class: %s" % slave_name)
                    continue
                else:
                    slave_types[slave_type_key][slave_name] = {}

                slave_types[slave_type_key][slave_name]['row_class'] = row_class
                slave_types[slave_type_key][slave_name]['elapsed_since_job'] = str(b['elapsed_since_job'])
                slave_types[slave_type_key][slave_name]['elapsed_since_job_secs'] = b['elapsed_since_job_secs']
                slave_types[slave_type_key][slave_name]['elapsed_on_job'] = str(b['elapsed_on_job'])
                slave_types[slave_type_key][slave_name]['slave_state'] = slave_state
                slave_types[slave_type_key][slave_name]['master'] = b['master']
                slave_types[slave_type_key][slave_name]['starttime'] = str(b['starttime'])
                slave_types[slave_type_key][slave_name]['notes'] = b['notes']
                slave_types[slave_type_key][slave_name]['enabled'] = b['enabled']
                slave_types[slave_type_key][slave_name]['slave_class'] = slave_class

                if slave_types["all_slaves"].has_key(slave_name):
                    log.debug("Already processed in 'all slaves': %s" % slave_name)
                    continue
                else:
                    slave_types["all_slaves"][slave_name] = {}

                slave_types["all_slaves"][slave_name]['row_class'] = row_class
                slave_types["all_slaves"][slave_name]['elapsed_since_job'] = str(b['elapsed_since_job'])
                slave_types["all_slaves"][slave_name]['elapsed_since_job_secs'] = b['elapsed_since_job_secs']
                slave_types["all_slaves"][slave_name]['elapsed_on_job'] = str(b['elapsed_on_job'])
                slave_types["all_slaves"][slave_name]['slave_state'] = slave_state
                slave_types["all_slaves"][slave_name]['master'] = b['master']
                slave_types["all_slaves"][slave_name]['starttime'] = str(b['starttime'])
                slave_types["all_slaves"][slave_name]['notes'] = b['notes']
                slave_types["all_slaves"][slave_name]['enabled'] = b['enabled']
                slave_types["all_slaves"][slave_name]['slave_class'] = slave_class


    for slave_type_key in slave_types:
        json_file = './slave_health/json/%s.json' % slave_type_key
        slave_types[slave_type_key]['metadata'] = {};
        slave_types[slave_type_key]['metadata']['generated'] = generated
        with open(json_file, 'wb') as fp:
            json.dump(slave_types[slave_type_key], fp, sort_keys=True, indent=4, default=dthandler)

    json_dir = './slave_health/json'
    trend_dir = '%s/trend_data/raw' % json_dir
    rollup_file = '%s/slave_state_rollup.json' % json_dir
    trend_file = '%s/slave_state_%s.json' % (trend_dir, now.isoformat())

    with open(rollup_file, 'wb') as fp:
        json.dump(slave_state_rollup, fp, sort_keys=True, indent=4, default=dthandler)
    if not os.path.exists(trend_dir):
        os.makedirs(trend_dir)
    shutil.copy(rollup_file, trend_file)

    with open('./slave_health/json/masters.json', 'wb') as fp:
        json.dump(masters, fp, sort_keys=True, indent=4, default=dthandler)
