var ZimeCombo = Class.extend(Combo, {
    key_map: {
        red:    { 'b': 'p', 'v': '<sub>m</sub><sup>v</sup>b', 
                  'c': '<sub>zh</sub>f<sub>m</sub>', 'x': 'z<sup>v</sup><sub>zh</sub>', 
                  't': 't', 'r': '<sub>n</sub>d', 
                  'e': '<sub>ch</sub>l<sub>n</sub>', 'w': 'c<sub>ch</sub>',
                  'g': 'k<sup>q</sup>', 'f': '<sub>ng</sub><sup>rh</sup>g<sup>j</sup>', 
                  'd': '<sub>sh</sub>h<sup>x</sup><sub>ng</sub>', 's': 's<sup>rh</sup><sub>sh</sub>' },
        blue:   { 'y': 'ue', 'h': 'ua', 'n': 'uo',
                  'u': 'e', 'j': 'a', 'm': 'u',
                  //'i': '&#x026a;<sub>ou</sub>', 'o': '<sub>ou</sub>&#x028a;', 'p': 'el',
                  'i': 'i<sub>ou</sub>', 'o': '<sub>ou</sub>o', 'p': 'el',
                  'k': 'n', 'l': 'g' },
        yellow: { 'q': '-', 'a': '-', 'z': '-', 
                  //'1': '1', '2': '2', '3': '3', '4': '4', '5': '5', 
                  //'6': '6', '7': '7', '8': '8', '9': '9', '0': '0', 
                  'semicolon': ';',
                  'comma': ',', 'period': '.', 'slash': '/' },
        green:  { 'space': 'y' }
    },

    key_order: 'g t b f r v s w x d e c space h y n m j u i o k comma l period p'.split(' '),

    key_value: { 
        'b': 'p', 'v': 'b', 'c': 'f', 'x': 'z', 
        't': 't', 'r': 'd', 'e': 'l', 'w': 'c', 
        'g': 'k', 'f': 'g', 'd': 'h', 's': 's', 
        'space': 'y',
        'h': 'ua', 'y': 'ue', 'n': 'uo', 
        'm': 'u', 'j': 'a', 'u': 'e', 
        'i': 'i', 'o': 'o', 'p': 'el', 
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
            .replace(/[ae]i?o$/, "au")
            .replace(/io$/, "ou")
            .replace(/^bf/, "m")
            .replace(/^dl/, "n")
            .replace(/^gh/, "ng")
            .replace(/^gsh?/, "rh")
            .replace(/^bzf?/, "v")
            .replace(/^zf/, "zh")
            .replace(/^cl/, "ch")
            .replace(/^([bpmfv])$/, "$1u")
            .replace(/^([dtnl])$/, "$1i")
            .replace(/^([gkh]|ng)$/, "$1o")
            .replace(/^([zcsr]h?)y?$/, "$1")
            .replace(/yi?/, "i")
            .replace(/^gi/, "ji")
            .replace(/^ki/, "qi")
            .replace(/^ngi/, "gni")
            .replace(/^hi/, "xi")
            .replace(/^i([aoeu])/, "y$1")
            .replace(/^i/, "yi")
            .replace(/^u([aoe])/, "w$1")
            .replace(/^u/, "wu")
            .replace(/^([jqx]|gn)i([aeou])/, "$1$2")
            .replace(/^([zcsr]h?)$/, "$1y")
            .replace(/ue([ni])$/, "u$1")
            .replace(/(^|[gkhzcsr])o$/, "$1eo")
            //.replace(/([jqxyi])uo$/, "$1o")
        ;

        return py;
    },

    py2pm: function (py) {
        var pm = py
            //.replace(/([jqxyi])o$/, "$1uo")
            .replace(/^ji?/, "gi")
            .replace(/^qi?/, "ki")
            .replace(/^gni?/, "ngi")
            .replace(/^xi?/, "hi")

            .replace(/^zh/, "zf")
            .replace(/^ch/, "cl")
            .replace(/^rh?/, "gs")
            .replace(/^v/, "bz")
            .replace(/^ng/, "gh")
            .replace(/^n/, "dl")
            .replace(/^m/, "bf")

            .replace(/^yi?/, "i")
            .replace(/^wu?/, "u")

            .replace(/i(.)/, "y$1")

            .replace(/eo$/, "o")
            .replace(/au$/, "ao")
            .replace(/ou$/, "io")
            .replace(/ui$/, "uei")
            .replace(/en/, "n")
            //.replace(/ng$/, "g")

            .split('').join('-')

            .replace(/u-([aoe])/, "u$1")
            .replace(/^e-l$/, "el")
            .replace(/(.)g$/, "$1g'")
        ;

        return pm;
    }

});
