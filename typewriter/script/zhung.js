var Zhung = new Class({

  layers: [
    {
      yellow: {
        '5': '5', '6': '6', '7': '7', '8': '8', '9': '9', 
        'backquote': '`', 'hyphen': '-', 'equal': '=',
        'bracketleft': '[', 'bracketright': ']', 'quote': '\''
      },
      blue: {
        '1': '1', '2': '2', '3': '3', '4': '4', '0': '0',
        'semicolon': '¨', 'comma': 'ˆ', 'period': '`', 'slash': '´'
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
        .replace(/^\u02c6$/, ',')
        .replace(/^\u0060$/, '.')
        .replace(/^\u0060{2}$/, '..')
        .replace(/^\u0060{3}$/, '...')
        .replace(/^\u00b4$/, '/')
        .replace(/([aoeiuyw])h5/g, '$1h1')
        .replace(/([aoeiuyw])h6/g, '$1h2')
        .replace(/([a-z]+)7/g, '$10')
        .replace(/([a-z])\u02c6/g, '$12')
        .replace(/([a-z])\u00b4/g, '$13')
        .replace(/([a-z])\u0060/g, '$14')
        .replace(/([a-z])\u00a8/g, '$10')
        .replace(/([aoeiuy])([ptkhwlmn]|ng)([1-40])/g, '$1$3$2')
        .replace(/([aoe])([iu])([1-40])/g, '$1$3$2')
        .replace(/([aoe])([aoe]+)([1-40])/g, '$1$3$2')
        .replace(/a2/g, '\u00e2')
        .replace(/a3/g, '\u00e1')
        .replace(/a4/g, '\u00e0')
        .replace(/a0/g, '\u00e4')
        .replace(/e2/g, '\u00ea')
        .replace(/e3/g, '\u00e9')
        .replace(/e4/g, '\u00e8')
        .replace(/e0/g, '\u00eb')
        .replace(/i2/g, '\u00ee')
        .replace(/i3/g, '\u00ed')
        .replace(/i4/g, '\u00ec')
        .replace(/i0/g, '\u00ef')
        .replace(/o2/g, '\u00f4')
        .replace(/o3/g, '\u00f3')
        .replace(/o4/g, '\u00f2')
        .replace(/o0/g, '\u00f6')
        .replace(/u2/g, '\u00fb')
        .replace(/u3/g, '\u00fa')
        .replace(/u4/g, '\u00f9')
        .replace(/u0/g, '\u00fc')
        .replace(/y2/g, '\u0177')
        .replace(/y3/g, '\u00fd')
        .replace(/y4/g, '\u1ef3')
        .replace(/y0/g, '\u00ff')
        .replace(/w2/g, '\u0175')
        .replace(/w3/g, '\u1e83')
        .replace(/w4/g, '\u1e81')
        .replace(/w0/g, '\u1e85')
        .replace(/([aoeiuyw])1/g, '$1')
        /*
        .replace(/([aoeiuyw])2/g, '\u0302$1')
        .replace(/([aoeiuyw])3/g, '\u0301$1')
        .replace(/([aoeiuyw])4/g, '\u0300$1')
        .replace(/([aoeiuyw])0/g, '\u0308$1')
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
