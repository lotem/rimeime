var LmzV0 = new Class({

  key_map: {
    blue: {
      '5': '5', '6': '6', '7': '7', '8': '8', '9': '9', '0': '0',
      'backquote': '`', 'hyphen': '-', 'equal': '=',
      'bracketleft': '[', 'bracketright': ']', 'quote': '\''
    },
    yellow: {
      '1': '1', '2': '2', '3': '3', '4': '4', 
      'slash': 'ˊ', 'semicolon': 'ˋ', 'comma': 'ˆ', 'period': 'ˇ'/*'¨'*/
    },
    green: {
      'q': 'q', 'w': 'w', 'e': 'e', 'r': 'r', 't': 't',
      'y': 'y', 'u': 'u', 'i': 'i', 'o': 'o', 'p': 'p',
      'a': 'a', 's': 's', 'd': 'd', 'f': 'f', 'g': 'g',
      'h': 'h', 'j': 'j', 'k': 'k', 'l': 'l', 
      'z': 'z', 'x': 'x', 'c': 'c', 'v': 'v', 'b': 'b',
      'n': 'n', 'm': 'm' 
    },
    red: {
      'space': ' '
    }
  },

  _preedit: '',
  
  _update_preedit: function() {
    $('#buffer').val(this._format(this._preedit));
  },

  _format: function(s) {
    var t = '';
    while (s != t) {
      t = s;
      s = t
        .replace(/^\u02ca$/, '/')
        .replace(/^\u02cb$/, ';')
        .replace(/^\u02c6$/, ',')
        .replace(/^\u02c7$/, '.')
        .replace(/^\u02c7{3}$/, '...')
        .replace(/([aoeiuyw])h5/g, '$1h1')
        .replace(/([aoeiuyw])h6/g, '$1h2')
        .replace(/([a-z])\u02ca/g, '$11')
        .replace(/([a-z])\u02cb/g, '$12')
        .replace(/([a-z])\u02c6/g, '$13')
        .replace(/([a-z])\u02c7/g, '$14')
        //.replace(/([a-z])\u00a8/g, '$14')
        .replace(/([aoeiuy])([ptkhwlmn]|ng)([1-4])/g, '$1$3$2')
        .replace(/([aoe])([iu])([1-4])/g, '$1$3$2')
        .replace(/([aoe])([aoe]+)([1-4])/g, '$1$3$2')
        .replace(/a1/g, '\u00e1')
        .replace(/a2/g, '\u00e0')
        .replace(/a3/g, '\u00e2')
        .replace(/a4/g, '\u01ce')
        //.replace(/a4/g, '\u00e4')
        .replace(/e1/g, '\u00e9')
        .replace(/e2/g, '\u00e8')
        .replace(/e3/g, '\u00ea')
        .replace(/e4/g, '\u011b')
        //.replace(/e4/g, '\u00eb')
        .replace(/i1/g, '\u00ed')
        .replace(/i2/g, '\u00ec')
        .replace(/i3/g, '\u00ee')
        .replace(/i4/g, '\u01d0')
        //.replace(/i4/g, '\u00ef')
        .replace(/o1/g, '\u00f3')
        .replace(/o2/g, '\u00f2')
        .replace(/o3/g, '\u00f4')
        .replace(/o4/g, '\u01d2')
        //.replace(/o4/g, '\u00f6')
        .replace(/u1/g, '\u00fa')
        .replace(/u2/g, '\u00f9')
        .replace(/u3/g, '\u00fb')
        .replace(/u4/g, '\u01d4')
        //.replace(/u4/g, '\u00fc')
        .replace(/y1/g, '\u00fd')
        .replace(/y2/g, '\u1ef3')
        .replace(/y3/g, '\u0177')
        .replace(/y4/g, 'y\u02c7')
        //.replace(/y4/g, '\u00ff')  // work-around
        .replace(/w1/g, '\u1e83')
        .replace(/w2/g, '\u1e81')
        .replace(/w3/g, '\u0175')
        .replace(/w4/g, 'w\u02c7')
        //.replace(/w4/g, '\u1e85')  // work-around
        /*
        .replace(/([aoeiuyw])1/g, '\u0301$1')
        .replace(/([aoeiuyw])2/g, '\u0300$1')
        .replace(/([aoeiuyw])3/g, '\u0302$1')
        .replace(/([aoeiuyw])4/g, '\u030c$1')
        //.replace(/([aoeiuyw])4/g, '\u0308$1')
        .replace(/([\u0300-\u030f])i/g, '$1\u0131')
        */
        ;
    }
    return s;
  },

  process_input: function(key, sink) {
    var dom_key = $('#key_' + key);
    var input = $('span', dom_key).text();

    if (input == ' ') {
      sink(this._format(this._preedit));
      this._preedit = '';
    } else {
      this._preedit += input;
    }
    this._update_preedit();
  },

  process_backspace: function() {
    if (this._preedit.length > 0) {
      this._preedit = this._preedit.slice(0, -1);
    }
    this._update_preedit();
  },

  process_escape: function() {
    this._preedit = '';
    $('#buffer').val('');
    $('#output').val('');
  }

});
