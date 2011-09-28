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
      'q': 'ㄪ', 'w': 'ㄈ<sub>ㄤ</sub>', 'e': 'ㄇ<sub>ㄢ</sub>', 'r': 'ㄆ<sub>ㄡ</sub>', 't': 'ㄅ<sub>ㄠ</sub>',
      'y': 'ㄉ<sub>ㄞ</sub>', 'u': 'ㄊ<sub>ㄟ</sub>', 'i': 'ㄋ<sub>ㄣ</sub>', 'o': 'ㄌ<sub>ㄥ</sub>', /* 'p': '', */
      'a': 'ㄏ<sub>ㄚ</sub>', 's': 'ㄎ<sub>ㄛ</sub>', 'd': 'ㄍ<sub>ㄜ</sub>', 'f': 'ㄨ', 'g': 'ㄝ',
      'h': 'ㄩ', 'j': 'ㄧ', 'k': 'ㄗ<sub>ˊ</sub>', 'l': 'ㄘ<sub>ˋ</sub>',
      /* 'z': '', */ 'x': 'ㄖ', 'c': 'ㄕ', 'v': 'ㄔ', 'b': 'ㄓ',
      'n': 'ㄦ<sub>ˆ</sub>', 'm': 'ㄙ<sub>˙</sub>' 
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
        ((key == 'space' || key == 'm' || key == 'k' || key == 'l' || key == 'n'))) {
      if (key != 'space')
        this._fill_slot(3, key_name.charAt(key_name.length - 1));
      if (this._slot[0] && !this._slot[1] && !this._slot[2]) {
        if (this._slot[0] == 'ㄅ') this._slot[0] = 'ㄠ';
        else if (this._slot[0] == 'ㄆ') this._slot[0] = 'ㄡ';
        else if (this._slot[0] == 'ㄇ') this._slot[0] = 'ㄢ';
        else if (this._slot[0] == 'ㄈ') this._slot[0] = 'ㄤ';
        else if (this._slot[0] == 'ㄉ') this._slot[0] = 'ㄞ';
        else if (this._slot[0] == 'ㄊ') this._slot[0] = 'ㄟ';
        else if (this._slot[0] == 'ㄋ') this._slot[0] = 'ㄣ';
        else if (this._slot[0] == 'ㄌ') this._slot[0] = 'ㄥ';
        else if (this._slot[0] == 'ㄍ') this._slot[0] = 'ㄜ';
        else if (this._slot[0] == 'ㄎ') this._slot[0] = 'ㄛ';
        else if (this._slot[0] == 'ㄏ') this._slot[0] = 'ㄚ';
      }
      var s = this._slot.join('');
      sink(s);
      this._clear_buffer();
    }
    // jaiyin
    else if (key == 'f' || key == 'j' || key == 'h') {
      this._fill_slot(1, key_name.charAt(0));
      if (key == 'j' || key == 'h') {
        var shengmu = this._slot[0];
        if (shengmu == 'ㄍ') this._fill_slot(0, 'ㄐ');
        else if (shengmu == 'ㄎ') this._fill_slot(0, 'ㄑ');
        else if (shengmu == 'ㄏ') this._fill_slot(0, 'ㄒ');
      }
    }
    // shengmu
    else if (this._slot_is_empty() && 
             key != 'g' && key != 'n') {
      this._fill_slot(0, key_name.charAt(0));
    }
    // yunmu
    else {
      if (key == 'n')
        this._fill_slot(2, key_name.charAt(0));
      else
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

