var DEFAULT_OUTPUT_LENGTH = 0;
var BUFFER_CHAR_WIDTH = 50;

var KEY_CODE = {
    192: 'backquote', 49: '1', 50: '2', 51: '3', 52: '4', 53: '5',
    54: '6', 55: '7', 56: '8', 57: '9', 48: '0', 109: 'hyphen', 189: 'hyphen', 107: 'equal', 187: 'equal',
    81: 'q', 87: 'w', 69: 'e', 82: 'r', 84: 't',
    89: 'y', 85: 'u', 73: 'i', 79: 'o', 80: 'p', 219: 'bracketleft', 221: 'bracketright', 
    65: 'a', 83: 's', 68: 'd', 70: 'f', 71: 'g',
    72: 'h', 74: 'j', 75: 'k', 76: 'l', 59: 'semicolon', 186: 'semicolon', 222: 'quote',
    90: 'z', 88: 'x', 67: 'c', 86: 'v', 66: 'b',
    78: 'n', 77: 'm', 188: 'comma', 190: 'period', 191: 'slash',
    32: 'space'
};

function camel_case(name) {
    var words = name.split('_');
    for (var i = 0; i < words.length; ++i) {
        if (!words[i])
            continue;
        words[i] = 
            words[i].substring(0, 1).toUpperCase() 
            + words[i].substring(1);
    }
    return words.join('');
}

var Class = function(proto) {
        var klass = function() {
                if (typeof this.initialize == "function") {
                        this.initialize.apply(this, arguments);
                }
        };
        $.extend(klass, this);
        if (proto != undefined) {
                klass.prototype = proto;
                klass.prototype.constructor = klass;
        }
        return klass;
};

Class.load = function(name, callback) {
    $.getScript("script/" + name + ".js", callback);
};

Class.createInstance = function(name, init) {
    var klass = eval(camel_case(name));
    return new klass(init);
};

Class.extend = function(klass, extension) {
    return new Class($.extend({}, klass.prototype, extension));
};

var Model = new Class({

    output_length: DEFAULT_OUTPUT_LENGTH,

    initialize: function(schema, params) {

        var model = this;

        var buffer = $('#buffer');

        this.schema = schema;

        this.sink = function(s) {
            model.commit(s);
        };

        if (schema.buffer_size)
            this.buffer_size = schema.buffer_size;

        if (schema.output_length)
            this.output_length = schema.output_length;

        if (params.buffer_size)
            this.buffer_size = params.buffer_size;

        if (params.output_length)
            this.output_length = params.output_length;

        if (this.buffer_size)
            buffer.width(this.buffer_size * BUFFER_CHAR_WIDTH);

        this.layer = 0;
        if (schema.layers) {
          this.render(schema.layers[0]);
        }
        else {
          this.render(schema.key_map);
        }
        $('#column_0_place_holder').addClass('unused');

        if (schema.update_prompt) {
            this.update_prompt = function(_prompt) {
                schema.update_prompt(_prompt);
            };

            if (params['prompt'])
                schema.update_prompt(params['prompt']);
        }

        buffer.keydown(function(event) {
            return model.process_keydown(event);
        });

        buffer.keyup(function(event) {
            return model.process_keyup(event);
        });

        buffer.keypress(function(event) {
            return model.process_keypress(event);
        });

        buffer.focus();

        $('#output').keydown(function(event) {
            if (event.keyCode == 9) {  // Tab
                buffer.focus();
                return false;
            }
            return true;
        });
    },

    lower_key: function(event) {
        var dom_key = $('#key_' + KEY_CODE[event.keyCode]);
        dom_key.attr('class', 
                     dom_key.attr('class').replace('keyup', 'keydown')
                                          .replace('light_', 'dark_')
        );
    },

    raise_key: function(event) {
        var dom_key = $('#key_' + KEY_CODE[event.keyCode]);
        dom_key.attr('class', 
                     dom_key.attr('class').replace('keydown', 'keyup')
                                          .replace('dark_', 'light_')
        );
    },

    switch_layers: function(event) {
      // now supporting 2 layers
      var layer = event.shiftKey ? 1 : 0;
      if (layer != this.layer) {
        this.layer = layer;
        if (this.schema.layers) {
          this.render(this.schema.layers[layer]);
        }
      }
    },

    focus_prompt: function () {
      try {
        parent.window.setTimeout(
            "$('#prompt').select().focus();", 
            50
        );
      } catch (e) {
      }
    },

    process_keydown: function(event) {
        //alert('keydown\ncharCode = ' + event.charCode + '\nkeyCode = ' + event.keyCode);

        if (event.altKey || event.ctrlKey)
            return true;

        this.switch_layers(event);
        
        switch (event.keyCode) {
            case 13:  // Enter
                this.focus_prompt();
                break;

            case 9:  // Tab
                $('#output').select().focus();
                break;

            case 8:  // Backspace
                this.schema.process_backspace();
                break;

            case 27:  // ESC
                this.schema.process_escape();
                break;

            default:
                if (event.keyCode in KEY_CODE) {
                    this.lower_key(event);
                    if (this.schema.process_keydown)
                        this.schema.process_keydown(KEY_CODE[event.keyCode], this.sink);

                    this.schema.process_input(KEY_CODE[event.keyCode], this.sink);
                }
                break;
        }

        return false;
    },

    process_keyup: function(event) {

        if (event.altKey || event.ctrlKey)
            return true;

        this.switch_layers(event);

        if (event.keyCode in KEY_CODE) {
            this.raise_key(event);
            if (this.schema.process_keyup)
                this.schema.process_keyup(KEY_CODE[event.keyCode], this.sink);
        }

        return false;
    },

    process_keypress: function(event) {
        return false;
    },

    commit: function(s) {
        if (s == '')
            return;
        
        var t = $('#output').val();
        var q = t ? t.split(' ') : [];

        q.push(s);

        // limit queue length
        if (this.output_length > 0 && 
            q.length > this.output_length)
                q.shift();

        $('#output').val(q.join(' '));
    },

    render: function(key_map) {
        var unused = {};
        for (var x in KEY_CODE) {
            unused[KEY_CODE[x]] = true;
        }
        for (var color in key_map) {
            var labels = key_map[color];
            for (var key in labels) {
                $('#key_' + key).attr('class', 'keyup');
                $('#key_' + key).addClass(color).addClass('light_' + color);
                $('#key_' + key + ' span').html(labels[key]);
                delete unused[key];
            }
        }
        for (var key in unused) {
            $('#key_' + key).addClass('unused');
        }
    }

});

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

var model;

$(document).ready(function () {
    var params = parse_params();
    var schema_name = params['schema'] || 'english';

    document.title += ' - ' + schema_name;

    function schema_onload() {
        //alert('loading schema: ' + schema_name);
        var schema = Class.createInstance(schema_name, params);
        model = new Model(schema, params);
    }

    Class.load(schema_name, schema_onload);
});
