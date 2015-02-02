if(window.EEA === undefined){
  var EEA = {
    who: 'eea.controlpanel',
    version: '0.1'
  };
}

EEA.ControlPanelInit = function(){
    var panels = $("div[id^='panel']");

    function moveOnTop(element){
        var maxzindex = 0;
        jQuery("div[id^='panel']").each(function(){
            var thiszindex = parseInt(jQuery(this).css("z-index"), 10);
            if (maxzindex < thiszindex) {
                maxzindex = thiszindex;
            }
        });
        jQuery(element).css("z-index", maxzindex + 1);
    }

    jQuery.each(panels, function(index, element){
        element = $(element);
        element.draggable({
            start:function(){
                moveOnTop(this);
            }
        });
        element.resizable({
            start:function(){
                moveOnTop(this);
            }
        });
        element.click(function(){
            moveOnTop(this);
        });
    });

    $( "#panel1 h3 span .eea-icon-refresh" ).click(function() {
        EEA.ControlPanelLoginStatus();
    });

    $( "#panel3 h3 span .eea-icon-refresh" ).click(function() {
        EEA.ControlPanelDbActivity();
    });

    $( "#panel4 h3 span .eea-icon-refresh" ).click(function() {
        EEA.EEACPBAnalyticsPanel();
    });

    // Refresh "Login status" panel
    var login_status = new EEA.ControlPanelLoginStatus();
    login_status.refresh();

    // Refresh "DB activity" panel
    var db_status = new EEA.ControlPanelDbActivity();
    db_status.refresh();

    // Refresh "EEA CPB analytics" panel
    var eea_cpb_status = new EEA.EEACPBAnalyticsPanel();
    eea_cpb_status.refresh();
};

EEA.ControlPanelDbActivity = function(){
    var panel = $('#panel3');
    $('#panel3 .container').css({ "background-color": "rgb(221, 221, 221)" });
    jQuery.ajax({
        url: '@@eea.controlpaneldb.html',
        data: {},
        success: function(data, textStatus, jqXHR){
            $('#panel3 .container').html('');
            var logs = data.log;
            jQuery.each(logs, function(index, element){
                var element_html = $('<div class="controlpanel-list-row"></div>');
                var username = jQuery.trim(element.user_name.substring(4, element.user_name.length));
                element_html.append(element.description + '<br />');
                element_html.append(element.time + '  |  ');
                element_html.append('<a title="" href="/author/' + username+ '">' + username + '</a>' + '  |  ');
                element_html.append(element.size + ' bytes');
                panel.children('.container').append(element_html);
                $('#panel3 .container').css({ "background-color": "#f0f0f0" });
            });
        },
        error: function(jqXHR, textStatus, errorThrown){
            console.log(errorThrown);
        }
    });
};

EEA.ControlPanelDbActivity.prototype = {
    refresh: function(){
    setInterval(function () {
        EEA.ControlPanelDbActivity();
    }, 60000);
    }
};

EEA.ControlPanelLoginStatusAgent = function(){
    var url = window.location.pathname;
    if (!url.match(/portal_factory/)) {
        jQuery.ajax({
            url: '@@eea.controlpanelloginstatusagent.html',
            error: function(jqXHR, textStatus, errorThrown){
                console.log(errorThrown);
            }
        });
        setInterval(function () {
            jQuery.ajax({
                url: '@@eea.controlpanelloginstatusagent.html',
                error: function(jqXHR, textStatus, errorThrown){
                    console.log(errorThrown);
                }
            });
        }, 300000);
    }
};

EEA.ControlPanelLoginStatus = function(){
    var panel = $('#panel1');
    $('#panel1 .container').css({ "background-color": "rgb(221, 221, 221)" });
    jQuery.ajax({
        url: '@@eea.controlpanelloginstatus.html',
        data: {},
        success: function(data, textStatus, jqXHR){
            $('#panel1 .container').html('');
            var logs = data.active_users;
            var users = [];
            jQuery.each(logs, function(index, element){
                if (element[0] === ""){
                    element[0] = index;
                }
                users.push({index:index, element:element});
            });

            users.sort(function(a, b){
                if (a.element[1] === b.element[1]){
                    if (a.element[0] > b.element[0]){
                        return 1;
                    }
                    if (a.element[0] < b.element[0]){
                        return -1;
                    }
                    if (a.element[0] === b.element[0]){
                        return 0;
                    }
                }
                else {
                    if (a.element[1]){
                        return -1;
                    }
                    else {
                        return 1;
                    }
                }
            });

            panel.children('.container').append('<div class="controlpanel-user-header"><div class="controlpanel-user-number">Nr.</div><div class="controlpanel-user-name">Username</div> <div class="controlpanel-user-lastlogin">Last login</div></div>');
            panel.children('.container').append('<div style="clear:both"><!-- --></div>');
            jQuery.each(users, function(idx, user){
                var element_html = $('<div class="controlpanel-list-row controlpanel-user-row"></div>');
                element_html.append('<div class="controlpanel-user-number">' + idx+ '</div>');
                var status_ccs = 'eea-icon-circle-o';
                if(user.element[1]){status_ccs = 'eea-icon-circle';}
                element_html.append('<div class="controlpanel-user-name"><span class="eea-icon ' + status_ccs + '"></span>');
                element_html.append('<a title="" href="/author/' + user.index + '">' + user.element[0] + '</a></div>');


                element_html.append('<div class="controlpanel-user-lastlogin">' + user.element[2] +'</div>');
                panel.children('.container').append(element_html);
                $('#panel1 .container').css({ "background-color": "#f0f0f0" });
            });
        },
        error: function(jqXHR, textStatus, errorThrown){
            console.log(errorThrown);
        }
    });
};

EEA.ControlPanelLoginStatus.prototype = {
    refresh: function(){
    setInterval(function () {
        EEA.ControlPanelLoginStatus();
    }, 300000);
    }
};

EEA.EEACPBAnalyticsPanel = function(){
    var panel = $('#panel4');
    $('#panel4 .container').css({ "background-color": "rgb(221, 221, 221)" });
    jQuery.ajax({
        url: '@@eea.controlpaneleeacpbstatus.html',
        data: {},
        success: function(data, textStatus, jqXHR){
            $('#panel4 .container').html('');
            var logs = data.active_ips;
            jQuery.each(logs, function(index, element){
                var element_html = jQuery('<div class="controlpanel-list-row" />');
                var status_ccs = 'eea-icon-circle-o';
                if(element.status){status_ccs = 'eea-icon-circle';}

                element_html.append('<span class="eea-icon ' + status_ccs + '"></span>')
                            .append(index)
                            .append(' - ');

                var nr_hosts = element.hostnames.length;
                jQuery.each(element.hostnames, function(idx, host){
                    element_html.append('<a title="" href="http://' + host + '">' + host + '</a>');
                    if (idx !== nr_hosts - 1) {
                        element_html.append(',');
                    }
                });
                element_html.append(' :: ' + element.last_ping);
                panel.children('.container').append(element_html);
                $('#panel4 .container').css({ "background-color": "#f0f0f0" });
            });
        },
        error: function(jqXHR, textStatus, errorThrown){
            console.log(errorThrown);
        }
    });
};

EEA.EEACPBAnalyticsPanel.prototype = {
    refresh: function(){
    setInterval(function () {
        EEA.EEACPBAnalyticsPanel();
    }, 300000);
    }
};

jQuery(document).ready(function(){
    var url = window.location.pathname;
    EEA.ControlPanelLoginStatusAgent();

    if (url.match(/eea.controlpanel.html$/)) {
        // Setup panels
        EEA.ControlPanelInit();

        // Populate database activity panel
        EEA.ControlPanelDbActivity();

        // Populate today login panel
        EEA.ControlPanelLoginStatus();

        // Populate login history panel
        // TODO

        // Populate EEA CPB analytics panel
        EEA.EEACPBAnalyticsPanel();
    }
});
