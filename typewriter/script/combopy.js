var Combopy = Class.extend(Combo, {
    key_map: {
        blue:   { 'b': 'p', 'v': '<sub>m</sub>b', 
                  'c': '<sub>zh</sub>f<sub>m</sub>', 'x': 'z<sub>zh</sub>', 
                  't': 't', 'r': '<sub>n</sub>d', 
                  'e': '<sub>ch</sub>l<sub>n</sub>', 'w': 'c<sub>ch</sub>',
                  'g': 'k<sup>q</sup>', 'f': '<sub>r</sub>g<sup>j</sup>', 
                  'd': '<sub>sh</sub>h<sup>x</sup><sub>r</sub>', 's': 's<sub>sh</sub>' },
        red:    { 'n': 'er', 'u': 'u', 'j': 'i', 'm': 'ü' },
        green:  { 'i': '\u026a<sub>ei</sub>', 'o': '<sub>ei</sub>o',
                  'k': 'n<sub>ng</sub>', 'l': '<sub>ng</sub>e',
                  'comma': ',<sup>\u028a</sup><sub>ou</sub>', 'period': '<sub>ou</sub>.',
                  'space': 'a' },
        yellow: { 'q': '-', 'a': '-', 'z': '-', 'y': '-', 'h': '-', 'p': '-',
                  //'1': '1', '2': '2', '3': '3', '4': '4', '5': '5', 
                  //'6': '6', '7': '7', '8': '8', '9': '9', '0': '0', 
                  'semicolon': ';', 'slash': '/' }
    },

    key_order: 's w x f r v g t b d e c n j m u space k i comma l o period'.split(' '),

    key_value: { 
        'b': 'p', 'v': 'b', 'c': 'f', 'x': 'z', 
        't': 't', 'r': 'd', 'e': 'l', 'w': 'c', 
        'g': 'k', 'f': 'g', 'd': 'h', 's': 's', 
        'space': 'a',
        'n': 'er', 'j': 'i', 'u': 'u', 'm': 'ü', 
        'i': 'y', 'o': 'o', 'k': 'n', 'l': 'e', 'comma': 'w', 'period': '.'
    },

    pm2py: function (pm) {
        var py = pm
            .replace(/^a$/, "")
            .replace(/^w$/, "COMMA")
            .replace(/^\.$/, "PERIOD")
            .replace(/\./, "e")
            .replace(/^COMMA$/, ",")
            .replace(/^PERIOD$/, ".")
            .replace(/([aoeiuü])ne$/, "$1ng")
            .replace(/ne$/, "eng")
            .replace(/n$/, "en")
            .replace(/([aoeiuü])en$/, "$1n")
            .replace(/u(a?)yo$/, "u$1ng")
            .replace(/üwe$/, "iung")
            .replace(/ü(a?)w$/, "i$1w")
            .replace(/ay$/, "ai")
            .replace(/yo$/, "ei")
            .replace(/aw$/, "ao")
            .replace(/we?$/, "ou")
            .replace(/y/, "i")
            .replace(/^ae$/, "a")
            .replace(/^bf/, "m")
            .replace(/^dl/, "n")
            .replace(/^gh/, "r")
            .replace(/^sgh?/, "r")
            .replace(/^zbf?/, "w")
            .replace(/^zf/, "zh")
            .replace(/^cl/, "ch")
            //.replace(/^sh/, "sh")
            .replace(/^([bpfw])$/, "$1u")
            .replace(/^([mdtnlgkh])$/, "$1e")
            .replace(/^([zcs]h?|r)i$/, "$1")
            .replace(/yi?/, "i")
            .replace(/^[gz]i/, "ji")
            .replace(/^[kc]i/, "qi")
            .replace(/^[hs]i/, "xi")
            .replace(/^[gz]ü/, "ju")
            .replace(/^[kc]ü/, "qu")
            .replace(/^[hs]ü/, "xu")
            .replace(/^([zcs]h?|r)$/, "$1i")
            .replace(/^i([aoeu])/, "y$1")
            .replace(/^i/, "yi")
            .replace(/^u([aoe])/, "w$1")
            .replace(/^u/, "wu")
            .replace(/ue([ni])/, "u$1")
            .replace(/^wu([ni])/, "we$1")
            .replace(/ung$/, "ong")
            .replace(/^ü/, "yu")
            //.replace(/üe/, "ue")
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
            .replace(/^([nl])ue$/, "$1ve")

            .replace(/^j[uv]/, "gv")
            .replace(/^q[uv]/, "kv")
            .replace(/^x[uv]/, "hv")
            .replace(/^ji?/, "gi")
            .replace(/^qi?/, "ki")
            .replace(/^xi?/, "hi")

            .replace(/^zh/, "zf")
            .replace(/^ch/, "cl")
            //.replace(/^sh/, "sh")
            .replace(/^r/, "gh")
            .replace(/^n/, "dl")
            .replace(/^m/, "bf")

            .replace(/^yu/, "iu")
            .replace(/^yi?/, "i")
            .replace(/^wu?/, "u")

            .replace(/([au])i$/, "$1y")
            .replace(/ei$/, "yo")
            .replace(/iao$/, "vaw")
            .replace(/io?u$/, "vw")
            .replace(/iong$/, "vw.")
            .replace(/ong$/, "uyo")
            .replace(/uang$/, "uayo")
            .replace(/ao$/, "aw")
            .replace(/ou$/, "w.")
            .replace(/en/, "n")
            .replace(/ng/, "ne")
            .replace(/iu|v/, "ü")
            .replace(/^a$/, "ae")

            .split('').join('-')

            .replace(/^e-r$/, "er")
        ;

        return pm;
    }

});
