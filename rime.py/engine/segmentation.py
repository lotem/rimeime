# -*- coding: utf-8 -*-
# vim:set et sts=4 sw=4:

import re

class Segmentor(object):

    def __init__(self, schema, sa):
        self.__sa = sa
        self.__max_keyword_length = int(schema.get_config_value(u'MaxKeywordLength') or u'7')
        self.__delimiter = schema.get_config_char_sequence(u'Delimiter') or u' '
        get_rules = lambda f, key: [f(r.split()) for r in schema.get_config_list(key)]
        compile_repl_pattern = lambda x: (re.compile(x[0]), x[1])
        self.__split_rules = get_rules(compile_repl_pattern, u'SplitRule')
        self.__divide_rules = get_rules(compile_repl_pattern, u'DivideRule')

    def __is_keyword(self, k):
        return k in self.__sa.spelling_map

    def __translate_keyword(self, k):
        s = self.__sa.spelling_map
        if k in s:
            return s[k]
        else:
            return k

    def segmentation(self, input_string):
        n = len(input_string)
        m = 0
        a = [[None] * j for j in range(n + 1)]
        p = []
        q = [0]
        def allow_divide(i, j, s):
            flag = True
            for k in p:
                if not a[j][k]:
                    if flag and a[i][k]:
                        return True
                    else:
                        continue
                lw = u''.join(input_string[k:j])
                for r in self.__divide_rules:
                    m = r[0].search(lw)
                    if m and r[0].sub(r[1], lw, 1) == s:
                        return True
                flag = False
            return False
        while q:
            i = q.pop(0)
            if i == n:
                p.append(i)
                break
            # TODO: implement split rules
            ok = False
            beyond_delimiter = False
            for j in range(i + 1, n + 1):
                if beyond_delimiter:
                    break
                s = u''.join(input_string[i:j])
                if len (s) > self.__max_keyword_length:
                    break
                ##print j, s
                if not self.__is_keyword(s):
                    continue
                if j < n and input_string[j] in self.__delimiter:
                    t = j + 1
                    beyond_delimiter = True
                else:
                    t = j
                ##print i, t, s
                if t not in q:
                    q.append(t)
                    m = max(m, t)
                elif not allow_divide(i, t, s):
                    continue
                a[t][i] = self.__translate_keyword(s)
                ok = True
            if ok:
                p.append(i)
            q.sort()
        if m < n:
            p.append(m)
        b = []
        d = []
        e = [[] for i in range(m + 1)]
        # path finding
        for i in reversed(p):
            ok = i == m
            for j in b:
                if i < j and a[j][i]:
                    ok = True
                    d = [k for k in d if k >= j]
                    e[i].append((j, a[j][i]))
            if ok:
                b.append(i)
                d.append(i)
            else:
                a[i] = [None for j in range(len(a[i]))]
        b.reverse()
        d.reverse()
        return m, n, b, d, e

