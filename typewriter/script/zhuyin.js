var Zhuyin = new Class({

  key_map: {
    blue:    { '1': 'ㄅ', 'q': 'ㄆ', 'a': 'ㄇ', 'z': 'ㄈ', 
               '2': 'ㄉ', 'w': 'ㄊ', 's': 'ㄋ', 'x': 'ㄌ',
               'e': 'ㄍ', 'd': 'ㄎ', 'c': 'ㄏ',
               'r': 'ㄐ', 'f': 'ㄑ', 'v': 'ㄒ',
               '5': 'ㄓ', 't': 'ㄔ', 'g': 'ㄕ', 'b': 'ㄖ',
               'y': 'ㄗ', 'h': 'ㄘ', 'n': 'ㄙ' },
    yellow: { 'u': 'ㄧ', 'j': 'ㄨ', 'm': 'ㄩ' },
    green:  { '8': 'ㄚ', 'i': 'ㄛ', 'k': 'ㄜ', 'comma': 'ㄝ',
               '9': 'ㄞ', 'o': 'ㄟ', 'l': 'ㄠ', 'period': 'ㄡ',
               '0': 'ㄢ', 'p': 'ㄣ', 'semicolon': 'ㄤ', 'slash': 'ㄥ',
               'hyphen': 'ㄦ' },
    red:    { 'space': '', '3': 'ˇ', '4': 'ˋ', '6': 'ˊ', '7': '˙' }
  },

  buffer_size: 3,

  _slot: ['', '', '', ''],

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
    var input = $('span', dom_key).text();

    // shengdiau
    if (dom_key.hasClass('red')) {
      if (key != 'space')
        this._fill_slot(3, input);

      var s = this._slot.join('');
      sink(s);
      this._clear_buffer();
    }

    // shengmu
    if (dom_key.hasClass('blue'))
      this._fill_slot(0, input);
    // jaiyin
    else if (dom_key.hasClass('yellow'))
      this._fill_slot(1, input);
    // yunmu
    else if (dom_key.hasClass('green'))
      this._fill_slot(2, input);
      
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

