var English = new Class({

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

  process_input: function(key, sink) {
    var dom_key = $('#key_' + key);
    var input = $('span', dom_key).text();

    var buffer = $('#buffer');
    if (input == ' ') {
      sink(buffer.val());
      buffer.val('');
    } else {
      buffer.val(buffer.val() + input);
    }

  },

  process_backspace: function() {
    var buffer = $('#buffer');
    var t = buffer.val();
    if (t.length > 0) {
      t = t.slice(0, -1);
      buffer.val(t);
    }
  },

  process_escape: function() {
    $('#buffer').val('');
    $('#output').val('');
  }

});
