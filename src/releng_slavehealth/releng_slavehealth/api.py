# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from __future__ import absolute_import

import html

import flask
import requests


BASE_URL = 'https://secure.pub.build.mozilla.org'

def create_proxy(name, path):
    if path == "js/jquery-ui-1.8.1.custom.min.js":
        return "", 200

    # fetch the url, and stream it back
    response = requests.get(
        BASE_URL + "/" + name + "/" + path,
        auth=(
            flask.current_app.config.get('MOZILLA_LDAP_USERNAME'),
            flask.current_app.config.get('MOZILLA_LDAP_PASSWORD'),
        ),
        params=flask.request.args,
    )

    headers = [
        header
        for header in response.raw.headers.items()
        if 'content-encoding' != header[0]
    ]

    # sometimes (not always) a buildapi returns json as html encoded string
    # no idea why, this is where we detect it and "fix" it
    content = response.content.decode('utf8')
    if content.startswith('<pre>'):
        content = html.unescape(content[5:-6])

    # reply with reponse from requests library
    return flask.Response(
        response=content,
        status=response.status_code,
        headers=headers,
        content_type=response.headers['content-type'],
    )


def slavealloc_proxy(path=""):
    return create_proxy("slavealloc", path)

def slaveapi_proxy(path=""):
    return create_proxy("slaveapi", path)

def buildapi_proxy(path=""):
    return create_proxy("buildapi", path)




null = None
false = False
true = True

def get_slaves():
    return {
        "b-linux64-hp-0010": {
            "elapsed_on_job": "0:07:26",
            "elapsed_since_job": "11 days, 20:07:24",
            "elapsed_since_job_secs": 1022844,
            "enabled": "No",
            "master": "<a href=\"http://None:None/buildslaves/b-linux64-hp-0010\">None</a>",
            "notes": "",
            "row_class": "disabled",
            "slave_class": "try",
            "slave_state": "disabled",
            "starttime": "2015-01-15 02:34:41"
        },
        "t-snow-r4-0001": {
            "elapsed_on_job": "0:04:42",
            "elapsed_since_job": "0:07:08",
            "elapsed_since_job_secs": 428,
            "enabled": "Yes",
            "master": "<a href=\"http://buildbot-master107.srv.releng.scl3.mozilla.com:8201/buildslaves/t-snow-r4-0001\">bm107-tests1-macosx</a>",
            "notes": "",
            "row_class": "working",
            "slave_class": "test",
            "slave_state": "working",
            "starttime": "2015-01-26 22:37:41"
        },

    }


def get_slaves_try(slave_type):
    return {
        "metadata": {
            "generated": "2014-09-25T15:40:06.063398Z"
        },
        "try-linux64-ec2-001": {
            "elapsed_on_job": "0:52:53",
            "elapsed_since_job": "43 days, 19:58:34",
            "elapsed_since_job_secs": 3787114,
            "enabled": "Yes",
            "master": "<a href=\"http://buildbot-master75.srv.releng.use1.mozilla.com:8101/buildslaves/try-linux64-ec2-001\">bm75-try1</a>",
            "notes": "",
            "row_class": "broken",
            "slave_state": "broken",
            "starttime": "2014-08-12 11:48:39"
        },
        "try-linux64-ec2-002": {
            "elapsed_on_job": "1:05:54",
            "elapsed_since_job": "112 days, 1:07:00",
            "elapsed_since_job_secs": 9680820,
            "enabled": "Yes",
            "master": "<a href=\"http://buildbot-master75.srv.releng.use1.mozilla.com:8101/buildslaves/try-linux64-ec2-002\">bm75-try1</a>",
            "notes": "",
            "row_class": "broken",
            "slave_state": "broken",
            "starttime": "2014-06-05 06:27:12"
        },
        "try-linux64-ec2-003": {
            "elapsed_on_job": "2:12:25",
            "elapsed_since_job": "111 days, 22:26:15",
            "elapsed_since_job_secs": 9671175,
            "enabled": "Yes",
            "master": "<a href=\"http://buildbot-master76.srv.releng.use1.mozilla.com:8101/buildslaves/try-linux64-ec2-003\">bm76-try1</a>",
            "notes": "",
            "row_class": "broken",
            "slave_state": "broken",
            "starttime": "2014-06-05 08:01:26"
        },
        "try-linux64-ec2-004": {
            "elapsed_on_job": "1:48:44",
            "elapsed_since_job": "42 days, 13:13:55",
            "elapsed_since_job_secs": 3676435,
            "enabled": "Yes",
            "master": "<a href=\"http://buildbot-master76.srv.releng.use1.mozilla.com:8101/buildslaves/try-linux64-ec2-004\">bm76-try1</a>",
            "notes": "",
            "row_class": "broken",
            "slave_state": "broken",
            "starttime": "2014-08-13 17:37:27"
        },
        "try-linux64-ec2-005": {
            "elapsed_on_job": "0:42:21",
            "elapsed_since_job": "112 days, 20:11:58",
            "elapsed_since_job_secs": 9749518,
            "enabled": "Yes",
            "master": "<a href=\"http://buildbot-master76.srv.releng.use1.mozilla.com:8101/buildslaves/try-linux64-ec2-005\">bm76-try1</a>",
            "notes": "",
            "row_class": "broken",
            "slave_state": "broken",
            "starttime": "2014-06-04 11:45:47"
        },
        "try-linux64-ec2-006": {
            "elapsed_on_job": "0:28:14",
            "elapsed_since_job": "112 days, 1:03:33",
            "elapsed_since_job_secs": 9680613,
            "enabled": "Yes",
            "master": "<a href=\"http://buildbot-master76.srv.releng.use1.mozilla.com:8101/buildslaves/try-linux64-ec2-006\">bm76-try1</a>",
            "notes": "",
            "row_class": "broken",
            "slave_state": "broken",
            "starttime": "2014-06-05 07:08:19"
        },
        "try-linux64-ec2-007": {
            "elapsed_on_job": "1:24:50",
            "elapsed_since_job": "112 days, 18:57:32",
            "elapsed_since_job_secs": 9745052,
            "enabled": "Yes",
            "master": "<a href=\"http://buildbot-master75.srv.releng.use1.mozilla.com:8101/buildslaves/try-linux64-ec2-007\">bm75-try1</a>",
            "notes": "",
            "row_class": "broken",
            "slave_state": "broken",
            "starttime": "2014-06-04 12:17:44"
        },
        "try-linux64-ec2-008": {
            "elapsed_on_job": "1:21:57",
            "elapsed_since_job": "112 days, 0:09:50",
            "elapsed_since_job_secs": 9677390,
            "enabled": "Yes",
            "master": "<a href=\"http://buildbot-master75.srv.releng.use1.mozilla.com:8101/buildslaves/try-linux64-ec2-008\">bm75-try1</a>",
            "notes": "",
            "row_class": "broken",
            "slave_state": "broken",
            "starttime": "2014-06-05 07:08:19"
        },
        "try-linux64-ec2-009": {
            "elapsed_on_job": "0:45:41",
            "elapsed_since_job": "112 days, 0:47:10",
            "elapsed_since_job_secs": 9679630,
            "enabled": "Yes",
            "master": "<a href=\"http://buildbot-master76.srv.releng.use1.mozilla.com:8101/buildslaves/try-linux64-ec2-009\">bm76-try1</a>",
            "notes": "",
            "row_class": "broken",
            "slave_state": "broken",
            "starttime": "2014-06-05 07:07:15"
        },
        "try-linux64-ec2-010": {
            "elapsed_on_job": "1:34:46",
            "elapsed_since_job": "111 days, 23:56:55",
            "elapsed_since_job_secs": 9676615,
            "enabled": "Yes",
            "master": "<a href=\"http://buildbot-master75.srv.releng.use1.mozilla.com:8101/buildslaves/try-linux64-ec2-010\">bm75-try1</a>",
            "notes": "",
            "row_class": "broken",
            "slave_state": "broken",
            "starttime": "2014-06-05 07:08:25"
        },
        "try-linux64-ec2-011": {
            "elapsed_on_job": "0:58:54",
            "elapsed_since_job": "111 days, 23:33:50",
            "elapsed_since_job_secs": 9675230,
            "enabled": "Yes",
            "master": "<a href=\"http://buildbot-master76.srv.releng.use1.mozilla.com:8101/buildslaves/try-linux64-ec2-011\">bm76-try1</a>",
            "notes": "",
            "row_class": "broken",
            "slave_state": "broken",
            "starttime": "2014-06-05 08:07:22"
        },
        "try-linux64-ec2-012": {
            "elapsed_on_job": "1:35:22",
            "elapsed_since_job": "111 days, 23:56:16",
            "elapsed_since_job_secs": 9676576,
            "enabled": "Yes",
            "master": "<a href=\"http://buildbot-master75.srv.releng.use1.mozilla.com:8101/buildslaves/try-linux64-ec2-012\">bm75-try1</a>",
            "notes": "",
            "row_class": "broken",
            "slave_state": "broken",
            "starttime": "2014-06-05 07:08:28"
        },
        "try-linux64-ec2-013": {
            "elapsed_on_job": "0:30:59",
            "elapsed_since_job": "112 days, 1:00:42",
            "elapsed_since_job_secs": 9680442,
            "enabled": "Yes",
            "master": "<a href=\"http://buildbot-master76.srv.releng.use1.mozilla.com:8101/buildslaves/try-linux64-ec2-013\">bm76-try1</a>",
            "notes": "",
            "row_class": "broken",
            "slave_state": "broken",
            "starttime": "2014-06-05 07:08:25"
        },
        "try-linux64-ec2-014": {
            "elapsed_on_job": "1:34:57",
            "elapsed_since_job": "111 days, 23:57:02",
            "elapsed_since_job_secs": 9676622,
            "enabled": "Yes",
            "master": "<a href=\"http://buildbot-master75.srv.releng.use1.mozilla.com:8101/buildslaves/try-linux64-ec2-014\">bm75-try1</a>",
            "notes": "",
            "row_class": "broken",
            "slave_state": "broken",
            "starttime": "2014-06-05 07:08:07"
        },
        "try-linux64-ec2-015": {
            "elapsed_on_job": "2:28:46",
            "elapsed_since_job": "111 days, 22:29:50",
            "elapsed_since_job_secs": 9671390,
            "enabled": "Yes",
            "master": "<a href=\"http://buildbot-master75.srv.releng.use1.mozilla.com:8101/buildslaves/try-linux64-ec2-015\">bm75-try1</a>",
            "notes": "",
            "row_class": "broken",
            "slave_state": "broken",
            "starttime": "2014-06-05 07:41:30"
        },
        "try-linux64-ec2-016": {
            "elapsed_on_job": "1:18:22",
            "elapsed_since_job": "112 days, 0:13:14",
            "elapsed_since_job_secs": 9677594,
            "enabled": "Yes",
            "master": "<a href=\"http://buildbot-master75.srv.releng.use1.mozilla.com:8101/buildslaves/try-linux64-ec2-016\">bm75-try1</a>",
            "notes": "",
            "row_class": "broken",
            "slave_state": "broken",
            "starttime": "2014-06-05 07:08:30"
        },
        "try-linux64-ec2-017": {
            "elapsed_on_job": "1:23:00",
            "elapsed_since_job": "111 days, 19:54:43",
            "elapsed_since_job_secs": 9662083,
            "enabled": "Yes",
            "master": "<a href=\"http://buildbot-master75.srv.releng.use1.mozilla.com:8101/buildslaves/try-linux64-ec2-017\">bm75-try1</a>",
            "notes": "",
            "row_class": "broken",
            "slave_state": "broken",
            "starttime": "2014-06-05 11:22:23"
        },
        "try-linux64-ec2-018": {
            "elapsed_on_job": "0:28:19",
            "elapsed_since_job": "112 days, 19:04:14",
            "elapsed_since_job_secs": 9745454,
            "enabled": "Yes",
            "master": "<a href=\"http://buildbot-master75.srv.releng.use1.mozilla.com:8101/buildslaves/try-linux64-ec2-018\">bm75-try1</a>",
            "notes": "",
            "row_class": "broken",
            "slave_state": "broken",
            "starttime": "2014-06-04 13:07:33"
        },
        "try-linux64-ec2-019": {
            "elapsed_on_job": "0:25:50",
            "elapsed_since_job": "111 days, 20:21:08",
            "elapsed_since_job_secs": 9663668,
            "enabled": "Yes",
            "master": "<a href=\"http://buildbot-master76.srv.releng.use1.mozilla.com:8101/buildslaves/try-linux64-ec2-019\">bm76-try1</a>",
            "notes": "",
            "row_class": "broken",
            "slave_state": "broken",
            "starttime": "2014-06-05 11:53:08"
        },
        "try-linux64-ec2-301": {
            "elapsed_on_job": "0:48:50",
            "elapsed_since_job": "112 days, 16:12:32",
            "elapsed_since_job_secs": 9735152,
            "enabled": "Yes",
            "master": "<a href=\"http://buildbot-master79.srv.releng.usw2.mozilla.com:8101/buildslaves/try-linux64-ec2-301\">bm79-try1</a>",
            "notes": "",
            "row_class": "broken",
            "slave_state": "broken",
            "starttime": "2014-06-04 15:38:44"
        },
        "try-linux64-ec2-302": {
            "elapsed_on_job": "0:37:51",
            "elapsed_since_job": "215 days, 21:06:25",
            "elapsed_since_job_secs": 18651985,
            "enabled": "Yes",
            "master": "<a href=\"http://None:None/buildslaves/try-linux64-ec2-302\">None</a>",
            "notes": "",
            "row_class": "broken",
            "slave_state": "broken",
            "starttime": "2014-02-21 10:55:50"
        },
        "try-linux64-ec2-303": {
            "elapsed_on_job": "0:49:05",
            "elapsed_since_job": "215 days, 21:06:35",
            "elapsed_since_job_secs": 18651995,
            "enabled": "Yes",
            "master": "<a href=\"http://None:None/buildslaves/try-linux64-ec2-303\">None</a>",
            "notes": "",
            "row_class": "broken",
            "slave_state": "broken",
            "starttime": "2014-02-21 10:44:26"
        },
        "try-linux64-ec2-304": {
            "elapsed_on_job": "0:39:25",
            "elapsed_since_job": "215 days, 19:51:33",
            "elapsed_since_job_secs": 18647493,
            "enabled": "Yes",
            "master": "<a href=\"http://None:None/buildslaves/try-linux64-ec2-304\">None</a>",
            "notes": "",
            "row_class": "broken",
            "slave_state": "broken",
            "starttime": "2014-02-21 12:09:08"
        },
        "try-linux64-ec2-305": {
            "elapsed_on_job": "1:59:31",
            "elapsed_since_job": "215 days, 21:17:42",
            "elapsed_since_job_secs": 18652662,
            "enabled": "Yes",
            "master": "<a href=\"http://None:None/buildslaves/try-linux64-ec2-305\">None</a>",
            "notes": "",
            "row_class": "broken",
            "slave_state": "broken",
            "starttime": "2014-02-21 09:22:53"
        },
        "try-linux64-ec2-306": {
            "elapsed_on_job": "2:52:10",
            "elapsed_since_job": "215 days, 22:18:04",
            "elapsed_since_job_secs": 18656284,
            "enabled": "Yes",
            "master": "<a href=\"http://None:None/buildslaves/try-linux64-ec2-306\">None</a>",
            "notes": "",
            "row_class": "broken",
            "slave_state": "broken",
            "starttime": "2014-02-21 07:29:52"
        },
        "try-linux64-ec2-307": {
            "elapsed_on_job": "1:25:13",
            "elapsed_since_job": "216 days, 11:37:35",
            "elapsed_since_job_secs": 18704255,
            "enabled": "Yes",
            "master": "<a href=\"http://None:None/buildslaves/try-linux64-ec2-307\">None</a>",
            "notes": "",
            "row_class": "broken",
            "slave_state": "broken",
            "starttime": "2014-02-20 19:37:18"
        },
        "try-linux64-ec2-308": {
            "elapsed_on_job": "1:32:48",
            "elapsed_since_job": "112 days, 19:04:26",
            "elapsed_since_job_secs": 9745466,
            "enabled": "Yes",
            "master": "<a href=\"http://buildbot-master78.srv.releng.usw2.mozilla.com:8101/buildslaves/try-linux64-ec2-308\">bm78-try1</a>",
            "notes": "",
            "row_class": "broken",
            "slave_state": "broken",
            "starttime": "2014-06-04 12:02:52"
        },
        "try-linux64-ec2-309": {
            "elapsed_on_job": "0:21:33",
            "elapsed_since_job": "215 days, 22:44:13",
            "elapsed_since_job_secs": 18657853,
            "enabled": "Yes",
            "master": "<a href=\"http://None:None/buildslaves/try-linux64-ec2-309\">None</a>",
            "notes": "",
            "row_class": "broken",
            "slave_state": "broken",
            "starttime": "2014-02-21 09:34:20"
        },
        "try-linux64-ec2-310": {
            "elapsed_on_job": "1:26:32",
            "elapsed_since_job": "112 days, 19:10:40",
            "elapsed_since_job_secs": 9745840,
            "enabled": "Yes",
            "master": "<a href=\"http://buildbot-master78.srv.releng.usw2.mozilla.com:8101/buildslaves/try-linux64-ec2-310\">bm78-try1</a>",
            "notes": "",
            "row_class": "broken",
            "slave_state": "broken",
            "starttime": "2014-06-04 12:02:54"
        },
        "try-linux64-ec2-311": {
            "elapsed_on_job": "2:25:39",
            "elapsed_since_job": "215 days, 22:59:51",
            "elapsed_since_job_secs": 18658791,
            "enabled": "Yes",
            "master": "<a href=\"http://None:None/buildslaves/try-linux64-ec2-311\">None</a>",
            "notes": "",
            "row_class": "broken",
            "slave_state": "broken",
            "starttime": "2014-02-21 07:14:36"
        },
        "try-linux64-ec2-312": {
            "elapsed_on_job": "0:26:23",
            "elapsed_since_job": "112 days, 16:55:03",
            "elapsed_since_job_secs": 9737703,
            "enabled": "Yes",
            "master": "<a href=\"http://buildbot-master78.srv.releng.usw2.mozilla.com:8101/buildslaves/try-linux64-ec2-312\">bm78-try1</a>",
            "notes": "",
            "row_class": "broken",
            "slave_state": "broken",
            "starttime": "2014-06-04 15:18:40"
        },
        "try-linux64-ec2-313": {
            "elapsed_on_job": "0:06:05",
            "elapsed_since_job": "215 days, 21:15:13",
            "elapsed_since_job_secs": 18652513,
            "enabled": "Yes",
            "master": "<a href=\"http://None:None/buildslaves/try-linux64-ec2-313\">None</a>",
            "notes": "",
            "row_class": "broken",
            "slave_state": "broken",
            "starttime": "2014-02-21 11:18:48"
        },
        "try-linux64-ec2-314": {
            "elapsed_on_job": "0:40:45",
            "elapsed_since_job": "215 days, 21:06:14",
            "elapsed_since_job_secs": 18651974,
            "enabled": "Yes",
            "master": "<a href=\"http://None:None/buildslaves/try-linux64-ec2-314\">None</a>",
            "notes": "",
            "row_class": "broken",
            "slave_state": "broken",
            "starttime": "2014-02-21 10:53:07"
        },
        "try-linux64-ec2-315": {
            "elapsed_on_job": "0:49:37",
            "elapsed_since_job": "216 days, 2:04:20",
            "elapsed_since_job_secs": 18669860,
            "enabled": "Yes",
            "master": "<a href=\"http://None:None/buildslaves/try-linux64-ec2-315\">None</a>",
            "notes": "",
            "row_class": "broken",
            "slave_state": "broken",
            "starttime": "2014-02-21 05:46:09"
        },
        "try-linux64-ec2-316": {
            "elapsed_on_job": "0:35:13",
            "elapsed_since_job": "215 days, 22:48:59",
            "elapsed_since_job_secs": 18658139,
            "enabled": "Yes",
            "master": "<a href=\"http://None:None/buildslaves/try-linux64-ec2-316\">None</a>",
            "notes": "",
            "row_class": "broken",
            "slave_state": "broken",
            "starttime": "2014-02-21 09:15:54"
        },
        "try-linux64-ec2-317": {
            "elapsed_on_job": "0:23:02",
            "elapsed_since_job": "112 days, 16:58:24",
            "elapsed_since_job_secs": 9737904,
            "enabled": "Yes",
            "master": "<a href=\"http://buildbot-master78.srv.releng.usw2.mozilla.com:8101/buildslaves/try-linux64-ec2-317\">bm78-try1</a>",
            "notes": "",
            "row_class": "broken",
            "slave_state": "broken",
            "starttime": "2014-06-04 15:18:40"
        },
        "try-linux64-ec2-318": {
            "elapsed_on_job": "0:33:39",
            "elapsed_since_job": "215 days, 22:41:32",
            "elapsed_since_job_secs": 18657692,
            "enabled": "Yes",
            "master": "<a href=\"http://None:None/buildslaves/try-linux64-ec2-318\">None</a>",
            "notes": "",
            "row_class": "broken",
            "slave_state": "broken",
            "starttime": "2014-02-21 09:24:55"
        },
        "try-linux64-ec2-319": {
            "elapsed_on_job": "0:19:46",
            "elapsed_since_job": "215 days, 22:55:28",
            "elapsed_since_job_secs": 18658528,
            "enabled": "Yes",
            "master": "<a href=\"http://None:None/buildslaves/try-linux64-ec2-319\">None</a>",
            "notes": "",
            "row_class": "broken",
            "slave_state": "broken",
            "starttime": "2014-02-21 09:24:52"
        }
    }



def get_slaves_build(slave_type):
    return {
        "bld-linux64-spot-002": {
            "elapsed_on_job": "0:32:33",
            "elapsed_since_job": "3:22:07",
            "elapsed_since_job_secs": 12127,
            "enabled": "Yes",
            "master": "<a href=\"http://buildbot-master70.srv.releng.use1.mozilla.com:8001/buildslaves/bld-linux64-spot-002\">bm70-build1</a>",
            "notes": "",
            "row_class": "working",
            "slave_class": "build",
            "slave_state": "working",
            "starttime": "2015-01-26 18:54:51"
        },
    }




def get_slaves_test(slave_type):
    return {
        "t-snow-r4-0001": {
            "elapsed_on_job": "0:04:42",
            "elapsed_since_job": "0:07:08",
            "elapsed_since_job_secs": 428,
            "enabled": "Yes",
            "master": "<a href=\"http://buildbot-master107.srv.releng.scl3.mozilla.com:8201/buildslaves/t-snow-r4-0001\">bm107-tests1-macosx</a>",
            "notes": "",
            "row_class": "working",
            "slave_class": "test",
            "slave_state": "working",
            "starttime": "2015-01-26 22:37:41"
        },
    }



def get_masters():
    return {
        "bm85-build1": "buildbot-master85.srv.releng.scl3.mozilla.com:8001",
        "bm86-build1": "buildbot-master86.srv.releng.scl3.mozilla.com:8001",
        "bm87-try1": "buildbot-master87.srv.releng.scl3.mozilla.com:8101",
        "bm91-build1": "buildbot-master91.srv.releng.usw2.mozilla.com:8001",
        "bm94-build1": "buildbot-master94.srv.releng.use1.mozilla.com:8001"
    }




#def get_special_slave():
#    return {
#        "bitsid": 2,
#        "envid": 5,
#        "speedid": 8,
#        "custom_tplid": null,
#        "enabled": false,
#        "distroid": 12,
#        "basedir": "/builds/slave/",
#        "dcid": 10,
##        "locked_masterid": null,
#        "purposeid": 5,
##        "current_masterid": null,
#        "notes": "Bug 666 - Does this slave actually exist?",
#        "poolid": 24,
#        "trustid": 5,
#        "slaveid": 1,
#        "name": "fake-slave-001"
#   }


def get_slave_state():
    return {
        "build": {
            "b-linux64-hp": {
                "broken": 0,
                "decommissioned": 14,
                "disabled": 1,
                "hung": 0,
                "not_in_slavealloc": 0,
                "pending_builds": 0,
                "slow": 0,
                "staging": 0,
                "working": 0
            },
            "b-linux64-ix": {
                "broken": 0,
                "decommissioned": 11,
                "disabled": 0,
                "hung": 0,
                "not_in_slavealloc": 0,
                "pending_builds": 0,
                "slow": 0,
                "staging": 0,
                "working": 0
            },
            "bld-linux64-ec2": {
                "broken": 38,
                "decommissioned": 0,
                "disabled": 0,
                "hung": 0,
                "not_in_slavealloc": 60,
                "pending_builds": 0,
                "slow": 0,
                "staging": 0,
                "working": 0
            },
            "bld-linux64-spot": {
                "broken": 306,
                "decommissioned": 0,
                "disabled": 0,
                "hung": 0,
                "not_in_slavealloc": 1,
                "pending_builds": 0,
                "slow": 0,
                "staging": 0,
                "working": 349
            },
            "bld-lion-r5": {
                "broken": 0,
                "decommissioned": 0,
                "disabled": 3,
                "hung": 0,
                "not_in_slavealloc": 8,
                "pending_builds": 0,
                "slow": 0,
                "staging": 1,
                "working": 55
            }
        },
        "metadata": {
            "generated": "2015-01-27T06:49:31.046908Z"
        },
        "test": {
            "t-snow-r4": {
                "broken": 0,
                "decommissioned": 2,
                "disabled": 2,
                "hung": 0,
                "not_in_slavealloc": 1,
                "pending_builds": 0,
                "slow": 0,
                "staging": 1,
                "working": 152
            },
            "t-w732-ix": {
                "broken": 0,
                "decommissioned": 0,
                "disabled": 0,
                "hung": 0,
                "not_in_slavealloc": 0,
                "pending_builds": 0,
                "slow": 0,
                "staging": 2,
                "working": 159
            },
            "t-w864-ix": {
                "broken": 1,
                "decommissioned": 0,
                "disabled": 3,
                "hung": 0,
                "not_in_slavealloc": 0,
                "pending_builds": 0,
                "slow": 0,
                "staging": 0,
                "working": 166
            },
            "t-xp32-ix": {
                "broken": 2,
                "decommissioned": 0,
                "disabled": 1,
                "hung": 0,
                "not_in_slavealloc": 0,
                "pending_builds": 0,
                "slow": 0,
                "staging": 0,
                "working": 158
            },
            "talos-linux64-ix": {
                "broken": 29,
                "decommissioned": 0,
                "disabled": 4,
                "hung": 0,
                "not_in_slavealloc": 0,
                "pending_builds": 0,
                "slow": 0,
                "staging": 0,
                "working": 86
            },
            "tst-emulator64-ec2": {
                "broken": 0,
                "decommissioned": 0,
                "disabled": 2,
                "hung": 0,
                "not_in_slavealloc": 17,
                "pending_builds": 0,
                "slow": 0,
                "staging": 0,
                "working": 0
            },
            "tst-emulator64-spot": {
                "broken": 54,
                "decommissioned": 0,
                "disabled": 0,
                "hung": 0,
                "not_in_slavealloc": 0,
                "pending_builds": 0,
                "slow": 0,
                "staging": 0,
                "working": 344
            },
            "tst-linux32-spot": {
                "broken": 302,
                "decommissioned": 0,
                "disabled": 0,
                "hung": 0,
                "not_in_slavealloc": 0,
                "pending_builds": 0,
                "slow": 0,
                "staging": 0,
                "working": 597
            },
            "tst-linux64-spot": {
                "broken": 7,
                "decommissioned": 0,
                "disabled": 0,
                "hung": 0,
                "not_in_slavealloc": 0,
                "pending_builds": 0,
                "slow": 0,
                "staging": 0,
                "working": 1292
            }
        },
        "try": {
            "b-linux64-hp": {
                "broken": 0,
                "decommissioned": 18,
                "disabled": 1,
                "hung": 0,
                "not_in_slavealloc": 0,
                "pending_builds": 0,
                "slow": 0,
                "staging": 0,
                "working": 0
            },
            "b-linux64-ix": {
                "broken": 0,
                "decommissioned": 2,
                "disabled": 0,
                "hung": 0,
                "not_in_slavealloc": 0,
                "pending_builds": 0,
                "slow": 0,
                "staging": 0,
                "working": 0
            },
            "bld-lion-r5": {
                "broken": 0,
                "decommissioned": 0,
                "disabled": 1,
                "hung": 0,
                "not_in_slavealloc": 0,
                "pending_builds": 0,
                "slow": 0,
                "staging": 0,
                "working": 20
            },
            "try-linux64-spot": {
                "broken": 204,
                "decommissioned": 0,
                "disabled": 0,
                "hung": 0,
                "not_in_slavealloc": 0,
                "pending_builds": 0,
                "slow": 0,
                "staging": 0,
                "working": 295
            }
        }
    }


def get_pendings():
    return {
        "pending": {
            "b2g-inbound": {
                "84df30ea5121": [
                    {
                        "submitted_at": 1415397048,
                        "id": 54657412,
                        "buildername": "b2g_macosx64 b2g-inbound opt test gaia-ui-test-functional-1"
                    },
                    {
                        "submitted_at": 1415397048,
                        "id": 54657413,
                        "buildername": "b2g_macosx64 b2g-inbound opt test gaia-ui-test-functional-2"
                    },
                    {
                        "submitted_at": 1415397048,
                        "id": 54657414,
                        "buildername": "b2g_macosx64 b2g-inbound opt test gaia-ui-test-functional-3"
                    },
                    {
                        "submitted_at": 1415397048,
                        "id": 54657415,
                        "buildername": "b2g_macosx64 b2g-inbound opt test gaia-ui-test-unit"
                    },
                    {
                        "submitted_at": 1415397048,
                        "id": 54657416,
                        "buildername": "b2g_macosx64 b2g-inbound opt test gaia-ui-test-accessibility"
                    }
                ],
                "cdbaa127d3b2": [
                    {
                        "submitted_at": 1415397166,
                        "id": 54657577,
                        "buildername": "Windows 7 32-bit b2g-inbound opt test mochitest-1"
                    },
                    {
                        "submitted_at": 1415397166,
                        "id": 54657578,
                        "buildername": "Windows 7 32-bit b2g-inbound opt test mochitest-2"
                    }
                ]
            },
            "pine": {
                "7e8d8042cf15": [
                    {
                        "submitted_at": 1415392210,
                        "id": 54649542,
                        "buildername": "b2g_pine_emulator_nonunified"
                    }
                ]
            }
        }
    }
