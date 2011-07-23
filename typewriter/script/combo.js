var Combo = new Class({

    key_map: {
    },

    key_order: ''.split(' '),

    key_value: { 
    },

    pm2py: function(pm) {
        var py = pm
        ;

        return py;
    },

    // pinyin to pinma translation
    py2pm: function (py) {
        var pm = py
        ;

        return pm;
    },

    _combo: {},

    _held: {},

    _held_count: 0,

    _update_buffer: function() {
        var keys = [];
        for (var i = 0; i < this.key_order.length; ++i) {
            var k = this.key_order[i];
            if (this._combo[k])
                keys.push(this.key_value[k]);
        }
        $('#buffer').val(keys.join('-'));
    },

    _clear_buffer: function() {
        this._combo = {};
        $('#buffer').val('');
    },

    _clear_output: function() {
        $('#output').val('');
    },

    _reset_marking: function() {

        $('.missing').removeClass('missing');
        $('.hit').removeClass('hit');
        $('.typo').removeClass('typo');

        if (this._pm == undefined)
            return;

        var pm_array = this._pm.split('-');
        for (var i = 0; i < pm_array.length; ++i) {
            var key = this._pm_keymap[pm_array[i]];
            $('#key_' + key).addClass('missing');
        }
    },

    process_escape: function() {
        this._clear_buffer();
        this._clear_output();
        this._reset_marking();
    },

    process_backspace: function() {
        this._clear_buffer();
    },

    process_input: function() {
    },

    process_keydown: function(key, sink) {

        if (this._held_count == 0)
            this._reset_marking();

        if (this._held[key] == undefined) {
            this._held[key] = true;
            ++this._held_count;
        }

        this._combo[key] = true;
        this._update_buffer();

        if (this._pm != undefined) {
            var dom_key = $('#key_' + key);
            if (dom_key.hasClass('missing'))
                dom_key.removeClass('missing').addClass('hit');
            else if (!dom_key.hasClass('hit'))
                dom_key.addClass('typo');
        }
    },

    process_keyup: function(key, sink) {

        if (this._held[key] != undefined) {
            delete this._held[key];
            --this._held_count;
        }

        if (this._held_count == 0) {
            sink(this.combo2py(this._combo));
            this._clear_buffer();
        }
    },

    combo2py: function(combo) {
        var pm = '';
        for (var i = 0; i < this.key_order.length; ++i) {
            var k = this.key_order[i];
            if (combo[k])
                pm += this.key_value[k];
        }
        
        return this.pm2py(pm);
    },

    initialize: function (params) {

        this._pm_keymap = {};
        for (var i = 0; i < this.key_order.length; ++i) {
            var k = this.key_order[i];
            this._pm_keymap[this.key_value[k]] = k;
        }

        if (params && params['prompt']) {
            this.output_length = 1;
        }
    },

    update_prompt: function(_prompt) {
        if (!_prompt) {
            delete this._pm;
            $('#prompt').html('');
        } else {
            this._pm = this.py2pm(_prompt);
            $('#prompt').html(_prompt + ' = <b>' + this._pm + '</b>');
        }
        this._reset_marking();
    }

});

