var V6 = Class.extend(Combo, {
    key_map: {
        blue:   { 'b': 'p', 'v': '<sub>m</sub>b', 
                  'c': '<sub>zh</sub>f<sub>m</sub>', 'x': 'z<sub>zh</sub>', 
                  't': 't', 'r': '<sub>n</sub>d', 
                  'e': '<sub>ch</sub>l<sub>n</sub>', 'w': 'c<sub>ch</sub>',
                  'g': 'k<sup>q</sup>', 'f': '<sub>r</sub>g<sup>j</sup>', 
                  'd': '<sub>sh</sub>h<sup>x</sup><sub>r</sub>', 's': 's<sub>sh</sub>' },
        green:  { 'y': 'ue', 'h': 'ua', 'n': 'uo',
                  'u': 'e', 'j': 'a', 'm': 'u',
                  'i': 'i<sub>ou</sub>', 'o': '<sub>ou</sub>o', 'p': 'er',
                  'k': 'n', 'l': 'g' },
        yellow: { 'q': '-', 'a': '-', 'z': '-', 
                  //'1': '1', '2': '2', '3': '3', '4': '4', '5': '5', 
                  //'6': '6', '7': '7', '8': '8', '9': '9', '0': '0', 
                  'semicolon': ';',
                  'comma': ',', 'period': '.', 'slash': '/' },
        red:    { 'space': 'y' }
    },

    key_order: 'g t b f r v s w x d e c space h y n m j u i o k comma l period p'.split(' '),

    key_value: { 
        'b': 'p', 'v': 'b', 'c': 'f', 'x': 'z', 
        't': 't', 'r': 'd', 'e': 'l', 'w': 'c', 
        'g': 'k', 'f': 'g', 'd': 'h', 's': 's', 
        'space': 'y',
        'h': 'ua', 'y': 'ue', 'n': 'uo', 
        'm': 'u', 'j': 'a', 'u': 'e', 
        'i': 'i', 'o': 'o', 'p': 'er', 
        'k': 'n', 'l': 'g\'', 'comma': ',', 'period': '.'
    },

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
            .replace(/(^|[^aoeiuy])n/, "$1en")
            .replace(/ue?([ni])$/, "u$1")
            .replace(/[ae]i?o$/, "ao")
            .replace(/io$/, "ou")
            .replace(/^bf/, "m")
            .replace(/^dl/, "n")
            .replace(/^gh/, "r")
            .replace(/^gsh?/, "r")
            .replace(/^bzf?/, "w")
            .replace(/^zf/, "zh")
            .replace(/^cl/, "ch")
            .replace(/^([bpfw])$/, "$1u")
            .replace(/^([mdtnlgkh])$/, "$1e")
            .replace(/^([zcs]h?|r)i$/, "$1")
            .replace(/yi?/, "i")
            .replace(/^[gz]i/, "ji")
            .replace(/^[kc]i/, "qi")
            .replace(/^[hs]i/, "xi")
            .replace(/^([zcs]h?|r)$/, "$1i")
            .replace(/^i([aoeu])/, "y$1")
            .replace(/^i/, "yi")
            .replace(/^u([aoe])/, "w$1")
            .replace(/^u/, "wu")
            .replace(/ue([ni])/, "u$1")
            .replace(/^wu([ni])/, "we$1")
            .replace(/ung$/, "ong")
            .replace(/^([jqx])iu/, "$1u")
            .replace(/iue/, "ue")
            .replace(/iu/, "v")
            .replace(/iou$/, "iu")
        ;

        return py;
    },

    py2pm: function (py) {
        var pm = py
            .replace(/^([bpf])u$/, "$1")
            .replace(/^([mdtnlgkh])e$/, "$1")
            .replace(/^([zcs]h?|r)i$/, "$1")

            .replace(/^ng$/, "eng")
            .replace(/^([nl])ue$/, "$1iue")
            .replace(/^([nl])v$/, "$1iu")

            .replace(/^ji?/, "gi")
            .replace(/^qi?/, "ki")
            .replace(/^xi?/, "hi")

            .replace(/^zh/, "zf")
            .replace(/^ch/, "cl")
            .replace(/^r/, "gh")
            .replace(/^n/, "dl")
            .replace(/^m/, "bf")

            .replace(/^yi?/, "i")
            .replace(/^wu?/, "u")

            .replace(/i(.)/, "y$1")

            .replace(/ong$/, "ung")
            .replace(/ou$/, "io")
            .replace(/ui$/, "uei")
            .replace(/en/, "n")

            .split('').join('-')

            .replace(/u-([aoe])/, "u$1")
            .replace(/^e-r$/, "er")
            .replace(/(.)g$/, "$1g'")
        ;

        return pm;
    }

});
