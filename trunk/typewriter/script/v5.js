var V5 = Class.extend(Combo, {
    key_map: {
        blue:   { 'v': '<sub>m</sub>b', 'c': 'p<sub>m</sub>', 'x': 'f', 
                  'r': '<sub>n</sub>d', 'e': 't<sub>n</sub>', 'w': 'l',
                  'f': '<sub>r</sub>z<sup>zh</sup>', 'd': 'c<sup>ch</sup><sub>r</sub>', 's': 's<sup>sh</sup>',
                  'g': 'g<sup>j</sup>', 't': 'k<sup>q</sup>', 'b': 'h<sup>x</sup>' },
        green:  { 'y': 'ue', 'h': 'ua', 'n': 'uo',
                  'u': 'e', 'j': 'a', 'm': 'u',
                  'i': 'i<sub>ou</sub>', 'o': '<sub>ou</sub>o', 'p': 'er',
                  'k': 'n', 'l': 'g' },
        yellow: { 'q': '-', 'a': '-', 'z': '-', 
                  //'1': '1', '2': '2', '3': '3', '4': '4', '5': '5', 
                  //'6': '6', '7': '7', '8': '8', '9': '9', '0': '0', 
                  'semicolon': ';',
                  'comma': ',', 'period': '.', 'slash': '/' },
        red:    { 'space': '<sup>-h</sup>y' }
    },

    key_order: 'v c x r e w f d s g t b space h y n m j u i o k comma l period p'.split(' '),

    key_value: { 
        'v': 'b', 'c': 'p', 'x': 'f', 
        'r': 'd', 'e': 't', 'w': 'l', 
        'f': 'z', 'd': 'c', 's': 's', 
        'g': 'g', 't': 'k', 'b': 'h', 
        'space': 'y',
        'h': 'ua', 'y': 'ue', 'n': 'uo', 
        'm': 'u', 'j': 'a', 'u': 'e', 
        'i': 'i', 'o': 'o', 'p': 'er', 
        'k': 'n', 'l': 'g\'', 'comma': ',', 'period': '.'
    },

    // pinma to pinyin translation
    pm2py: function (pm) {
        var py = pm
            .replace(/^y$/, "")
            .replace(/^,$/, "COMMA")
            .replace(/^\.$/, "PERIOD")
            .replace(/,/, "n")
            .replace(/\./, "g'")
            .replace(/^COMMA$/, ",")
            .replace(/^PERIOD$/, ".")
            .replace(/[ni]?g'$/, "ng")
            .replace(/^n/, "en")
            .replace(/[ae]i?o$/, "ao")
            .replace(/io$/, "ou")
            .replace(/^bp/, "m")
            .replace(/^dt/, "n")
            .replace(/^zc/, "r")
            .replace(/^([zcs])y/, "$1h")
            .replace(/^ry/, "r")
            .replace(/^([bpfv])$/, "$1u")
            .replace(/^([mdtnlgkh])$/, "$1e")
            .replace(/^([zcs]h?|r)$/, "$1i")
            .replace(/yi?/, "i")
            .replace(/^gi/, "ji")
            .replace(/^ki/, "qi")
            .replace(/^hi/, "xi")
            .replace(/^i([aoeu])/, "y$1")
            .replace(/^i/, "yi")
            .replace(/^u([aoe])/, "w$1")
            .replace(/^u/, "wu")
            .replace(/^wu([ni])/, "we$1")
            .replace(/ue([ni])$/, "u$1")
            .replace(/uo?ng$/, "ong")
            .replace(/^([jqx])iu/, "$1u")
            .replace(/iou$/, "iu")
            .replace(/([bpmfvdtnlgkhjqxzcsr])n/, "$1en")
            .replace(/^([bpmfvy])uo$/, "$1o")
        ;

        return py;
    },

    // pinyin to pinma translation
    py2pm: function (py) {
        var pm = py
            .replace(/^ng$/, "eng")
            .replace(/^([nl])v/, "$1yu")
            .replace(/^([nl])ue$/, "$1yue")

            .replace(/ui$/, "uei")
            .replace(/iu$/, "iou")

            .replace(/^([zcs])h/, "$1y")
            
            .replace(/^r/, "zc")
            .replace(/^n/, "dt")
            .replace(/^m/, "bp")

            .replace(/^ji?/, "gi")
            .replace(/^qi?/, "ki")
            .replace(/^xi?/, "hi")

            .replace(/^yi?/, "i")
            .replace(/^wu?/, "u")

            .replace(/i(.)/, "y$1")

            .replace(/ou$/, "io")
            .replace(/ong$/, "ung")

            .replace(/en/, "n")

            .replace(/([zcs]y?)i$/, "$1")
            .replace(/([dtlgkh]|bp)e$/, "$1")
            .replace(/([bpf])u$/, "$1")

            .split('').join('-')

            .replace(/u-([aoe])/, "u$1")
            .replace(/^e-r$/, "er")

            .replace(/g$/, "g'")
        ;

        return pm;
    }

});
