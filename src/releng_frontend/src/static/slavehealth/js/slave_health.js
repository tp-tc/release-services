var local_test = false;
var slavetype_url = "./slavetype.html";
var slavealloc_api_baseurl = "https://secure.pub.build.mozilla.org/slavealloc/api/";
var buildapi_baseurl = "https://secure.pub.build.mozilla.org/buildapi/recent/";
var slaveapi_baseurl = "https://secure.pub.build.mozilla.org/slaveapi/slaves/";
var nagios_baseurl = "http://nagios1.private.releng.scl3.mozilla.com/releng-scl3/cgi-bin/";
var nagios_host_baseurl = nagios_baseurl + "extinfo.cgi?type=1&host=";
var nagios_history_baseurl = nagios_baseurl + "history.cgi?host=";
var slaveid;
var unknown_pending = {};

Date.prototype.stdTimezoneOffset = function () {
    var jan = new Date(this.getFullYear(), 0, 1);
    var jul = new Date(this.getFullYear(), 6, 1);
    return Math.max(jan.getTimezoneOffset(), jul.getTimezoneOffset());
};

Date.prototype.dst = function () {
    return this.getTimezoneOffset() < this.stdTimezoneOffset();
};

function getPTOffset() {
    // returns the offset in seconds to Pacific Time (PT)
    // relative to your current TZ, accounting for DST.
    var d = new Date();
    var PST_offset = 8;
    var PDT_offset = 7;
    var current_offset = PST_offset;
    if (d.dst()) {
        current_offset = PDT_offset;
    }
    var local_offset = d.getTimezoneOffset() / 60;
    return (current_offset - local_offset) * 3600;
}

function getPTDisplay() {
    // returns the Pacific Time (PT) timezone string
    // for display, accounting for DST.
    var d = new Date();
    if (d.dst()) {
        return "PDT";
    }
    return "PST";
}

function isPositiveInteger(str) {
    return /^[1-9]\d*$/.test(str);
}

function isAWSInstance(slavename) {
  if (slavename.indexOf('spot') >= 0 || slavename.indexOf('ec2') >= 0) {
      return true;
  }
   return false;
}

function getSlaveclassForPendingJob(pending) {
    if (pending.match(/(try[\w\-\ \.]*)(build|non-unified)/)) {
        return "try";
    } else if (pending.match(/(build|nightly|_dep|bundle|release-|l10n dep|fuzzer|valgrind|non-?unified|periodic)/)) {
        return "build";
    } else if (pending.match(/(test|talos|jetpack)/)) {
        return "test";
    }
    return "";
}

function getSlavetypeForPendingJob(slaveclass, pending) {
    var slavetype = "";
    // This makes matching Thunderbird builds/tests like everything else.
    pending = pending.replace(/^(TB )/,"");
    if (slaveclass === "try") {
        if (pending.match(/(OS X|macosx64)/)) {
            slavetype = "bld-lion-r5";
        } else if (pending.match(/(WINNT|win32|win64)/)) {
            slavetype = "y-2008-spot";
        } else {
            // Need to list the first row of the group in index.html
            slavetype = "try-linux64-spot";
        }
    } else if (slaveclass === "build") {
        if (pending.match(/(OS X|macosx64)/)) {
            slavetype = "bld-lion-r5";
        } else if (pending.match(/(WINNT|win32|win64|fuzzer-win64)/)) {
            slavetype = "b-2008-spot";
        } else {
            // Need to list the first row of the group in index.html
            slavetype = "bld-linux64-spot";
        }
    } else if (slaveclass === "test") {
        if (pending.match(/^Android/)) {
            if (pending.match(/^Android (?:4\.2 )?x86/)) {
                slavetype = "talos-linux64-ix";
            } else if (pending.match(/^Android 4.3 armv7 API 11\+ .+ test (plain-reftest|crashtest|jsreftest)/)) {
                slavetype = "tst-emulator64-spot";
            } else if (pending.match(/^Android 4.3 armv7 API 15\+ .+ test (plain-reftest|crashtest|jsreftest)/)) {
                slavetype = "tst-emulator64-spot";
            } else if (pending.match(/^Android armv7 API 9 .+ test (plain-reftest|crashtest|jsreftest)/)) {
                slavetype = "tst-emulator64-spot";
            } else if (pending.match(/^Android 2.3 (Armv6 )?Emulator .+ test (plain-reftest|crashtest|jsreftest)/)) {
                slavetype = "tst-emulator64-spot";
            } else if (pending.match(/^Android 4.3 armv7 API 11\+ .+ test (?!(plain-reftest|crashtest|jsreftest))/)) {
                slavetype = "tst-linux64-spot";
            } else if (pending.match(/^Android 4.3 armv7 API 15\+ .+ test (?!(plain-reftest|crashtest|jsreftest))/)) {
                slavetype = "tst-linux64-spot";
            } else if (pending.match(/^Android armv7 API 9 .+ test (?!(plain-reftest|crashtest|jsreftest))/)) {
                slavetype = "tst-linux64-spot";
            } else if (pending.match(/^Android 2.3 (Armv6 )?Emulator .+ test (?!(plain-reftest|crashtest|jsreftest))/)) {
                slavetype = "tst-linux64-spot";
            } else if (pending.match(/^Android 4.3 armv7 (API 11\+) .+ test ((plain-reftest|crashtest|jsreftest))/)) {
                slavetype = "tst-emulator64-spot";
            } else if (pending.match(/^Android 4.3 armv7 (API 15\+) .+ test ((plain-reftest|crashtest|jsreftest))/)) {
                slavetype = "tst-emulator64-spot";
            } else if (pending.match(/^Android 4.3 armv7 (API 11\+) .+ test (?!(plain-reftest|crashtest|jsreftest))/)) {
                slavetype = "tst-linux64-spot";
            } else if (pending.match(/^Android 4.3 armv7 (API 15\+) .+ test (?!(plain-reftest|crashtest|jsreftest))/)) {
                slavetype = "tst-linux64-spot";
            }
        } else if (pending.match(/^(Ubuntu VM 12.04 (?!x64).+|b2g_ubuntu32_vm|jetpack-.+-ubuntu32_vm)/)) {
            slavetype = "tst-linux32-spot";
        } else if (pending.match(/^(Ubuntu (ASAN |Code Coverage )?VM 12.04 x64 .+|b2g_ubuntu64_vm|b2g_emulator(-\S\S)?_vm|jetpack-.+-ubuntu64(-asan)?_vm)/)) {
            slavetype = "tst-linux64-spot";
	} else if (pending.match(/^Ubuntu (ASAN |Code Coverage )?VM large 12.04 x64 .+gtest$/)) {
            slavetype = "tst-emulator64-spot";
        } else if (pending.match(/^(WINNT 6\.2|Windows 8|jetpack-.+-win8)/)) {
            slavetype = "t-w864-ix";
        } else if (pending.match(/^(Windows 10|jetpack-.+-win10)/)) {
            slavetype = "t-w1064-ix";
        } else if (pending.match(/^Windows 7 VM-GFX/)) {
            slavetype = "g-w732-spot";
        } else if (pending.match(/^Windows 7 VM/)) {
            slavetype = "t-w732-spot";
        } else if (pending.match(/^(Windows 7|jetpack-.+-win7)/)) {
            slavetype = "t-w732-ix";
        } else if (pending.match(/^(Windows XP|jetpack-.+-xp)/)) {
            slavetype = "t-xp32-ix";
        } else if (pending.match(/^(Rev4 MacOSX Snow Leopard|jetpack-.+-snowleopard)/)) {
            slavetype = "t-snow-r4";
        } else if (pending.match(/(Rev7 MacOSX Yosemite 10.10.5|jetpack-.+-yosemite)/)) {
            slavetype = "t-yosemite-r7";
        } else if (pending.match(/^Ubuntu (ASAN )?HW 12.04 x64/)) {
            slavetype = "talos-linux64-ix";
        }
    }
    return slavetype;
}

function getSlavetypeByName(slavename) {
    if (slavename.match(/^tst-linux64-spot/)) {
        return "tst-linux64-spot";
    } else if (slavename.match(/^tst-emulator64-spot/)) {
        return "tst-emulator64-spot";
    } else if (slavename.match(/^bld-linux64-spot/)) {
        return "bld-linux64-spot";
    } else if (slavename.match(/^t-w732-spot/)) {
        return "t-w732-spot";
    } else if (slavename.match(/^bld-lion-r5/)) {
        return "bld-lion-r5";
    } else if (slavename.match(/^b-2008-spot/)) {
        return "b-2008-spot";
    } else if (slavename.match(/^y-2008-spot/)) {
        return "y-2008-spot";
    } else if (slavename.match(/^try-linux64-spot/)) {
        return "try-linux64-spot";
    } else if (slavename.match(/^t-w864-ix/)) {
        return "t-w864-ix";
    } else if (slavename.match(/^t-w1064-ix/)) {
        return "t-w1064-ix";
    } else if (slavename.match(/^g-w732-spot/)) {
        return "g-w732-spot";
    } else if (slavename.match(/^t-w732-ix/)) {
        return "t-w732-ix";
    } else if (slavename.match(/^t-xp32-ix/)) {
        return "t-xp32-ix";
    } else if (slavename.match(/^t-yosemite-r7/)) {
        return "t-yosemite-r7";
    } else if (slavename.match(/^talos-linux64-ix/)) {
        return "talos-linux64-ix";
    } else if (slavename.match(/^tst-linux32-spot/)) {
        return "tst-linux32-spot";
    }
    return "";
}

function getParameterByName(name) {
    name = name.replace(/[\[]/, "\\\[").replace(/[\]]/, "\\\]");
    var regex = new RegExp("[\\?&]" + name + "=([^&#]*)");
    var results = regex.exec(location.search);
    return results === null ? "" : $.encoder.encodeForURL(decodeURIComponent(results[1].replace(/\+/g, " ")));
}

function getSlaveclassFromSlavealloc(purposeid, trustid) {
    // Purposes: tests === 4, build === 5
    if (purposeid === 4) {
        return "test";
    }
    // Trust levels: try === 4
    if (trustid === 4) {
        return "try";
    }
    return "build";
}

function getLinkclassForResult(result) {
    var linkclass = "";
    switch (result) {
    case 0:
        linkclass = "success";
        break;
    case 1:
        linkclass = "warnings";
        break;
    case 2:
        linkclass = "failure";
        break;
    case 3:
        linkclass = "skipped";
        break;
    case 4:
        linkclass = "exception";
        break;
    case 5:
        linkclass = "retry";
        break;
    case 6:
        linkclass = "cancelled";
        break;
    }
    return linkclass;
}

function getLetterForResult(result) {
    var letter = "P";
    switch (result) {
    case 0:
        // Passed (success)
        letter = "P";
        break;
    case 1:
        // Working
        letter = "W";
        break;
    case 2:
        // Failed
        letter = "F";
        break;
    case 3:
        // Skipped
        letter = "S";
        break;
    case 4:
        // Exception
        letter = "E";
        break;
    case 5:
        // Retry
        letter = "R";
        break;
    case 6:
        // Cancelled
        letter = "C";
        break;
    }
    return letter;
}

function getDurationFromSeconds(seconds) {
    var hours = parseInt(seconds / 3600, 10) % 24;
    var minutes = parseInt(seconds / 60, 10) % 60;
    seconds = seconds % 60;

    return (hours < 10 ? "0" + hours : hours) + ":" + (minutes < 10 ? "0" + minutes : minutes) + ":" + (seconds  < 10 ? "0" + seconds : seconds);
}

function getDateFromSeconds(seconds) {
    var d = new Date(0);
    d.setUTCSeconds(seconds);
    return d;
}

function getEnabledStatusFromID(enabled) {
    var checkbox_string = "Enabled? <input id=\"slavealloc_enabled_checkbox\" type=\"checkbox\" disabled=\"disabled\"";
    if (enabled) {
        checkbox_string += " checked=\"checked\"";
    }
    checkbox_string += " />";
    return checkbox_string;
}

function getEnvironmentFromID(envid) {
    switch (envid) {
    case 2:
        return "Production";
    case 3:
        return "Development/Pre-production";
    case 5:
        return "Decommissioned";
    }
    return "Unknown environment";
}

function dateToYMD(date) {
    var d = date.getDate();
    var m = date.getMonth() + 1;
    var y = date.getFullYear();
    return String(y + '-' + (m <= 9 ? '0' + m : m) + '-' + (d <= 9 ? '0' + d : d));
}

function dateToYM(date) {
    var m = date.getMonth() + 1;
    var y = date.getFullYear();
    return String(y + '-' + (m <= 9 ? '0' + m : m));
}

function updateSlaveallocDiv(attrib, attrib_id, div_id, name) {
    var json_url = slavealloc_api_baseurl + attrib + '/' + attrib_id;
    $.getJSON(json_url, function (attrib_json) {
        $('div#' + div_id).html(attrib_json[name]);
    });
}

function updateSlavetypeStatus(slaveclass, slavetype, states) {
    var status_cell = 'table#' + slaveclass + ' tr#' + slavetype + ' td.status';
    var broken = states["broken"] || 0;
    var hung = states["hung"] || 0;
    var slow = states["slow"] || 0;
    var working = states["working"] || 0;
    var disabled = states["disabled"] || 0;
    var staging = states["staging"] || 0;
    var total = broken + hung + slow + working + disabled + staging || 0;
    var status_text = '<span class="total" title="Total">' + total + ':</span> ';
    if (slavetype.match(/(ec2|spot)/)) {
        status_text += '<span class="stopped" title="Stopped">' + (broken + hung + slow) + '</span> | ';
    } else {
        var pending_cell = 'table#' + slaveclass + ' tr#' + slavetype + ' td.pending';
        var pending_count = $(pending_cell).text();
        if (pending_count && pending_count > 0) {
	    status_text += '<span class="broken" title="Broken">' + (broken + hung + slow) + '</span> | ';
        } else {
            status_text += '<span class="idle" title="Idle">' + (broken + hung + slow) + '</span> | ';
        }
    }
    status_text += '<span class="working" title="Working">' + working + '</span> | ';
    status_text += '<span class="disabled" title="Disabled">' + disabled + '</span> | ';
    status_text += '<span class="staging" title="Staging">' + staging + '</span>';
    $(status_cell).html(status_text);
}

function incrementUnknownPending(buildername, slaveclass, slavetype) {
    $('div#unknown').css('display', 'inline-block');
    $('table#unknown tr#none').remove();
    var css_buildername = buildernameToCSSID(buildername);
    if ($('table#unknown tbody tr#' + css_buildername).length ) {
        var unknown_cell = 'tr#' + css_buildername + ' td#count';
        var unknown_count = $(unknown_cell).text();
        unknown_count++;
        $(unknown_cell).text(unknown_count);
    } else {
        $('table#unknown tr:last').after('<tr id=' + css_buildername + '><td>' + buildername + '</td><td>' + slaveclass + '</td><td>' + slavetype + '</td><td id="count">1</td></tr>');
    }
}

function updatePendingCount(buildername) {
    var slaveclass = getSlaveclassForPendingJob(buildername);
    if (slaveclass === "") {
	incrementUnknownPending(buildername, 'unknown', 'unknown');
        return;
    }
    var slavetype = getSlavetypeForPendingJob(slaveclass, buildername);
    if (slavetype === "") {
	incrementUnknownPending(buildername, slaveclass, 'unknown');
        return;
    }
    var pending_cell = 'table#' + slaveclass + ' tr#' + slavetype + ' td.pending';
    var pending_count = $(pending_cell).text();
    pending_count++;
    $(pending_cell).text(pending_count);
    // Change Idle to Broken if we have pending jobs for an HW slavetype
    if (! isAWSInstance(slavetype)) {
        var idle_cell = 'table#' + slaveclass + ' tr#' + slavetype + ' td.status span.idle';
	$(idle_cell).removeClass('idle').addClass('broken').attr('title','Broken');
    }
}

function buildernameToID(buildername) {
    // convert space to underscore
    var id_string = buildername.replace(/ /g, '_');
    // Strip out + characters
    id_string = id_string.replace(/\+/g, '');
    return id_string;
}

function buildernameToCSSID(buildername) {
    // reuse code
    var id_string = buildernameToID(buildername);
    // escape decimal
    id_string = id_string.replace(/\./g, '\\.');
    return id_string;
}

function createRowForSlave(slavetype, slavename, slavedata, params) {
    if (slavedata['elapsed_since_job'] === "0") {
        slavedata['elapsed_since_job'] = "0:00:00";
    }
    if (slavename.match(/-(ec2|spot)-/) && slavedata['row_class'] === "broken") {
        slavedata['row_class'] = "stopped";
    }
    var row_class = slavedata['row_class'];
    var newrow = $('<tr>').addClass(row_class);
    var slave_url = "<a href=\"./slave.html" + params + "&name=" + slavename + "\">" + slavename + '</a>';
    newrow.append($('<td>').html(slave_url + '&nbsp;<span id="' + slavename + '"><img src="./icons/help.png" alt="Check bug status" title="Check bug status" onclick="getBugByAlias(&quot;' + slavename + '&quot;);"></span>').addClass('slavename'));
    newrow.append($('<td>').addClass('elapsed').attr('seconds', slavedata['elapsed_since_job_secs']).text(slavedata['elapsed_since_job']));
    newrow.append($('<td class="state">').text(slavedata['row_class']));
    newrow.append($('<td>').html(slavedata['master']));
    newrow.append($('<td>').text(slavedata['starttime']));
    newrow.append($('<td>').text(slavedata['elapsed_on_job']));
    newrow.append($('<td>').html(slavedata['notes']));
    newrow.append($('<td class="enabled">').text(slavedata['enabled']));
    $('#lastbuild > tbody:last').append(newrow);
}

function createNotesInput() {
    var notes_value = "";
    if (notes != "No notes in slavealloc") {
        notes_value = notes;
    }
    var notes_input = "<input id=\"slavealloc_notes_update\" type=\"text\" class=\"fill\"  value=\"" + notes_value + "\">";
    $('div#slavealloc_notes').html(notes_input);
}

function updateStatus(selector, msg, status, fade_timer, disable_fade) {
    disable_fade = typeof disable_fade !== 'undefined' ? disable_fade : false;
    $(selector).stop();
    $(selector).text("");
    $(selector).css({ opacity: 1 });
    if (disable_fade) {
        $(selector).show().attr('class', status).text(msg);
    } else {
        var fade_delay = 5000;
        status = typeof status !== 'undefined' ? status : "success";
        if (typeof fade_timer !== 'undefined') {
            if (fade_timer > fade_delay) {
                fade_timer = fade_timer - fade_delay;
            } else {
                fade_timer = fade_delay;
                fade_delay = 0;
            }
        } else {
            fade_timer = 5000;
        }
        $(selector).show().attr('class', status).text(msg).delay(fade_delay).fadeOut(fade_timer);
    }
}

function submitSlaveallocEdits() {
    var slavealloc_update_url = slavealloc_api_baseurl + 'slaves/' + slaveid;
    updateStatus('div#slaveallocstatus', "Updating slavealloc...", "pending", 15000);
    var enabled = false;
    if ($('input#slavealloc_enabled_checkbox').is(':checked')) {
        enabled = true;
    }
    var updated_notes = $('input#slavealloc_notes_update').val().replace( /[\*\^\'\@\$\;\"]/g , '');
    disableButton('button#submitslavealloc');
    $.ajax({
        url: slavealloc_update_url,
        type: "PUT",
        data: JSON.stringify({ "enabled": enabled, "notes": updated_notes })
      })
        .fail(function (response) {
            updateStatus('div#slaveallocstatus', "Got failure " + response.status + ": " + response.responseText, "failure", 0, true);
        })
        .done(function (data) {
            updateStatus('div#slaveallocstatus', "Slavealloc updated successfully", "success", 15000);
        })
        .always(function() {
            $.getJSON(slave_json, function(slave){
                getSlavedata(slave, slaveclass, slavetype, params);
            });
        });
}

function disableButton(selector) {
    $(selector).unbind('click');
    $(selector).attr('disabled', 'disabled').addClass('disabled');
}

function enableSlaveallocSubmit() {
    disableButton('button#editslavealloc');
    $('input#slavealloc_enabled_checkbox').removeAttr('disabled').removeClass('disabled');
    createNotesInput();
    $('button#submitslavealloc').click(function () { submitSlaveallocEdits(); });
    $('button#submitslavealloc').removeAttr('disabled').removeClass('disabled');
}

function enableSlaveallocEdit() {
    disableButton('button#submitslavealloc');
    $('button#editslavealloc').click(function () { enableSlaveallocSubmit(); });
    $('button#editslavealloc').removeAttr('disabled').removeClass('disabled');
}

function getSlavedata(slave, slaveclass, slavetype, params) {
    notes = "No notes in slavealloc";
    slaveid = slave['slaveid']
    if (slaveid) {
        // If we succeed in looking up the slaveid, enable the edit toggle.
        enableSlaveallocEdit();
    }
    if (slave['current_masterid'] && slave['current_masterid'] !== null && slave['current_masterid'] !== '') {
        var master_json = slavealloc_api_baseurl + "masters/" + slave['current_masterid'];
        $.getJSON(master_json, function (master) {
            $('div#slavealloc_master').html("<a target=\"_blank\" href=\"http://" + master['fqdn'] + ":" + master['http_port'] + "/buildslaves/" + slave['name'] + "?numbuilds=0\">" + master['nickname'] + "</a>");
        });
    } else {
        $('div#slavealloc_master').html("Not attached");
    }
    if (slave['notes'] && slave['notes'] !== "") {
        notes = slave['notes'];
    }
    $('div#slavealloc_enabled').html(getEnabledStatusFromID(slave['enabled']));
    $('div#slavealloc_env').html(getEnvironmentFromID(slave['envid']));
    $('div#slavealloc_basedir').html(slave['basedir']);
    updateSlaveallocDiv('distros', slave['distroid'], 'slavealloc_distro', 'name');
    updateSlaveallocDiv('bitlengths', slave['bitsid'], 'slavealloc_bits', 'name');
    updateSlaveallocDiv('datacenters', slave['dcid'], 'slavealloc_datacenter', 'name');
    updateSlaveallocDiv('speeds', slave['speedid'], 'slavealloc_speed', 'name');
    updateSlaveallocDiv('purposes', slave['purposeid'], 'slavealloc_purpose', 'name');
    updateSlaveallocDiv('trustlevels', slave['trustid'], 'slavealloc_trustlevel', 'name');
    updateSlaveallocDiv('pools', slave['poolid'], 'slavealloc_pool', 'name');
    if (slaveclass === "") {
        slaveclass = getSlaveclassFromSlavealloc(slave['purposeid'], slave['trustid']);
    }
    if (slavetype === "") {
        slavetype = getSlavetypeByName(slave['name']);
        params = "?class=" + slaveclass + "&type=" + slavetype;
        $('div#slavetype').html("<a href=\"" + slavetype_url + params + "\">" + slavetype + "</a>");
    }
    // Markup bugs in notes.
    var marked_up_notes = markupBugs(notes);
    $('div#slavealloc_notes').html(marked_up_notes);
}

function byStartTimestamp(a, b) {
    var a2 = (a.start_timestamp) ? a.start_timestamp : a.request_timestamp;
    var b2 = (b.start_timestamp) ? b.start_timestamp : b.request_timestamp;
    return a2 - b2;
}

function flattenRebootObj(id, reboot_obj, action_type) {
    var flattened = {};
    flattened['id'] = id;
    flattened['action_type'] = action_type;
    flattened['finish_timestamp'] = reboot_obj['finish_timestamp'];
    flattened['start_timestamp'] = reboot_obj['start_timestamp'];
    flattened['request_timestamp'] = reboot_obj['request_timestamp'];
    flattened['state'] = reboot_obj['state'];
    flattened['text'] = reboot_obj['text'];
    return flattened;
}

function getReboots(slavename) {
    // We need to collate reboots and shutdowns
    // var slaveapi_baseurl = '/slave_health/json/slaves/';
    var slave_shutdown_url = slaveapi_baseurl + slavename + '/actions/shutdown_buildslave';
    var slave_reboot_url = slaveapi_baseurl + slavename + '/actions/reboot';
    var all_reboots = [];
    var offset = getPTOffset();
    $.ajax({
        url:      slave_shutdown_url,
        async:    false,
        dataType: 'json',
        success:  function (shutdown_json) {
            var key;
            for (key in shutdown_json['shutdown_buildslave']) {
                if (shutdown_json['shutdown_buildslave'].hasOwnProperty(key)) {
                    all_reboots.push(flattenRebootObj(key, shutdown_json['shutdown_buildslave'][key], 'shutdown'));
                }
            }
        }
    });
    $.ajax({
        url:      slave_reboot_url,
        async:    false,
        dataType: 'json',
        success:  function (reboot_json) {
            var key;
            for (key in reboot_json['reboot']) {
                if (reboot_json['reboot'].hasOwnProperty(key)) {
                    all_reboots.push(flattenRebootObj(key, reboot_json['reboot'][key], 'reboot'));
                }
            }
        }
    });

    var sorted_reboots = all_reboots.sort(byStartTimestamp);

    $('table#reboothistory tr:gt(0)').remove();
    if (sorted_reboots.length === 0) {
        var newrow = $('<tr>');
        newrow.append($('<td>').text('No reboot history found').addClass('problem').attr('colspan', 3));
        newrow.hide();
        $('table#reboothistory > tbody:last').after(newrow);
        newrow.fadeIn(500);
        newrow.css('display', 'table-row');
    } else {
        var numreboots = 0;
        $.each(sorted_reboots, function (i) {
            numreboots++;
            // Only show 10 most recent results
            if (numreboots > (sorted_reboots.length - 10)) {
                var newrow = $('<tr>');
                if (sorted_reboots[i].start_timestamp !== 0) {
                    var rebootdate = getDateFromSeconds(sorted_reboots[i].start_timestamp - offset);
                    newrow.append($('<td>').html(rebootdate.toLocaleString()));
                } else {
                    newrow.append($('<td>').text("In Progress"));
                }
                newrow.append($('<td>').text(sorted_reboots[i].action_type));
                newrow.append($('<td>').text(sorted_reboots[i].text));
                newrow.hide();
                $('table#reboothistory > tbody:last').after(newrow);
                newrow.fadeIn(500);
                newrow.css('display', 'table-row');
            }
        });
    }
}

function jobHistoryIsEmpty() {
  $('table#lasttenjobs > tbody:last').append("<tr><td class=\"problem\" colspan=\"4\">No job history found</td></tr>");
}

function getJobHistory(data) {
    // Get a list of links to masters so we can link directly to job results.
    $.ajax({
        url:      './json/masters.json',
        async:    false,
        dataType: 'json',
        success:  function (masterjson) {
            var key;
            for (key in masterjson) {
                if (masterjson.hasOwnProperty(key)) {
                    master_links[key] = masterjson[key];
                }
            }
        }
    });

    if (data.length == 0) {
      jobHistoryIsEmpty();
      return false;
    }

    var numbuilds = 0;
    var jobhistory = "";
    var offset = getPTOffset();
    $.each(data, function (i) {
        numbuilds++;
        var master_link = master_links[data[i]['master']];
        if (numbuilds <= 10) {
            var duration = data[i]['endtime'] - data[i]['starttime'];
            if (duration < 0) {
                duration = 0;
            }
            var durationStr = getDurationFromSeconds(duration);
            var startdate = getDateFromSeconds(data[i]['starttime'] - offset);
            var enddate = getDateFromSeconds(data[i]['endtime'] - offset);
            var newrow = $('<tr>').addClass(getLinkclassForResult(data[i]['result']));
            newrow.append($('<td>').html("<a href=\"http://" + master_link + "/builders/" + data[i]['buildername'] + "/builds/" + data[i]['buildnumber'] + "\">" + data[i]['buildername'] + "</a>"));
            newrow.append($('<td>').text(startdate.toLocaleString()));
            newrow.append($('<td>').text(enddate.toLocaleString()));
            newrow.append($('<td>').addClass('center').text(durationStr));
            newrow.hide();
            $('table#lasttenjobs > tbody:last').append(newrow);
            newrow.fadeIn(500);
            newrow.css('display', 'table-row');
        }
        jobhistory += "<a class=\"" + getLinkclassForResult(data[i]['result']) + "\" href=\"http://" + master_link + "/builders/" + data[i]['buildername'] + "/builds/" + data[i]['buildnumber'] + "\">" + getLetterForResult(data[i]['result']) + "</a>";
    });
    $('div#jobhistory').html(jobhistory);
}

function updateNagiosLink(slavename) {
    var slaveapi_slave_json = slaveapi_baseurl + slavename;
    $.getJSON(slaveapi_slave_json, function (slavedata) {
        $('a#nagiosexternallink').attr('href', nagios_history_baseurl + slavedata['fqdn']);
        $('button#nagios').removeAttr('disabled').removeClass('disabled');
    });
}

function disableRebootButtons() {
    disableButton('button#shutdownslave');
    disableButton('button#rebootslave');
}

function enableRebootButtons(slavename) {
    $('button#shutdownslave').click(function () { shutdownSlave(slavename); });
    if (isAWSInstance(slavename)) {
        $('button#rebootslave').click(function () { terminateInstance(slavename); });
    } else {
        $('button#rebootslave').click(function () { rebootSlave(slavename); });
    }
    $('button#shutdownslave').removeAttr('disabled').removeClass('disabled');
    $('button#rebootslave').removeAttr('disabled').removeClass('disabled');
}

var rebootthreshold = 300;
var shutdownthreshold = 300;
var lastshutdown;
var lastreboot;
function pollRebootStatus(requestid, slavename) {
    var resultsElement = $("#results");
    var url = slaveapi_baseurl + slavename + "/actions/reboot" + "?requestid=" + requestid;
    $.ajax(url, {"type": "get"})
        .done(function (data) {
            switch (data['state']) {
            case 0:
                updateStatus('div#rebootactionstatus', "Reboot is still pending.", "pending", 15000);
                setTimeout(pollRebootStatus, 15000, requestid, slavename);
                break;
            case 1:
                updateStatus('div#rebootactionstatus', "Reboot is in progress.", "pending", 15000);
                setTimeout(pollRebootStatus, 15000, requestid, slavename);
                break;
            case 2:
                updateStatus('div#rebootactionstatus', "Slave rebooted successfully", "success");
                getReboots(slavename);
                enableRebootButtons(slavename);
                break;
            default:
                updateStatus('div#rebootactionstatus', "Reboot failed", "failure");
                getReboots(slavename);
                enableRebootButtons(slavename);
                break;
            }
        });
}

function pollShutdownStatus(requestid, slavename) {
    var resultsElement = $("#results");
    var url = slaveapi_baseurl + slavename + "/actions/shutdown_buildslave" + "?requestid=" + requestid;
    $.ajax(url, {"type": "get"})
        .done(function (data) {
            switch (data['state']) {
            case 0:
                updateStatus('div#rebootactionstatus', "Shutdown is still pending.", "pending", 15000);
                setTimeout(pollShutdownStatus, 15000, requestid, slavename);
                break;
            case 1:
                updateStatus('div#rebootactionstatus', "Shutdown is in progress.", "pending", 15000);
                setTimeout(pollShutdownStatus, 15000, requestid, slavename);
                break;
            case 2:
                updateStatus('div#rebootactionstatus', "Buildbot shutdown successfully", "success");
                getReboots(slavename);
                enableRebootButtons(slavename);
                break;
            default:
                updateStatus('div#rebootactionstatus', "Shutdown failed", "failure");
                getReboots(slavename);
                enableRebootButtons(slavename);
                break;
            }
        });
}

function pollTerminationStatus(requestid, slavename) {
    var resultsElement = $("#results");
    var url = slaveapi_baseurl + slavename + "/actions/terminate" + "?requestid=" + requestid;
    $.ajax(url, {"type": "get"})
        .done(function (data) {
            switch (data['state']) {
            case 0:
                updateStatus('div#rebootactionstatus', "Termination is still pending.", "pending", 15000);
                setTimeout(pollTerminationStatus, 15000, requestid, slavename);
                break;
            case 1:
                updateStatus('div#rebootactionstatus', "Termination is in progress.", "pending", 15000);
                setTimeout(pollTerminationStatus, 15000, requestid, slavename);
                break;
            case 2:
                updateStatus('div#rebootactionstatus', "Instance terminated successfully", "success");
                getReboots(slavename);
                enableRebootButtons(slavename);
                break;
            default:
                updateStatus('div#rebootactionstatus', "Termination failed", "failure");
                getReboots(slavename);
                enableRebootButtons(slavename);
                break;
            }
        });
}

function shutdownSlave(slavename) {
    var slave_shutdown_url = slaveapi_baseurl + slavename + '/actions/shutdown_buildslave';
    var now = new Date();
    var elapsed = shutdownthreshold;

    if (lastshutdown instanceof Date) {
        elapsed = (now.getTime() - lastshutdown.getTime()) / 1000;
    }
    if (elapsed >= shutdownthreshold) {
        lastshutdown = now;
        disableRebootButtons();
        updateStatus('div#rebootactionstatus', "Shutdown triggered. Please wait.", "pending", 15000);
        $.post(slave_shutdown_url)
            .fail(function (response) {
                updateStatus('div#rebootactionstatus', "Got failure " + response.status + ": " + response.responseText, "failure", 0, true);
            })
            .done(function (data) {
                setTimeout(pollShutdownStatus, 15000, data["requestid"], slavename);
            });
    } else {
        updateStatus('div#rebootactionstatus', "Buildbot already shutdown within last " + rebootthreshold + " seconds.", "failure");
    }
}

function terminateInstance(slavename) {
    var slave_reboot_url = slaveapi_baseurl + slavename + '/actions/terminate';
    var now = new Date();
    var elapsed = rebootthreshold;

    if (lastreboot instanceof Date) {
        elapsed = (now.getTime() - lastreboot.getTime()) / 1000;
    }
    if (elapsed >= rebootthreshold) {
        lastreboot = now;
        disableRebootButtons();
        updateStatus('div#rebootactionstatus', "Termination triggered. Please wait.", "pending", 15000);
        $.post(slave_reboot_url)
            .fail(function (response) {
                updateStatus('div#rebootactionstatus', "Got failure " + response.status + ": " + response.responseText, "failure", 0, true);
            })
            .done(function (data) {
                setTimeout(pollRebootStatus, 15000, data["requestid"], slavename);
            });
    } else {
        updateStatus('div#rebootactionstatus', "Instance already terminated within last " + rebootthreshold + " seconds.", "failure");
    }
}

function rebootSlave(slavename) {
    var slave_reboot_url = slaveapi_baseurl + slavename + '/actions/reboot';
    var now = new Date();
    var elapsed = rebootthreshold;

    if (lastreboot instanceof Date) {
        elapsed = (now.getTime() - lastreboot.getTime()) / 1000;
    }
    if (elapsed >= rebootthreshold) {
        lastreboot = now;
        disableRebootButtons();
        updateStatus('div#rebootactionstatus', "Reboot triggered. Please wait.", "pending", 15000);
        $.post(slave_reboot_url)
            .fail(function (response) {
                updateStatus('div#rebootactionstatus', "Got failure " + response.status + ": " + response.responseText, "failure", 0, true);
            })
            .done(function (data) {
                setTimeout(pollRebootStatus, 15000, data["requestid"], slavename);
            });
    } else {
        updateStatus('div#rebootactionstatus', "Slave already rebooted within last " + rebootthreshold + " seconds.", "failure");
    }
}

function batchReboot(rebootType, threshold) {
    var linkSelector;
    var n;
    if (rebootType == "broken") {
	linkSelector = 'span#brokenrebootlink';
    } else if (rebootType == "idle") {
	linkSelector = 'span#idlerebootlink';
    } else {
	updateStatus('div#batchactionstatus span#message', "Unknown reboot type.", "failure", 0, true);
	return false;
    }
    // Disable the button we don't try to reboot in rapid succession.
    var $batchrebootlink = $(linkSelector);
    $batchrebootlink.removeClass('activelink').addClass('disabledLink');
    $batchrebootlink.unbind('click');
    $batchrebootlink.attr('title', "Disabled after initial attempt. Please reload page to try again.");
    var slavestoreboot;
    if (rebootType == "broken") {
        slavestoreboot = $("tr.broken td.slavename span").map(function(){
            return $(this).attr('id');
	}).get();
    } else if (rebootType == "idle") {
        slavestoreboot = $("tr.broken td.elapsed, tr.working td.elapsed").filter(function() {
             return +$(this).attr('seconds') > threshold;
	}).map(function() {
             return $(this).closest('td').prev().find("span").attr('id');
        });
    }
    if (slavestoreboot.length == 0) {
	updateStatus('div#batchactionstatus span#message', "No slaves match criteria.", "failure", 0, true);
    } else {
	$.each(slavestoreboot, function(index, slavename) {
	    var slave_reboot_url = slaveapi_baseurl + slavename + '/actions/reboot';
            $.post(slave_reboot_url)
		.fail(function (response) {
                    updateStatus('div#batchactionstatus span#message', slavename + " reboot failed", "failure", 0, true);
		})
		.done(function (data) {
                    updateStatus('div#batchactionstatus span#message', slavename + " reboot queued", "success");
		});
	});
    }
}

function rebootBrokenSlaves() {
    return batchReboot("broken");
}

function rebootIdleSlaves(minutes) {
    if (isPositiveInteger(minutes) == false) {
	updateStatus('div#batchactionstatus span#message', "Minute value not a positive integer.",
		     "failure", 0, true);
	return false;
    }
    var seconds = minutes * 60;
    return batchReboot("idle", seconds);

}

function swapBrokenAndIdle(pending_count) {
    if (pending_count > 0) {
        $("span.pending").html(pending_count).addClass('broken');
        $("tr.idle").removeClass('idle').addClass('broken');
        $("tr.idle td.state, tr.broken td.state").html("broken");
    } else {
        $("tr.broken").removeClass('broken').addClass('idle');
        $("tr.idle td.state, tr.broken td.state").html("idle");
    }
}

function generateReportsDropdown(current_page) {
    current_page = typeof current_page !== 'undefined' ? current_page : 'index';
    var report_html = '<div id="reports" class="dropdown"><h2>Reports</h2>\n' +
	              '  <div class="dropdownReports">\n' +
		      '    Available reports:<br/>\n' +
		      '    <ul>\n';
    if (current_page != 'buildduty') {
        report_html += '      <li><a target="_builddutyreport" href="./buildduty_report.html">buildduty report</a></li>\n';
    }
    report_html += '      <li><hr/></li>\n' +
                   '      <li><a target="_hgstats" href="http://nigelbabu.github.io/hgstats/#hours/2">hg status</a></li>\n' +
		   '      <li><a target="_ec2dashboard" href="https://www.hostedgraphite.com/da5c920d/grafana/#/dashboard/temp/5d509a54d0b496d184023bab35c17d0f41e6c607">EC2 dashboard</a></li>\n' +
                   '      <li><a target="_runnerdashboard" href="https://stats.taskcluster.net/grafana/#/dashboard/db/runner">Runner Dashboard</a></li>\n' +
                   '      <li><a target="_smokepinguse1" href="http://netops2.private.scl3.mozilla.com/smokeping/sm.cgi?target=Datacenters.RELENG-SCL3.nagios1-releng-use1">smokeping - use1</a></li>\n' +
                   '      <li><a target="_smokepingusw2" href="http://netops2.private.scl3.mozilla.com/smokeping/sm.cgi?target=Datacenters.RELENG-SCL3.nagios1-releng-usw2">smokeping - usw2</a></li>\n' +
                   '    </ul>\n' +
                   '  </div>\n' +
                   '</div>\n';
  $("div.topbarright").prepend(report_html);
}
