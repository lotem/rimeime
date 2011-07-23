/*
ā ă á à â a̍
ē ĕ é è ê e̍
ī ĭ í ì î i̍
ō ŏ ó ò ô o̍ 
ū ŭ ú ù û u̍
ȳ ў ý ỳ ŷ y̍

2=¯
3=˘
4=´
5=`
7=ˆ
8=ˈ
9=˙

a,o > e > i,u,y > n,g,k

q = ʔ 
a = ɑ
e = ɛ
r = œ
y = ø
o = ɔ
g = ŋ
h = ʰ
 */
var Foochow = new Class({

  layers: [
    {
      yellow: {
        '1': '1', '6': '6', '0': '0',
        'hyphen': '-', 'equal': '=',
        'bracketleft': '[', 'bracketright': ']',
        'semicolon': ';', 'quote': '\'', 'slash': '/', 'comma': ',', 'period': '.'
      },
      blue: {
        'backquote': '`<sub>IPA</sub>', 
        '2': '2<sup>¯</sup>', '3': '3<sup>˘</sup>', '4': '4<sup>´</sup>', '5': '5<sup>`</sup>',
        '7': '7<sup>ˆ</sup>', '8': '8<sup>ˈ</sup>', '9': '9<sup>˙</sup>'
      },
      green: {
        'q': 'q<sub>ʔ</sub>', 'w': 'w', 'e': 'e<sub>ɛ</sub>', 'r': 'r<sub>œ</sub>', 't': 't',
        'y': 'y<sub>ø</sub>', 'u': 'u', 'i': 'i', 'o': 'o<sub>ɔ</sub>', 'p': 'p',
        'a': 'a<sub>ɑ</sub>', 's': 's', 'd': 'd', 'f': 'f', 'g': 'g<sub>ŋ</sub>',
        'h': 'h<sup>ʰ</sup>', 'j': 'j', 'k': 'k', 'l': 'l', 
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
    var t = s
      .replace(/`([0-9`])/g, '{{$1}}')
      .replace(/`q/g, 'ʔ')
      .replace(/`a/g, 'ɑ')
      .replace(/`e/g, 'ɛ')
      .replace(/`r/g, 'œ')
      .replace(/`y/g, 'ø')
      .replace(/`o/g, 'ɔ')
      .replace(/`g/g, 'ŋ')
      .replace(/`h/g, 'ʰ')
      .replace(/([aoeiuy])([ngk]+)([2-57-9])/g, '$1$3$2')
      .replace(/([aoe])([iuy])([2-57-9])/g, '$1$3$2')
      .replace(/([ao])(e)([2-57-9])/g, '$1$3$2')
      .replace(/a2/g, '\u0101')
      .replace(/a3/g, '\u0103')
      .replace(/a4/g, '\u00e1')
      .replace(/a5/g, '\u00e0')
      .replace(/a7/g, '\u00e2')
      .replace(/e2/g, '\u0113')
      .replace(/e3/g, '\u0115')
      .replace(/e4/g, '\u00e9')
      .replace(/e5/g, '\u00e8')
      .replace(/e7/g, '\u00ea')
      .replace(/i2/g, '\u012b')
      .replace(/i3/g, '\u012d')
      .replace(/i4/g, '\u00ed')
      .replace(/i5/g, '\u00ec')
      .replace(/i7/g, '\u00ee')
      .replace(/o2/g, '\u014d')
      .replace(/o3/g, '\u014f')
      .replace(/o4/g, '\u00f3')
      .replace(/o5/g, '\u00f2')
      .replace(/o7/g, '\u00f4')
      .replace(/u2/g, '\u016b')
      .replace(/u3/g, '\u016d')
      .replace(/u4/g, '\u00fa')
      .replace(/u5/g, '\u00f9')
      .replace(/u7/g, '\u00fb')
      .replace(/y2/g, '\u0233')
      .replace(/y3/g, '\u045e')
      .replace(/y4/g, '\u00fd')
      .replace(/y5/g, '\u1ef3')
      .replace(/y7/g, '\u0177')
      .replace(/([aoeiuy])8/g, '$1\u030d')
      .replace(/([aoeiuy])9/g, '$1\u0307')
      .replace(/{{(.)}}/g, '$1')
      ;
    return t;
  },

  process_input: function(key, sink) {
    var dom_key = $('#key_' + key);
    var input = $('span', dom_key).text();

    if (input == ' ') {
      sink(this._format(this._preedit));
      this._preedit = '';
    } else if (input.length > 0) {
      this._preedit += input.slice(0, 1);
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
