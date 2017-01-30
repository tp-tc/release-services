#!/usr/bin/env python
import argparse
import datetime
import os
import re
import requests
from operator import attrgetter

import logging
log = logging.getLogger(__name__)

dep_tracker = {}
sec_tracker = {}
no_deps = []
deps_open = []
deps_resolved = []
unknown = []

html_file='./slave_health/buildduty_report.html'
username = ''
password = ''

# Set whatever REST API options we want
options = {
    'product':          'Release Engineering',
    'component':        'Buildduty',
    'status':           ['UNCONFIRMED','NEW','ASSIGNED','REOPENED'],
    'email1':           'nobody@mozilla.org',
    'email1_assigned_to': 1,
    'include_fields':   '_default,attachments,depends_on',
}

loan_request_options = {
    'product':          'Release Engineering',
    'component':        'Loan Requests',
    'email1':           'nobody@mozilla.org',
    'email1_assigned_to': 1,
    'status':           ['UNCONFIRMED','NEW','ASSIGNED','REOPENED'],
}

def generateHTMLHeader():
    now = datetime.datetime.now()
    now_day = now.strftime("%B %d, %Y")
    now_precise = now.strftime("%c")
    header = """<!DOCTYPE html>
 <html>
  <head>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
    <title>Buildduty Report - %s</title>
    <link rel="stylesheet" media="screen,projection,tv" href="./css/responsive-bundle.352a81c95337.css" />
    <link rel="stylesheet" href="./jquery.tablesorter/themes/blue/style.css" type="text/css" media="print, projection, screen" />
    <link rel="stylesheet" href="./css/slave_health.css" type="text/css" media="print, projection, screen" />
    <script type="text/javascript" src="./jquery.tablesorter/jquery-1.6.4.min.js"></script>
    <script type="text/javascript" src="./jquery.tablesorter/jquery.tablesorter.js"></script>
    <script language="javaScript" type="text/javascript" src="./js/bugzilla.js"></script>
    <script language="javaScript" type="text/javascript" src="./js/slave_health.js"></script>
  </head>

  <body class="noscript">
    <div id="topbar">
      <div id="title" class="dropdown"><a href="./index.html">Slave Health</a></div>
      <div class="dropdown separator"> &gt; </div>
      <div id="builddutyreport" class="dropdown">Buildduty Report</div>
      <div class="topbarright">
        <div id="generated" class="dropdown">
          Data generated at: <span id="generated">%s</span>
        </div>
      </div>
    </div>

    <div class="container">
""" % (now_day, now_precise)
    return header

def generateInPageLinks(page_sections):
    links = " | ".join("<a href=\"#%s\">%s</a>" % (page_section['name'],
                                                   page_section['title']) for page_section in page_sections)
    return links

def generateBugTable(table_id, title, bugs, css_class=None, strike_deps=False, links=""):
    if not css_class:
        css_class="tablesorter"
    table = "<table id=\"{0}\" class=\"{1}\">\n".format(table_id, css_class)
    table += "<thead><tr><th class=\"bugid\">Bug&nbsp;ID</th><th class=\"summary\">Summary</th><th class=\"lastupdated\">Last Updated</th><th class=\"dependson\">Depends On</th></tr></thead>\n"

    if bugs:
        for bug in sorted(bugs, key=lambda a: a['last_change_time'], reverse=False):
            summary = re.sub(r'(.*) (problem tracking)$', r'<a target="_\1_slave_health" href="slave.html?name=\1">\1</a> \2', bug['summary'])
            last_change_time = re.sub('[A-Za-z]', ' ', bug['last_change_time'])
            table += "<tr><td><a href=\"https://bugzil.la/{0}\">Bug&nbsp;{0}</a></td><td class=\"summary\">{1}</td><td>{2}</td>\n".format(bug['id'], summary, last_change_time)
            table += "<td>"
            if not bug['depends_on']:
                table += "None"
            else:
                for dep_bug in bug['depends_on']:
                    strike_open = ''
                    strike_close = ''
                    if dep_bug in dep_tracker and dep_tracker[dep_bug] in ['RESOLVED', 'VERIFIED']:
                        strike_open = '<s>'
                        strike_close = '</s>'
                    elif dep_bug in sec_tracker:
                        strike_open = ''
                        strike_close = '<img class="inline" src="icons/lock.png" alt="Lock icon" title="Lock icon" />'
                    table += "{0}<a href=\"https://bugzil.la/{1}\">{1}</a>{2}, ".format(strike_open, dep_bug, strike_close)
                table = table[:-2]
            table += "</td>\n</tr>\n"
    else:
        table += "<tr><td class=\"notfound\" colspan=\"4\">No bugs found.</td></tr>"
    table += "</table>\n\n"
    table_header = "<strong>%s</strong> <a name =\"%s\" target=\"builddutybugzilla\" href=\"https://bugzilla.mozilla.org/buglist.cgi?bug_id=%s\"><img class=\"bugzilla\" src=\"icons/bugzilla.png\" alt=\"View list in Bugzilla\" title=\"View list in Bugzilla\" /></a>" % \
        (title, table_id, ','.join(str(bug['id']) for bug in bugs))
    if links != "":
        table_header += " | <small>%s</small>" % links
    table_header += "\n"

    return table_header + table

def generateHTMLFooter():
    footer = """
<script type="text/javascript">
$(document).ready(function(){
  generateReportsDropdown('buildduty');
  $(".dropdown").live("click", function dropdownClick(ev) {
    $(this).addClass("open");
  });
  $("html").bind("mousedown", function clickAnywhere(e) {
    // Close open dropdowns if the event's target is not inside
    // an open dropdown.
    if ($(e.target).parents(".dropdown.open").length == 0)
      $(".dropdown").removeClass("open");
  });
  // Empty tables can cause tablesorter failures, and cause future tables to not sort at all.
  // We try/catch here to not error out on the first empty table.
  try {
    $("#nodeps").tablesorter({sortList:[[2,1]], widgets: ["zebra"]});
  } catch(e) {
  }
  try {
    $("#depsresolved").tablesorter({sortList:[[2,1]], widgets: ["zebra"]});
  } catch(e) {
  }
  try {
    $("#depsopen").tablesorter({sortList:[[2,1]], widgets: ["zebra"]});
  } catch(e) {
  }
  try {
    $("#loanreqs").tablesorter({sortList:[[2,1]], widgets: ["zebra"]});
  } catch(e) {
  }
  $("td.summary").each(function() {
    var res = $(this).text().split(' ');
    if (res[1] == 'problem' && res[2] == 'tracking') {
      var slave_json = slavealloc_api_baseurl + "slaves/" + res[0] + "?byname=1";
      var summary = $(this);
      $.getJSON(slave_json, function(data){
        if (data["notes"] != "" && data["notes"] != null) {
           var marked_up_notes = markupBugs(data['notes']);
           summary.append('<span class="notes" title="slavealloc notes">' + marked_up_notes + '</span>');
        }
      });
    }
  });
});
</script>

    </div>

  </body>
</html>
"""
    return footer

def bug_query_to_object(URL):
    r = requests.get(URL)
    return r.json()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.set_defaults(log_level=logging.WARN,
                        output_dir="./logs",
                        logfile="buildduty_report.log",
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

    bug_list = bug_query_to_object('http://bugzilla.mozilla.org/rest/bug?status=UNCONFIRMED&status=NEW&status=ASSIGNED&status=REOPENED&product=Release%20Engineering&component=Buildduty&emailassigned_to1=1&email1=nobody%40mozilla.org&include_fields=id,summary,attachments,depends_on,last_change_time,status')

    for bug in bug_list['bugs']:
        if not bug['depends_on']:
            no_deps.append(bug)
            continue
        found_open_deps = False
        # Track the current bug in case others depend on it.
        dep_tracker[bug['id']] = bug['status']
        for dep_bug in bug['depends_on']:
            if not dep_bug in dep_tracker:
                bug_objects = bug_query_to_object('https://bugzilla.mozilla.org/rest/bug/%s' % dep_bug)
                if bug_objects:
                    if 'bugs' in bug_objects:
                        try:
                            dep_tracker[dep_bug] = bug_objects['bugs'][0]['status']
                        except:
                            # Something has gone wrong with the lookup, so assume it's still open.
                            dep_tracker[dep_bug] = 'UNKNOWN'
                            found_open_deps = True
                            continue
                    elif 'error' in bug_objects and 'You are not authorized' in bug_objects['message']:
                        # This bug is confidential, so we mark it as open since we don't know.
                        sec_tracker[dep_bug] = True
                        found_open_deps = True
                        continue
            if not dep_bug in dep_tracker or \
               dep_tracker[dep_bug] not in ['RESOLVED', 'VERIFIED']:
                # We only need to find one dep still open
                found_open_deps = True
        if found_open_deps:
            deps_open.append(bug)
        else:
            deps_resolved.append(bug)

    loan_requests = bug_query_to_object('https://bugzilla.mozilla.org/rest/bug?status=UNCONFIRMED&status=NEW&status=ASSIGNED&status=REOPENED&product=Release%20Engineering&component=Loan%20Requests&assigned_to=nobody@mozilla.org&include_fields=id,summary,attachments,depends_on,last_change_time,status')

    f = open(html_file, 'w')
    f.write(generateHTMLHeader())

    no_deps_desc = {'name': 'nodeps',
                    'title': 'No dependencies (likely new bugs)'}
    deps_resolved_desc = {'name': 'depsresolved',
                          'title': 'All dependencies resolved'}
    deps_open_desc = {'name': 'depsopen',
                      'title': 'Open dependencies'}
    loan_requests_desc = {'name': 'loanreqs',
                          'title': 'Loan requests (new)'}

    f.write(generateBugTable('loanreqs',
                             'Loan requests (new)',
                             loan_requests['bugs'],
                             strike_deps=True,
                             links=generateInPageLinks([no_deps_desc,
                                                        deps_open_desc,
                                                        deps_resolved_desc])
                             ) + '\n')
    f.write("\n<hr/>\n")
    f.write(generateBugTable('nodeps',
                             'No dependencies (likely new bugs)',
                             no_deps,
                             links=generateInPageLinks([deps_resolved_desc,
                                                        deps_open_desc,
                                                        loan_requests_desc])
                             ) + '\n')
    f.write("\n<hr/>\n")
    f.write(generateBugTable('depsresolved',
                             'All dependencies resolved',
                             deps_resolved,
                             strike_deps=True,
                             links=generateInPageLinks([no_deps_desc,
                                                        deps_open_desc,
                                                        loan_requests_desc])
                             ) + '\n')
    f.write("\n<hr/>\n")
    f.write(generateBugTable('depsopen',
                             'Open dependencies',
                             deps_open,
                             strike_deps=True,
                             links=generateInPageLinks([no_deps_desc,
                                                        deps_resolved_desc,
                                                        loan_requests_desc])
                             ) + '\n')

    f.write(generateHTMLFooter())

    log.debug("Done processing.")
