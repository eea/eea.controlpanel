if(window.EEA === undefined){
  var EEA = {
    who: 'eea.controlpanel',
    version: '1.0'
  };
}

EEA.ControlPanelInit = function(){
    var panels = $("div[id^='panel']");
    jQuery.each(panels, function(index, element){
        element = $(element);
        element.draggable();
        element.resizable();
    });
};

EEA.ControlPanelDbActivity = function(){
    var panel = $('#panel3');
    jQuery.ajax({
        url: '@@eea.controlpaneldb.html',
        data: {},
        success: function(data, textStatus, jqXHR){
            var logs = data['log'];
            jQuery.each(logs, function(index, element){
                var element_html = $('<div></div>');
                var username = jQuery.trim(element['user_name'].substring(4, element['user_name'].length));
                element_html.append(element['description'] + '<br />');
                element_html.append(element['time'] + '  |  ');
                element_html.append('<a title="" href="/author/' + username+ '">' + username + '</a>' + '  |  ');
                element_html.append(element['size'] + ' bytes');
                panel.children('.container').append(element_html);
            });
        },
        error: function(jqXHR, textStatus, errorThrown){
            console.log(errorThrown);
        }
    });
};

EEA.ControlPanelLoginStatusAgent = function(){
    setInterval(function () {
        jQuery.ajax({
            url: '@@eea.controlpanelloginstatusagent.html',
            data: {},
            error: function(jqXHR, textStatus, errorThrown){
                console.log(errorThrown);
            }
        });
    }, 5000);
    // TODO: set to 10 minutes = 600000
};

EEA.ControlPanelLoginStatus = function(){
    var panel = $('#panel1');
    jQuery.ajax({
        url: '@@eea.controlpanelloginstatus.html',
        data: {},
        success: function(data, textStatus, jqXHR){
            panel.children('.container').append(data);
        },
        error: function(jqXHR, textStatus, errorThrown){
            console.log(errorThrown);
        }
    });
};

jQuery(document).ready(function(){
    console.log('CONTROL PANLE init +++++++++++++++++++');
    // Setup panels
    EEA.ControlPanelInit();

    // Populate database activity panel
    EEA.ControlPanelDbActivity();

    // Populate today login panel
    EEA.ControlPanelLoginStatusAgent();
    EEA.ControlPanelLoginStatus();

    // Populate login history panel
    // TODO
});