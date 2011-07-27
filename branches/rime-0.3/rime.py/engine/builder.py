# -*- coding: utf-8 -*-
# vim:set et sts=4 sw=4:

import re
from math import log

from algebra import *
from segmentation import Segmentor


class Entry:

    # TODO: 用slots做性能優化

    def __init__(self, e, i, j, prob=0.0, use_count=0, next=None):
        self.e = e
        self.i = i
        self.j = j
        self.prob = prob
        self.use_count = use_count
        self.next = next

    def get_word(self):
        return self.e[0] if self.e else u''

    def get_okey(self):
        return self.e[1] if self.e else u''

    def get_eid(self):
        return self.e[2] if self.e else 0

    def get_all(self):
        w = []
        s = self
        while s:
            w.append(s)
            s = s.next
        return w

    def get_phrase(self):
        ''' 取詞組

        ZIME3.x裡，一個候選詞組可由多個詞組成，有bigram將他們連接起來
        今後，這樣的詞組不再作為候選列出
        '''
        return u''.join([e.get_word() for e in self.get_all()])

    def partof(self, other):
        ''' 判斷另一個詞／詞組是不是本詞組的一個前綴

        作用是，判斷出實際含有半截詞組的中間節點，以從候選中去除
        因為二元關係包含用戶選用的次數，若前綴與本詞組使用次數相同
        則不視其為獨立的詞條
        '''
        if self.use_count != other.use_count:
            return False
        a, b = self, other
        while a and b and a.get_eid() == b.get_eid():
            a, b = a.next, b.next
        return not a

    def __unicode__(self):
        return u'<%s %g %d (%d, %d)%s>' % \
            (self.get_word(), self.prob, self.use_count, self.i, self.j, (u' => %s' % self.next.get_phrase()) if self.next else u'')


class ContextInfo:

    # TODO: 這裡頭的一部分信息應該放到Context裡頭，另一些打包成Context.lmdata

    def __init__(self):
        self.m = 0
        self.n = 0
        self.e = []
        self.q = {}
        self.unig = {}
        self.big = {}
        self.cand = []
        self.pred = [None]
        self.last = None


class Model:

    # TODO: 可拆分成 LanguageModel, CandidateList, Builder

    PENALTY = log(1e-3)
    LIMIT = 50
    MAX_CONCAT_PHRASE = 3

    def __init__(self, schema):
        self.__max_key_length = int(schema.get_config_value(u'MaxKeyLength') or u'2')
        get_rules = lambda f, key: [f(r.split()) for r in schema.get_config_list(key)]
        compile_repl_pattern = lambda x: (re.compile(x[0]), x[1])
        mapping_rules = get_rules(compile_repl_pattern, u'MappingRule')
        fuzzy_rules = get_rules(compile_repl_pattern, u'FuzzyRule')
        spelling_rules = get_rules(compile_repl_pattern, u'SpellingRule')
        alternative_rules = get_rules(compile_repl_pattern, u'AlternativeRule')
        keywords = schema.get_db().list_keywords()
        self.__sa = SpellingAlgebra(report_errors=False)
        self.__sa.calculate(mapping_rules, 
                            fuzzy_rules, 
                            spelling_rules, 
                            alternative_rules, 
                            keywords)
        self.__segmentor = Segmentor(schema, self.__sa)
        self.__db = schema.get_db()

    def create_context_info(self):
        return ContextInfo()

    def query(self, ctx):
        m, n, b, d, e = self.__segmentor.segmentation(ctx.input)
        prev_e = ctx.info.e
        ctx.info.m = m
        ctx.info.n = n
        ctx.info.b = b
        ctx.info.d = d
        ctx.info.e = e
        # find the start position of altered input
        diff = 0
        while diff < m and diff < len(prev_e) and prev_e[diff] == e[diff]:
            diff += 1
        # clear unconfirmed selection
        i = ctx.confirmed
        s = ctx.sel
        while i > 0 and s[i - 1].j > diff:
            i -= 1
        del ctx.sel[i:]
        ctx.confirmed = i
        self.__lookup_candidates(ctx.info, diff)
        self.__calculate_sentence(ctx.info)

    def __lookup_candidates(self, info, diff):
        m = info.m
        b = info.b
        e = info.e
        c = info.cand
        unig = info.unig
        big = info.big
        total, utotal = [x + 0.1 for x in self.__db.lookup_freq_total()]
        to_prob = lambda x: log((x + 0.1) / total)
        def make_keys(i, k, length):
            if length == 0 or i == m:    
                return [(i, k)]
            keys = sum([make_keys(jw, k + [kw], length - 1) for jw, kw in e[i]], [])
            return [(i, k)] + keys
        def lookup(k):
            key = u' '.join(k)
            if key in info.q:
                return info.q[key]
            result = info.q[key] = self.__db.lookup_unigram(key)
            for x in result:
                prob = to_prob(x[3])
                unig[x[2]] = prob
            if len(k) >= min(2, self.__max_key_length):
                for x in self.__db.lookup_bigram(key):
                    if x[0] in big:
                        s = big[x[0]]
                    else:
                        s = big[x[0]] = {}
                    s[x[1]] = to_prob(x[2])
            return result
        def add_word(x, i, j):
            ##print 'add_word:', i, j, x[0], x[1]
            use_count = x[4]
            e = Entry(x, i, j, 1.0, use_count)
            if not c[i][j]:
                a = c[i][j] = []
            else:
                a = c[i][j]
            a.append(e)
        def match_key(x, i, j, k):
            if not k:
                if j > diff:
                    add_word(x, i, j)
                return
            if j == m:
                return
            for jw, kw in e[j]:
                if k[0] in self.__sa.io_map[kw]:
                    match_key(x, i, jw, k[1:])
        def judge(x, i, j):
            okey = x[1].split()
            if len(okey) <= self.__max_key_length:
                if j > diff:
                    add_word(x, i, j)
            else:
                match_key(x, i, j, okey[self.__max_key_length:])
        # clear invalidated candidates
        for i in range(diff):
            c[i][diff + 1:] = [None for j in range(diff + 1, m + 1)]
        c[diff:] = [[None for j in range(m + 1)] for i in range(diff, m + 1)]
        # last committed word goes to array index -1
        if info.last:
            last = info.last
            #print u'last: %s' % last
            c[-1][0] = [Entry(last.e, -1, 0, last.prob, last.use_count, None)]
            if not info.q:
                r = self.__db.lookup_bigram_by_entry(last)
                if r:
                    eid = last.get_eid()
                    if eid in big:
                        s = big[eid]
                    else:
                        s = big[eid] = {}
                    for x in r:
                        s[x[0]] = to_prob(x[1])
        # traverse
        for i in b:
            for jw, kw in e[i]:
                for j, k in make_keys(jw, [kw], self.__max_key_length - 1):
                    if j <= diff and len(k) < self.__max_key_length:
                        continue
                    #print 'lookup:', i, j, k
                    for x in lookup(k):
                        judge(x, i, j)

    def __calculate_sentence(self, info):
        m = info.m
        b = info.b
        c = info.cand
        f = [[None for j in range(m + 1)] for i in range(m + 1)]
        info.fraz = f
        unig = info.unig
        big = info.big
        # index m should be left empty; index -1 is reserved for the last committed word
        pred = [None for i in range(m + 1 + 1)]
        info.pred = pred
        def update_pred(i, e):
            # 用戶用過的詞優先於未用過而但概率高的詞
            used = lambda x: bool(x.use_count) and x.get_all()[-1].j == m
            pred_cmp = lambda a, b: cmp(used(a), used(b)) or cmp(a.prob, b.prob)
            if not pred[i] or pred_cmp(e, pred[i]) > 0:
                pred[i] = e
        def succ_phrases(j):
            '''returns succeeding phrases starting with position j, grouped by eid'''
            succ = dict()
            for k in range(j + 1, m + 1):
                if c[j][k]:
                    for x in c[j][k][:Model.LIMIT]:
                        eid = x.get_eid()
                        if eid in succ:
                            succ[eid].append(x)
                        else:
                            succ[eid] = [x]
                if f[j][k]:
                    for x in f[j][k]:
                        eid = x.get_eid()
                        if eid in succ:
                            succ[eid].append(x)
                        else:
                            succ[eid] = [x]
            return succ
        # traverse
        for j in reversed(b):
            succ = None
            for i in range(-1, j):
                if c[i][j]:
                    for x in c[i][j]:
                        # calculate prob
                        if i != -1:
                            x.prob = unig[x.get_eid()]
                        if j != m:
                            x.prob += pred[j].prob + Model.PENALTY
                        update_pred(i, x)
                        if j == m:
                            continue
                        # try making phrases
                        eid = x.get_eid()
                        if eid in big:
                            if succ is None:
                                succ = succ_phrases(j)
                            for v in big[eid]:
                                if v in succ:
                                    for y in succ[v]:
                                        prob = big[eid][v] - unig[v] + y.prob
                                        e = Entry(x.e, i, j, prob, min(x.use_count, y.use_count), y)
                                        #print "concat'd phrase:", unicode(e)
                                        # save phrase
                                        k = e.get_all()[-1].j
                                        if f[i][k]:
                                            f[i][k].append(e)
                                        else:
                                            f[i][k] = [e]
                                        # update pred[i] with concat'd phrases
                                        update_pred(i, e)
        # make sentences
        for i in range(m - 1, -1, -1):
            if pred[i]:
                k = i
                s = []
                while k < m:
                  x = pred[k]
                  a = x.get_all()
                  k = a[-1].j
                  s.extend(a)
                if len(s) > 1:
                    # copy nodes
                    head = None
                    for y in reversed(s):
                        head = Entry(y.e, y.i, y.j, y.prob, 0, head)
                    if f[i][k]:
                        f[i][k].append(head)
                    else:
                        f[i][k] = [head]
                    #print "concat'd centence:", unicode(head)
                    # update pred[i] with concat'd sentence
                    pred[i] = head
        """
        print '[DEBUG] pred:'
        for x in pred:
            if x:
                print unicode(x)
        """

    def train(self, ctx, s):

        def g(ikeys, okey, depth):
            if not okey or depth >= self.__max_key_length:
                return ikeys
            r = []
            for x in ikeys:
                if okey[0] not in self.__sa.oi_map:
                    return []
                for y in self.__sa.oi_map[okey[0]]:
                    r.append(x + [y])
            return g(r, okey[1:], depth + 1)

        indexer = lambda okey: [u' '.join(ikey) for ikey in g([[]], okey.split(), 0)]
        last = None
        for e in s:
            if last:
                self.__db.update_bigram(last, e, indexer)
            last = e
            self.__db.update_unigram(e)
        self.__db.update_freq_total(len(s))
        ctx.info = self.create_context_info()
        ctx.info.last = Entry(last.e, -1, 0, last.prob, last.use_count + 1) if last else None

    def make_candidate_list(self, ctx, i, j):
        m = ctx.info.m
        cand = ctx.info.cand
        fraz = ctx.info.fraz
        pred = ctx.info.pred
        if i >= m:
            return []
        if i == -1:
            i = ctx.sel[-1].j if ctx.sel else 0
        if j == -1:
            j = m
            while j > i and not cand[i][j] and not fraz[i][j]:
                j -= 1
        elif j == 0:
            while j < m and not cand[i][j] and not fraz[i][j]:
                j += 1
        # info about the previously selected phrase
        prev_table = dict()
        prev = ctx.sel[-1] if ctx.sel else ctx.info.last
        if prev:
            prev_award = 0.0
            prev_eid = prev.get_eid()
            #print 'prev:', prev.get_phrase(), prev_eid
            for x in cand[prev.i][prev.j]:
                if x.get_eid() == prev_eid:
                    #print u'pred[x.j]: %s x: %s' % (pred[x.j], x)
                    prev_award = pred[x.j].prob - x.prob
                    #print 'prev_award:', prev_award
                    break
            for y in fraz[prev.i][prev.j:]:
                if y:
                    for x in y[:Model.LIMIT]:
                        if x.next and x.get_eid() == prev_eid:
                            #print 'award goes to:', unicode(x)
                            prev_table[id(x.next)] = x.prob + prev_award
            #print 'prev_table:', prev_table
        def adjust(e):
            if id(e) not in prev_table:
                return e
            prob = prev_table[id(e)]
            #print 'adjust:', e.get_phrase(), e.prob, prob
            return Entry(e.e, e.i, e.j, prob, e.use_count, e.next)
        r = [[] for k in range(m + 1)]
        p = []
        #print 'range:', u''.join(ctx.input[i:j])
        for k in range(j, i, -1):
            if cand[i][k]:
                for x in cand[i][k]:
                    e = adjust(x)
                    r[k].append(e)
            if fraz[i][k]:
                for x in fraz[i][k]:
                    e = adjust(x)
                    #print "concat'd phrase:", e.get_phrase(), e.prob
                    if not any([e.partof(ex) for kx, ex in p]):
                        p.append((k, e))
        phrase_cmp = lambda a, b: -cmp(a[1].prob, b[1].prob)
        p.sort(cmp=phrase_cmp)
        for k, e in p[:Model.MAX_CONCAT_PHRASE]:
            r[k].append(e)
        if not r[j]:
            for kx, ex in p:
                if kx == j:
                    r[j].append(ex)
                    break
            #print 'supplemented:', r[j][0].get_phrase()
        cand_cmp = lambda a, b: -cmp(a.use_count + a.prob, b.use_count + b.prob)
        ret = []
        for s in reversed(r):  # longer words come first
            if s:
                phrases = set()
                for e in sorted(s, cand_cmp):
                    p = e.get_phrase()
                    # ignore less freqently used phrases with identical representation
                    if p not in phrases:
                        phrases.add(p)
                        ret.append((p, e))
        """
        for x in ret[:5]:
            print u'[DEBUG] cand: %s' % x[1]
        """
        return ret
