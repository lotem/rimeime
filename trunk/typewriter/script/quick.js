var Quick = new Class({

  layers: [
    { // lowercase
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
      green: {
        'q': '手', 'w': '田', 'e': '水', 'r': '口', 't': '廿',
        'y': '卜', 'u': '山', 'i': '戈', 'o': '人', 'p': '心',
        'a': '日', 's': '尸', 'd': '木', 'f': '火', 'g': '土',
        'h': '竹', 'j': '十', 'k': '大', 'l': '中', 
        'z': '符', 'x': '難', 'c': '金', 'v': '女', 'b': '月',
        'n': '弓', 'm': '一' 
      },
      red: {
        'space': ' '
      }
    },
    { // uppercase
      blue: {
        '1': '!', '2': '@', '3': '#', '4': '$', '5': '%',
        '6': '^', '7': '&', '8': '*', '9': '(', '0': ')' 
      },
      yellow: {
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

  LIMIT: 2,

  process_input: function(key, sink) {
    var dom_key = $('#key_' + key);
    var input = $('span', dom_key).text();

    var buffer = $('#buffer');
    if (input == ' ') {
      sink(buffer.val());
      buffer.val('');
    } else {
      var a = buffer.val().split(' ');
      if (a.length > 0 && a[a.length - 1].length == this.LIMIT)
        a.push(input);
      else
        a[a.length - 1] += input;
      buffer.val(a.join(' '));
    }

  },

  process_backspace: function() {
    var buffer = $('#buffer');
    var t = buffer.val();
    if (t.length > 0) {
      t = t.slice(0, -1);
      if (t.charAt(t.length - 1) == ' ')
        t = t.slice(0, -1);
      buffer.val(t);
    }
  },

  process_escape: function() {
    $('#buffer').val('');
    $('#output').val('');
  }

});
