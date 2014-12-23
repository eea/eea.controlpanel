if(window.EEA === undefined){
  var EEA = {
    who: 'eea.controlpanel',
    version: '0.1'
  };
}

EEA.ControlPanelInit = function(){
    var panels = $("div[id^='panel']");
    jQuery.each(panels, function(index, element){
        element = $(element);
        element.draggable();
        element.resizable();
    });

    $( "#panel1 h3 span .eea-icon-refresh" ).click(function() {
        EEA.ControlPanelLoginStatus();
    });

    $( "#panel3 h3 span .eea-icon-refresh" ).click(function() {
        EEA.ControlPanelDbActivity();
    });

    // Refresh "Login status" panel
    var login_status = new EEA.ControlPanelLoginStatus();
    login_status.refresh();

    // Refresh "DB activity" panel
    var login_status = new EEA.ControlPanelDbActivity();
    login_status.refresh();
};

EEA.ControlPanelDbActivity = function(){
    var panel = $('#panel3');
    $('#panel3 .container').css({ "background-color": "rgb(221, 221, 221)" });
    jQuery.ajax({
        url: '@@eea.controlpaneldb.html',
        data: {},
        success: function(data, textStatus, jqXHR){
            $('#panel3 .container').html('');
            var logs = data['log'];
            jQuery.each(logs, function(index, element){
                var element_html = $('<div></div>');
                var username = jQuery.trim(element['user_name'].substring(4, element['user_name'].length));
                element_html.append(element['description'] + '<br />');
                element_html.append(element['time'] + '  |  ');
                element_html.append('<a title="" href="/author/' + username+ '">' + username + '</a>' + '  |  ');
                element_html.append(element['size'] + ' bytes');
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
}

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
            var logs = data['active_users'];
            jQuery.each(logs, function(index, element){
                var element_html = $('<div></div>');
                var status_ccs = 'eea-icon-circle-o';
                if(element[1]){status_ccs = 'eea-icon-circle';}
                element_html.append('<span class="eea-icon ' + status_ccs + '"></span>');
                element_html.append('<a title="" href="/author/' + index + '">' + element[0] + '</a>');
                element_html.append(' :: ' + element[2]);
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
}

EEA.EEACPBAnalyticsPanel = function(){
    var panel = $('#panel4');
    $('#panel1 .container').css({ "background-color": "rgb(221, 221, 221)" });
    jQuery.ajax({
        url: '@@eea.controlpaneleeacpbstatus.html',
        data: {},
        success: function(data, textStatus, jqXHR){
            $('#panel4 .container').html('');
            var logs = data['active_ips'];
            jQuery.each(logs, function(index, element){
                var element_html = jQuery('<div />');
                var status_ccs = 'eea-icon-circle-o';
                if(element.status){status_ccs = 'eea-icon-circle';}

                element_html.append('<span class="eea-icon ' + status_ccs + '"></span>')
                            .append(index)
                            .append(' - ');

                var nr_hosts = element.hostnames.length;
                jQuery.each(element.hostnames, function(idx, host){
                    element_html.append('<a title="" href="http://' + host + '">' + host + '</a>');
                    if (idx !== nr_hosts - 1) {
                        element_html.append(',')
                    }
                });
                
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
}

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
        EEA.EEACPBAnalyticsPanel();
    }
});
