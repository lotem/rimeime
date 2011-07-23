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
      'q': 'ㄔ<sup>ㄑ</sup>', 'w': 'ㄜ', 'e': 'ㄝ', 'r': 'ㄖ<sup>ˊ</sup>', 't': 'ㄊ<sup>ㄟ</sup>',
      'y': 'ㄩ', 'u': 'ㄨ', 'i': 'ㄧ', 'o': 'ㄛ', 'p': 'ㄆ<sup>ㄡ</sup>',
      'a': 'ㄚ', 's': 'ㄙ', 'd': 'ㄉ<sup>ㄞ</sup>', 'f': 'ㄈ<sup>ˆ</sup>', 'g': 'ㄍ<sup>ㄥ</sup>',
      'h': 'ㄏ<sup>˙</sup>', 'j': 'ㄓ<sup>ㄐ</sup>', 'k': 'ㄎ<sup>ㄤ</sup>', 'l': 'ㄌ<sup>ㄦ</sup>', 
      'z': 'ㄗ', 'x': 'ㄕ<sup>ㄒ</sup>', 'c': 'ㄘ', 'v': 'ㄪ<sup>ˋ</sup>', 'b': 'ㄅ<sup>ㄠ</sup>',
      'n': 'ㄋ<sup>ㄣ</sup>', 'm': 'ㄇ<sup>ㄢ</sup>' 
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
        ((key == 'space' || key == 'r' || key == 'f' || key == 'v' || key == 'h'))) {
      if (key != 'space')
        this._fill_slot(3, key_name.charAt(key_name.length - 1));
      var s = this._slot.join('');
      sink(s);
      this._clear_buffer();
    }
    // jaiyin
    else if (key == 'i' || key == 'u' || key == 'y') {
      this._fill_slot(1, key_name.charAt(0));
      if (key == 'i' || key == 'y') {
        var shengmu = this._slot[0];
        if (shengmu == 'ㄓ' || shengmu == 'ㄍ') this._fill_slot(0, 'ㄐ');
        else if (shengmu == 'ㄔ' || shengmu == 'ㄎ') this._fill_slot(0, 'ㄑ');
        else if (shengmu == 'ㄕ' || shengmu == 'ㄏ') this._fill_slot(0, 'ㄒ');
      }
    }
    // shengmu
    else if (this._slot_is_empty() && 
             key != 'a' && key != 'o' && key != 'w' && key != 'e') {
      this._fill_slot(0, key_name.charAt(0));
    }
    // yunmu
    else {
      this._fill_slot(2, key_name.length == 1 ? key_name.charAt(0) : key_name.charAt(1));
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

