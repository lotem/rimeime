var Canton = new Class({

  layers: [
    {
      yellow: {
        '7': '7', '8': '8', '9': '9', '0': '0',
        'backquote': '`', 'hyphen': '-', 'equal': '=',
        'bracketleft': '[', 'bracketright': ']'
      },
      blue: {
        '1': '1', '2': '2', '3': '3', '4': '4', '5': '5', '6': '6',
        'semicolon': '¨', 'quote': '´', 'slash': '`', 'comma': '˜', 'period': 'ˆ'
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
    { // uppercase
      yellow: {
        '1': '!', '2': '@', '3': '#', '4': '$', '5': '%',
        '6': '^', '7': '&', '8': '*', '9': '(', '0': ')',
        'backquote': '~', 'hyphen': '_', 'equal': '+',
        'bracketleft': '{', 'bracketright': '}',
        'semicolon': ':', 'quote': '\"', 
        'comma': '<', 'period': '>', 'slash': '?'
      },
      green: {
        'q': 'Q', 'w': 'W', 'e': 'E', 'r': 'R', 't': 'T',
        'y': 'Y', 'u': 'U', 'i': 'I', 'o': 'O', 'p': 'P',
        'a': 'A', 's': 'S', 'd': 'D', 'f': 'F', 'g': 'G',
        'h': 'H', 'j': 'J', 'k': 'K', 'l': 'L', 
        'z': 'Z', 'x': 'X', 'c': 'C', 'v': 'V', 'b': 'B',
        'n': 'N', 'm': 'M' 
      },
      red: {
        'space': ' '
      }
    }
  ],    

  _preedit: '',
  
  _update_preedit: function() {
    $('#buffer').val(this._format(this._preedit));
  },

  _format: function(s) {
    var t = '';
    while (s != t) {
      t = s;
      s = t
        .replace(/^\u00a8$/, ';')
        .replace(/^\u02dc$/, ',')
        .replace(/^\u02c6$/, '.')
        .replace(/^\u02c6{2}$/, '..')
        .replace(/^\u02c6{3}$/, '...')
        .replace(/^\u00b4$/, '\'')
        .replace(/^\u0060$/, '/')
        .replace(/([a-z])\u00a8/g, '$11')
        .replace(/([a-z])\u02dc/g, '$12')
        .replace(/([a-z])\u02c6/g, '$13')
        .replace(/([a-z])\u00b4/g, '$15')
        .replace(/([a-z])\u0060/g, '$16')
        .replace(/([aoeiuy])([mnptkbdgh]+)([1-6])/g, '$1$3$2')
        .replace(/([aoiu])([iuyw])([1-6])/g, '$1$3$2')
        .replace(/(e)([iyw])([1-6])/g, '$1$3$2')
        .replace(/(a)(a+)([1-6])/g, '$1$3$2')
        .replace(/([ao])(o+)([1-6])/g, '$1$3$2')
        .replace(/([aoe])(e+)([1-6])/g, '$1$3$2')
        .replace(/a1/g, '\u00e4')
        .replace(/a2/g, '\u00e3')
        .replace(/a3/g, '\u00e2')
        .replace(/a5/g, '\u00e1')
        .replace(/a6/g, '\u00e0')
        .replace(/e1/g, '\u00eb')
        .replace(/e2/g, '\u1ebd')
        .replace(/e3/g, '\u00ea')
        .replace(/e5/g, '\u00e9')
        .replace(/e6/g, '\u00e8')
        .replace(/i1/g, '\u00ef')
        .replace(/i2/g, '\u0129')
        .replace(/i3/g, '\u00ee')
        .replace(/i5/g, '\u00ed')
        .replace(/i6/g, '\u00ec')
        .replace(/o1/g, '\u00f6')
        .replace(/o2/g, '\u00f5')
        .replace(/o3/g, '\u00f4')
        .replace(/o5/g, '\u00f3')
        .replace(/o6/g, '\u00f2')
        .replace(/u1/g, '\u00fc')
        .replace(/u2/g, '\u0169')
        .replace(/u3/g, '\u00fb')
        .replace(/u5/g, '\u00fa')
        .replace(/u6/g, '\u00f9')
        .replace(/y1/g, '\u00ff')
        .replace(/y2/g, '\u1ef9')
        .replace(/y3/g, '\u0177')
        .replace(/y5/g, '\u00fd')
        .replace(/y6/g, '\u1ef3')
        .replace(/m5/g, '\u1e3f')
        .replace(/n(g?)2/g, '\u00f1$1')
        .replace(/n(g?)5/g, '\u0144$1')
        .replace(/n(g?)6/g, '\u01f9$1')
        /*
        .replace(/([aoeiuymn]|ng)1/g, '$1\u00a8')
        .replace(/([aoeiuymn]|ng)2/g, '$1\u02dc')
        .replace(/([aoeiuymn]|ng)3/g, '$1\u02c6')
        .replace(/([aoeiuymn]|ng)4/g, '$1')
        .replace(/([aoeiuymn]|ng)5/g, '$1\u02ca')
        .replace(/([aoeiuymn]|ng)6/g, '$1\u02cb')
        .replace(/i([\u0300-\u030f])/g, '\u0131$1')
        */
        .replace(/([aoeiuymn]|ng)1/g, '\u0308$1')
        .replace(/([aoeiuymn]|ng)2/g, '\u0303$1')
        .replace(/([aoeiuymn]|ng)3/g, '\u0302$1')
        .replace(/([aoeiuymn]|ng)4/g, '$1')
        .replace(/([aoeiuymn]|ng)5/g, '\u0301$1')
        .replace(/([aoeiuymn]|ng)6/g, '\u0300$1')
        .replace(/([\u0300-\u030f])i/g, '$1\u0131')
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
