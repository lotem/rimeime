var Zhung = new Class({

  key_map: {
    /*
    blue: {
      '1': '1', '2': '2', '3': '3', '4': '4', '5': '5',
      '6': '6', '7': '7', '8': '8', '9': '9', '0': '0' 
    },
    yellow: {
      'backquote': '`', 'hyphen': '-', 'equal': '=',
      'bracketleft': '[', 'bracketright': ']',
      'semicolon': ';', 'quote': '\'', 
      'comma': ',', 'period': '.', 'slash': '/'
    },
    */
    green: {
      'q': 'ㄈ', 'w': 'ㄇ<sub>ㄢ</sub>', 'e': 'ㄆ<sub>ㄡ</sub>', 'r': 'ㄅ<sub>ㄠ</sub>', 't': 'ㄪ',
      'y': 'ㄩ', 'u': 'ㄉ<sub>ㄞ</sub>', 'i': 'ㄊ<sub>ㄟ</sub>', 'o': 'ㄋ<sub>ㄣ</sub>', 'p': 'ㄌ',
      'a': 'ㄚ', 's': '<sup>ㄏㄒ</sup><sub>ㄛ</sub>', 'd': '<sup>ㄎㄑ</sup><sub>ㄜ</sub>', 'f': '<sup>ㄍㄐ</sup><sub>ㄝ</sub>', 'g': 'ㄨ',
      'h': 'ㄧ', 'j': 'ㄓ<sub>ˆ</sub>', 'k': 'ㄔ<sub>ˊ</sub>', 'l': 'ㄕ<sub>ˋ</sub>', 
      'z': 'ㄦ', 'x': 'ㄙ', 'c': 'ㄘ', 'v': 'ㄗ', 'b': 'ㄤ',
      'n': 'ㄥ', 'm': 'ㄖ' 
    },
    red: {
      'space': ' '
    }
  },

  buffer_size: 3,

  _slot: ['', '', '', ''],

  _slot_is_empty: function() {
    for (var i = 0; i < this._slot.length; ++i) {
      if (this._slot[i] != '')
        return false;
    }
    return true;
  },

  _fill_slot: function(part, value) {
    this._slot[part] = value;
  },

  _update_buffer: function() {
    $('#buffer').val(this._slot.join(''));
  },

  _clear_buffer: function() {
    this._slot = ['', '', '', ''];
    $('#buffer').val('');
  },

  _clear_output: function() {
    $('#output').val('');
  },

  process_escape: function() {
    this._clear_output();
    this._clear_buffer();
  },

  process_input: function(key, sink) {
    var dom_key = $('#key_' + key);
    var key_name = $('span', dom_key).text();

    // shengdiau
    if (!this._slot_is_empty() && 
        ((key == 'space' || key == 'j' || key == 'k' || key == 'l'))) {
      if (key != 'space')
        this._fill_slot(3, key_name.charAt(key_name.length - 1));
      if (this._slot[0] && !this._slot[1] && !this._slot[2]) {
        if (this._slot[0] == 'ㄅ') this._slot[0] = 'ㄠ';
        else if (this._slot[0] == 'ㄆ') this._slot[0] = 'ㄡ';
        else if (this._slot[0] == 'ㄇ') this._slot[0] = 'ㄢ';
        else if (this._slot[0] == 'ㄉ') this._slot[0] = 'ㄞ';
        else if (this._slot[0] == 'ㄊ') this._slot[0] = 'ㄟ';
        else if (this._slot[0] == 'ㄋ') this._slot[0] = 'ㄣ';
        else if (this._slot[0] == 'ㄍ') this._slot[0] = 'ㄝ';
        else if (this._slot[0] == 'ㄎ') this._slot[0] = 'ㄜ';
        else if (this._slot[0] == 'ㄏ') this._slot[0] = 'ㄛ';
      }
      var s = this._slot.join('');
      sink(s);
      this._clear_buffer();
    }
    // jaiyin
    else if (key == 'h' || key == 'g' || key == 'y') {
      this._fill_slot(1, key_name.charAt(0));
      if (key == 'h' || key == 'y') {
        var shengmu = this._slot[0];
        if (shengmu == 'ㄍ') this._fill_slot(0, 'ㄐ');
        else if (shengmu == 'ㄎ') this._fill_slot(0, 'ㄑ');
        else if (shengmu == 'ㄏ') this._fill_slot(0, 'ㄒ');
      }
    }
    // shengmu
    else if (this._slot_is_empty() && 
             key != 'a' && key != 'b' && key != 'n' && key != 'z') {
      this._fill_slot(0, key_name.charAt(0));
    }
    // yunmu
    else {
      this._fill_slot(2, key_name.charAt(key_name.length - 1));
    }
      
    this._update_buffer();
  },

  process_backspace: function() {
    for (var i = 2; i >= 0; --i)
      if (this._slot[i] != '') {
        this._slot[i] = '';
        break;
      }
    this._update_buffer();
  }

});

