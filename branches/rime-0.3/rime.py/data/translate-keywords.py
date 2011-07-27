#! /usr/bin/env python

try:
    import psyco
    psyco.full()
    print 'psyco activated.'
except:
    pass

import os
import sys
import optparse
import json
import re

def debug(*what):
    print >> sys.stderr, '[DEBUG]: ', ' '.join(map(unicode, what))

class SpellingCollisionError:
    def __init__(self, rule, vars):
        self.rule = rule
        self.vars = vars
    def __str__(self):
        return 'spelling collision detected in %s: %s' % (self.rule, repr(self.vars))

class SpellingAlgebra:

    def __init__(self, report_errors=True):
        self.__report_errors = report_errors

    def calculate(self, mapping_rules, fuzzy_rules, spelling_rules, alternative_rules, keywords):

        akas = dict()

        def add_aka(s, x):
            if s in akas:
                a = akas[s]
            else:
                a = akas[s] = []
            if x not in a:
                a.append(x)

        def del_aka(s, x):
            if s in akas:
                a = akas[s]
            else:
                a = akas[s] = []
            if x in a:
                a.remove(x)
            if not a:
                del akas[s]

        def transform(x, r):
            return r[0].sub(r[1], x, 1)

        def apply_fuzzy_rule(d, r):
            dd = dict(d)
            for x in d:
                if not r[0].search(x):
                    continue
                y = transform(x, r)
                if y == x:
                    continue
                if y not in dd:
                    dd[y] = d[x]
                    add_aka(dd[y], y)
                else:
                    del_aka(dd[y], y)
                    dd[y] |= d[x]
                    add_aka(dd[y], y)
            return dd

        def apply_alternative_rule(d, r):
            for x in d.keys():
                if not r[0].search(x):
                    continue
                y = transform(x, r)
                if y == x:
                    continue
                if y not in d:
                    d[y] = d[x]
                elif self.__report_errors:
                    raise SpellingCollisionError('AlternativeRule', (x, d[x], y, d[y]))
            return d

        io_map = dict()
        for okey in keywords:
            ikey = reduce(transform, mapping_rules, okey)
            s = frozenset([okey])
            if ikey in io_map:
                io_map[ikey] |= s
            else:
                io_map[ikey] = s
        for ikey in io_map:
            add_aka(io_map[ikey], ikey)
        io_map = reduce(apply_fuzzy_rule, fuzzy_rules, io_map)

        oi_map = dict()
        ikeys = []
        spellings = []
        for okeys in akas:
            ikey = akas[okeys][0]
            ikeys.append(ikey)
            for x in akas[okeys]:
                spellings.append((x, ikey))
            for k in okeys:
                if k in oi_map:
                    a = oi_map[k]
                else:
                    a = oi_map[k] = []
                a.append(ikey)
        akas = None

        # remove non-ikey keys
        io_map = dict([(k, list(io_map[k])) for k in ikeys])

        spelling_map = dict()
        for s, ikey in spellings:
            t = reduce(transform, spelling_rules, s)
            if t not in spelling_map:
                spelling_map[t] = ikey
            elif self.__report_errors:
                raise SpellingCollisionError('SpellingRule', (s, ikey, t, spelling_map[t]))
        # do not apply alternative_rules for results with standard spelling only 
        #spelling_map = reduce(apply_alternative_rule, alternative_rules, spelling_map)

        return spelling_map, io_map, oi_map

usage = 'usage: %prog [options] YourSchema.txt'
parser = optparse.OptionParser(usage)

parser.add_option('-i', '--ikey', action='store_true', dest='ikey', default=False, help='use ikeys rather than spellings')
parser.add_option('-s', '--source', dest='source', help='specify the prefix of source dict files', metavar='PREFIX')
parser.add_option('-v', '--verbose', action='store_true', dest='verbose', default=False, help='make lots of noice')

options, args = parser.parse_args()

if len(args) != 1:
    parser.error('incorrect number of arguments')
schema_file = args[0] if len(args) > 0 else None

schema = None
display_name = None
dict_prefix = None

mapping_rules = []
fuzzy_rules = []
spelling_rules = []
alternative_rules = []

if schema_file:
    equal_sign = re.compile(ur'\s*=\s*')
    compile_repl_pattern = lambda x: (re.compile(x[0]), x[1])
    back_ref = re.compile(ur'\\(\d+)')
    back_ref_g = re.compile(ur'\\g<(\d+)>')
    def to_js_regex(r):
        p = r.split(None, 1)
        if len(p) < 2:
            return r
        p[1] = back_ref.sub(ur'$\1', back_ref_g.sub(ur'$\1', p[1]))
        return u' '.join(p)
    f = open(schema_file, 'r')
    for line in f:
        x = line.strip().decode('utf-8').lstrip(u'\ufeff')
        if not x or x.startswith(u'#'):
            continue
        try:
            (path, value) = equal_sign.split(x, 1)
        except:
            print >> sys.stderr, 'error parsing (%s) %s' % (schema_file, x)
            exit()
        if not schema and path == u'Schema':
            schema = value
            print >> sys.stderr, 'schema: %s' % schema
        if schema:
            if path == u'DisplayName':
                display_name = value
            if not dict_prefix and path == u'Dict':
                dict_prefix = value
                print >> sys.stderr, 'dict: %s' % dict_prefix
            if path == u'MaxKeyLength':
                max_key_length = int(value)
            elif path == u'MappingRule':
                mapping_rules.append(compile_repl_pattern(value.split()))
            elif path == u'FuzzyRule':
                fuzzy_rules.append(compile_repl_pattern(value.split()))
            elif path == u'SpellingRule':
                spelling_rules.append(compile_repl_pattern(value.split()))
            elif path == u'AlternativeRule':
                alternative_rules.append(compile_repl_pattern(value.split()))
        if path.endswith(u'Rule'):
            value = to_js_regex(value) 
    f.close()

if not dict_prefix:
    print >> sys.stderr, 'no dict specified in schema file.'
    exit()

prefix_args = {'prefix' : dict_prefix}

source_file_prefix = options.source or dict_prefix.replace(u'_', u'-')
keyword_file = '%s-keywords.txt' % source_file_prefix

keywords = dict()
if keyword_file:
    f = open(keyword_file, 'r')
    for line in f:
        x = line.strip().decode('utf-8').lstrip(u'\ufeff')
        if not x or x.startswith(u'#'):
            continue
        try:
            ll = x.split(u'\t', 1)
            (okey, phrase) = ll
        except:
            print >> sys.stderr, 'error: invalid format (%s) %s' % (keyword_file, x)
            exit()
        if okey not in keywords:
            keywords[okey] = [phrase]
        else:
            keywords[okey].append(phrase)
    f.close()

sa = SpellingAlgebra()
try:
    spelling_map, io_map, oi_map = sa.calculate(mapping_rules, 
                                                fuzzy_rules, 
                                                spelling_rules, 
                                                alternative_rules, 
                                                keywords)
except SpellingCollisionError as e:
    print >> sys.stderr, e
    exit()

if options.ikey:
    for ikey in io_map:
        s = set()
        for okey in io_map[ikey]:
            s |= set(keywords[okey])
        for x in s:
            print u'\t'.join([ikey, x]).encode('utf-8')
else:
    for spelling in spelling_map:
        ikey = spelling_map[spelling]
        s = set()
        for okey in io_map[ikey]:
            s |= set(keywords[okey])
        for x in s:
            print u'\t'.join([spelling, ikey, x]).encode('utf-8')

print >> sys.stderr, 'done.'

