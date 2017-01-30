var template_base_link = "https://bugzilla.mozilla.org/enter_bug.cgi?assigned_to=nobody@mozilla.org&bug_severity=normal&bug_status=NEW&component=Buildduty&form_name=enter_bug&priority=P3&product=Release%20Engineering&status_whiteboard=[buildduty][buildslaves][capacity]";

var b2008_build_re   = /b-2008-|y-2008-/;
var lion_build_re    = /lion-r5/;
var linux64_build_re = /linux64/;

var linux_test_re    = /linux32/;
var linux64_test_re  = /linux64/;
var snow_test_re     = /snow/;
var yosemite_test_re = /yosemite/;
var w7_test_re       = /w732/;
var w864_test_re     = /w864/;
var w1064_test_re    = /w1064/;
var xp_test_re       = /xp32/;

var known_bugs = {};
var images = [];

var BugRe = /(bug\#*\ *)(\d+)/ig;
BugRe.compile(BugRe);

function getTemplateLinkForSlavename(slavename) {
    var platform = "";
    var opsys = "";
    var switcharg = true;
    switch (switcharg) {
    case w7_test_re.test(slavename):
        platform = 'x86';
        opsys = 'Windows%207';
        break;
    case xp_test_re.test(slavename):
        platform = 'x86';
        opsys = 'Windows%20XP';
        break;
    case snow_test_re.test(slavename):
        platform = 'x86';
        opsys = 'Mac%20OS%20X';
        break;
    case lion_build_re.test(slavename):
    case yosemite_test_re.test(slavename):
        platform = 'x86_64';
        opsys = 'Mac%20OS%20X';
        break;
    case linux_test_re.test(slavename):
        platform = 'x86';
        opsys = 'Linux';
        break;
    case linux64_build_re.test(slavename):
    case linux64_test_re.test(slavename):
        platform = 'x86_64';
        opsys = 'Linux';
        break;
    case b2008_build_re.test(slavename):
        platform = 'x86_64';
        opsys = 'Windows%20Server%202008';
        break;
    case w864_test_re.test(slavename):
        platform = 'x86_64';
        opsys = 'Windows%208';
        break;
    case w1064_test_re.test(slavename):
        platform = 'x86_64';
        opsys = 'Windows%2010';
        break;
    default:
        return "";
    }
    var template_link = template_base_link;
    template_link += '&short_desc=' + slavename + '%20problem%20tracking';
    template_link += '&alias=' + slavename;
    template_link += '&rep_platform=' + platform;
    template_link += '&op_sys=' + opsys;
    return template_link;
}

function handleResponse(response, slavename) {
    var output = "";
    var json = JSON.parse(response);
    var bugs = json.bugs;

    var em = document.getElementById(slavename);
    var bugzilla_url = "";
    var bug_icon = "";
    var bug_exists = "";
    var bug_status = "";
    if (bugs && bugs[0]) {
        var i;
        for (i = 0; i < bugs.length; i++) {
            output += bugs[i].id + ": " + bugs[i].summary + "\n";
        }
        bugzilla_url = 'https://bugzil.la/' + bugs[0].id;
        bug_status = bugs[0].status;
        if (bugs[0].status === 'NEW') {
            bug_icon += '<img alt="Existing bug, status=NEW" title="Existing bug, status=NEW" src="./icons/bug.png"/>';
        } else if (bugs[0].status === 'REOPENED') {
            bug_icon += '<img alt="Existing bug, status=REOPENED" title="Existing bug, status=REOPENED" src="./icons/bug_error.png"/>';
        } else if (bugs[0].status === 'RESOLVED') {
            bug_icon += '<img alt="Existing bug, status=' + bugs[0].resolution + '" title="Existing bug, status=' + bugs[0].resolution + '" src="./icons/bug_delete.png"/>';
            bug_status += " " + bugs[0].resolution;
        }
        bug_exists = "Existing bug";
    } else {
        bugzilla_url = getTemplateLinkForSlavename(slavename);
        bug_icon += '<img alt="File a new bug" title="File a new bug" src="./icons/bug_add.png" />';
        bug_exists = "File a new bug";
        bug_status = "NOT FOUND";
    }
    em.innerHTML = '<a target="_blank" href="' + bugzilla_url + '">' + bug_icon + '</a>';
    $('div#bugexists').html(bug_exists);
    $('div#bugstatus').html("Status: <span class='" + bug_status + "'>" + bug_status + "</span>");
}

function progressListener() {
    if (this.readyState === 4 && (this.status === 200 || this.status === 400)) {
        handleResponse(this.responseText, this.slavename);
    }
}

function getBugByAlias(bugAlias) {
    var em = document.getElementById(bugAlias);
    em.innerHTML = '<img alt="Looking up bug..." title="Looking up bug..." src="./icons/loading.png" />';

    var apiURL = "https://bugzilla.mozilla.org/rest/bug/" + bugAlias;

    var client = new XMLHttpRequest();
    client.onreadystatechange = progressListener;
    client.slavename = bugAlias;
    client.open("GET", apiURL);
    client.setRequestHeader('Accept',       'application/json');
    client.setRequestHeader('Content-Type', 'application/json');
    client.send();
}

function markupBugs(notes) {
    return notes.replace(BugRe,
                         "<a target='_slave_health_bug' href='https://bugzil.la/$2'>$1$2</a>");
}

function preload() {
    var i;
    for (i = 0; i < preload.arguments.length; i++) {
        images[i] = new Image();
        images[i].src = preload.arguments[i];
    }
}

preload.apply(this, ["./icons/help.png",
                     "./icons/bug.png",
                     "./icons/bug_add.png",
                     "./icons/bug_delete.png",
                     "./icons/bug_error.png",
                     "./icons/loading.png"]
             );
