// extract query parameters from url
function parse_params() {
    var params = {};
    var s = document.location.search;
    if (!s) {
        return params;
    }
    var i = s.indexOf("?");
    if (i != -1) {
        s = s.substring(i + 1);
    }
    var list = s.split("&");
    for (i = 0; i < list.length; ++i) {
        var p = list[i].split("=");
        var key = decodeURIComponent(p[0]);
        var value = (p.length > 1) ? decodeURIComponent(p[1]) : true;
        params[key] = value;
    }
    return params;
}

function schema_change() {
    var selected = $('#schema_select option:selected');
    $('#schema').val(selected.val());
    document.title = document.title.replace(
        /(?: - .*)?$/, 
        ' - ' + selected.text()
    );
    $('#submit').click();
}

function focus_buffer() {
    try {
        $('#model_frame').get(0).contentWindow.setTimeout(
            "$('#buffer').focus();", 
            50
        );
    } catch (e) {
    }
}

function prompt_keypress(event) {

    if (event.shiftKey && event.keyCode == 9 /* Tab */ || 
        event.keyCode == 13 /* Enter */) {
        
        if (event.keyCode == 13) {
            var sink = $('#model_frame').get(0)
                .contentWindow.model.update_prompt;
            if (sink)
                sink($('#prompt').val());
        }

        focus_buffer();
        return false;
    }

    return true;
}

$(document).ready(function() {
    var params = parse_params();
    var schema_name = params['schema'] || 'english';
    var options = $('#schema_select option');
    for (var i = 0; i < options.length; ++i)
        if (options.eq(i).val() == schema_name)
            $('#schema_select').attr('selectedIndex', i);

    $('#prompt').keypress(prompt_keypress).focus();
    $('#schema_select').change(schema_change);
    schema_change();
});
