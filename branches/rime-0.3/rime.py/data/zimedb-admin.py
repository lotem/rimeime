#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:set et sts=4 sw=4:

try:
    import psyco
    psyco.full()
    print 'psyco activated.'
except:
    pass

import os
import sys
import optparse
import sqlite3
import re

zime_data_path = os.path.dirname(__file__)
zime_engine_path = os.path.normpath(os.path.join(zime_data_path, '..', 'engine'))
sys.path.append(zime_engine_path)
from algebra import *
from storage import DB


def debug(*what):
    print >> sys.stderr, u'[DEBUG]: ', u' '.join(map(unicode, what))

usage = '''
%prog [options] --list
%prog [options] --install   Schema.txt
%prog [options] --uninstall <Schema>
%prog [options] --save      <Schema>
%prog [options] --restore   <Schema>'''
parser = optparse.OptionParser(usage)

parser.add_option('-l', '--list', action='store_true', dest='list_schema', default=False, help='command: show schema list')
parser.add_option('-i', '--install', dest='install_schema', help='command: install schema', metavar='FILE')
parser.add_option('-u', '--uninstall', dest='uninstall_schema', help='command: uninstall schema and associated dict', metavar='Schema')
parser.add_option('-s', '--save', dest='save_userdata', help='command: save user data', metavar='Schema')
parser.add_option('-r', '--restore', dest='restore_userdata', help='command: restore user data', metavar='Schema')
parser.add_option('-c', '--compact', action='store_true', dest='compact', default=False, help='compact db file on modifications')
parser.add_option('-d', '--db-file', dest='db_file', help='specify zimedb location', metavar='FILE')
parser.add_option('-k', '--keep', action='store_true', dest='keep', default=False, help='keep existing dict while installing schema')
parser.add_option('-n', '--no-phrases', action='store_true', dest='no_phrases', default=False, help='do not use phrase file while installing schema')
parser.add_option('-p', '--prefix', dest='source_prefix', help='specify the prefix for dict files', metavar='PREFIX')

parser.add_option('-v', '--verbose', action='store_true', dest='verbose', default=False, help='make lots of noice')

options, args = parser.parse_args()

if len(args) != 0:
    parser.error('incorrect number of arguments')

if not options.db_file:
    home_path = os.path.expanduser('~')
    db_path = os.path.join(home_path, '.ibus', 'zime')
    if not os.path.isdir(db_path):
        os.makedirs(db_path)
    db_file = os.path.join(db_path, 'zime.db')
else:
    db_file = options.db_file

if not os.path.exists(db_file):
    if options.install_schema:
        print >> sys.stderr, 'creating new db file: %s' % db_file
    else:
        print >> sys.stderr, 'cannot locate db file: %s' % db_file
        exit(-1)

DB.open(db_file)


# retrieve schema list and associated dict names
schema_list = DB.get_schema_list()
schemas = set([x[0] for x in schema_list])
prefix_map = dict()
for (schema, prefix) in DB.get_installed_dicts():
    prefix_map[schema] = prefix


def list_schema():
    print u'# schemas installed in %s:' % db_file
    print u'%-20s %-20s %s' % (u'#<SCHEMA>', u'<DICT>', u'<NAME>')
    for (schema, label) in schema_list:
        prefix = prefix_map[schema] if schema in prefix_map else u'--'
        print u"%-20s %-20s %s" % (schema, prefix, label)


def install_schema(schema_file):
    
    # parsing Schema.txt

    equal_sign = re.compile(ur'\s*=\s*')
    def compile_repl_pattern(x):
        (patt, repl) = x.split()
        return (re.compile(patt), repl)

    schema = None
    dict_prefix = None
    max_key_length = 2
    mapping_rules = []
    fuzzy_rules = []
    spelling_rules = []
    alternative_rules = []
    db = None

    for line in open(schema_file, 'r'):
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
            DB.clear_setting(u'SchemaList/%s' % schema)
            DB.clear_setting(u'%s/%%' % schema)
        if schema:
            if path == u'DisplayName':
                # registering Schema
                DB.update_setting(u'SchemaList/%s' % schema, value)
            if not dict_prefix and path == u'Dict':
                dict_prefix = value
                print >> sys.stderr, 'dict: %s' % dict_prefix
            if path == u'MaxKeyLength':
                max_key_length = int(value)
            elif path == u'MappingRule':
                mapping_rules.append(compile_repl_pattern(value))
            elif path == u'FuzzyRule':
                fuzzy_rules.append(compile_repl_pattern(value))
            elif path == u'SpellingRule':
                spelling_rules.append(compile_repl_pattern(value))
            elif path == u'AlternativeRule':
                alternative_rules.append(compile_repl_pattern(value))
            # save setting to db
            DB.add_setting(u'%s/%s' % (schema, path), value)

    if not schema:
        print >> sys.stderr, 'error: no schema defined.'
        exit()

    if not dict_prefix:
        print >> sys.stderr, 'error: no dict specified in schema file.'
        exit()

    source_prefix = options.source_prefix or dict_prefix.replace(u'_', u'-')
    keyword_file = '%s-keywords.txt' % source_prefix
    phrase_file = None if options.no_phrases else '%s-phrases.txt' % source_prefix

    # parsing dict-keywords.txt

    keywords = dict()
    if keyword_file:
        for line in open(keyword_file, 'r'):
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

    # performing spelling algebra
    sa = SpellingAlgebra()
    try:
        sa.calculate(mapping_rules, 
                     fuzzy_rules, 
                     spelling_rules, 
                     alternative_rules, 
                     keywords)
    except SpellingCollisionError as e:
        print >> sys.stderr, e
        exit()

    if options.keep:
        DB.flush(True)
        print >> sys.stderr, 'done.'
        exit()

    db = DB(schema)
    db.recreate_tables()

    # 基本音節拼式
    db.add_keywords(sorted(keywords))

    def g(ikeys, okey, depth):
        if not okey or depth >= max_key_length:
            return ikeys
        r = []
        for x in ikeys:
            if okey[0] not in sa.oi_map:
                if options.verbose:
                    print >> sys.stderr, 'invalid keyword encountered: [%s]' % okey[0]
                return []
            for y in sa.oi_map[okey[0]]:
                r.append(x + [y])
        return g(r, okey[1:], depth + 1)
    indexer = lambda okey: [u' '.join(ikey) for ikey in g([[]], okey.split(), 0)]

    batch = list()
    counter = 0
    if options.verbose:
        print >> sys.stderr, 'processing phrases...'

    # 收錄keywords文件中的單字
    for k in keywords:
        for p in keywords[k]:
            batch.append(((p[1:] if p.startswith(u'*') else p, k), 0))
            counter += 1
            if options.verbose and counter % 10000 == 0:
                db.add_phrases(batch, indexer)
                batch = list()
                print >> sys.stderr, '%d phrases imported from %s.' % (counter, keyword_file)
    del keywords

    if phrase_file:
        for line in open(phrase_file, 'r'):
            x = line.strip().decode('utf-8').lstrip(u'\ufeff')
            if not x or x.startswith(u'#'):
                continue
            try:
                ll = x.split(u'\t', 2)
                if len(ll) == 3:
                    (phrase, freq_str, okey) = ll
                    freq = int(freq_str)
                else:
                    (okey, phrase) = ll
                    if phrase.startswith(u'*'):
                        phrase = phrase[1:]
                    freq = 0
                if u' ' in phrase:
                    phrase = phrase.replace(u' ', '')
            except:
                print >> sys.stderr, 'error: invalid format (%s) %s' % (phrase_file, x)
                exit()
            batch.append(((phrase, okey), freq))
            counter += 1
            if options.verbose and counter % 10000 == 0:
                db.add_phrases(batch, indexer)
                batch = list()
                print >> sys.stderr, '%d phrases imported from %s.' % (counter, phrase_file)

    if batch:
        db.add_phrases(batch, indexer)
    print >> sys.stderr, 'totaling %d phrases imported.' % counter

    if options.compact:
        DB.compact()
    DB.flush(True)
    print >> sys.stderr, 'done.'


def uninstall_schema(schema):

    if schema not in schemas:
        print >> sys.stderr, u'non-existing schema: %s' % schema
        return

    DB.clear_setting(u'SchemaList/%s' % schema)
    DB.clear_setting(u'SchemaChooser/%s/%%' % schema)
    DB.clear_setting(u'%s/%%' % schema)
    if schema not in prefix_map:
        print >> sys.stderr, u'warning: no dict associated with schema: %s' % schema
    else:
        prefix = prefix_map[schema]
        no_longer_needed = True
        for s, p in prefix_map.iteritems():
            if p == prefix and s != schema:
                no_longer_needed = False
                break
        if no_longer_needed:
            print >> sys.stderr, u'dict %s associated with %s is no longer needed; dropped...' % (prefix, schema)
            DB(schema).drop_tables()

    if options.compact:
        DB.compact()
    DB.flush(True)
    print >> sys.stderr, u'schema %s has been removed.' % schema


def save_userdata(schema):

    if schema not in schemas:
        print >> sys.stderr, u'non-existing schema: %s' % schema
        return

    db = DB(schema)
    prefix = db.read_config_value(u'Dict')
    filename_prefix = prefix.replace(u'_', u'-')

    userfreq_file = "%s-userfreq.txt" % filename_prefix
    out = open(userfreq_file, "w")
    r = db.dump_user_freq()
    for x in r:
        print >> out, (u"%s\t%d\t%s" % tuple(x)).encode('utf-8')
    out.close()
    print >> sys.stderr, '%d records saved to %s' % (len(r), userfreq_file)

    usergram_file = "%s-usergram.txt" % filename_prefix
    out = open(usergram_file, "w")
    r = db.dump_user_gram()
    for x in r:
        print >> out, (u"%s\t%s\t%d\t%s\t%s" % tuple(x)).encode('utf-8')
    out.close()
    print >> sys.stderr, '%d records saved to %s' % (len(r), usergram_file)
    

def restore_userdata(schema):

    if schema not in schemas:
        print >> sys.stderr, u'non-existing schema: %s' % schema
        return

    db = DB(schema)
    prefix = db.read_config_value(u'Dict')
    filename_prefix = prefix.replace(u'_', u'-')

    max_key_length = int(db.read_config_value(u'MaxKeyLength') or u'2')
    get_rules = lambda f, key: [f(r.split()) for r in db.read_config_list(key)]
    compile_repl_pattern = lambda x: (re.compile(x[0]), x[1])
    mapping_rules = get_rules(compile_repl_pattern, u'MappingRule')
    fuzzy_rules = get_rules(compile_repl_pattern, u'FuzzyRule')
    spelling_rules = get_rules(compile_repl_pattern, u'SpellingRule')
    alternative_rules = get_rules(compile_repl_pattern, u'AlternativeRule')
    keywords = db.list_keywords()
    sa = SpellingAlgebra(report_errors=False)
    sa.calculate(mapping_rules, 
                 fuzzy_rules, 
                 spelling_rules, 
                 alternative_rules, 
                 keywords)
    def g(ikeys, okey, depth):
        if not okey or depth >= max_key_length:
            return ikeys
        r = []
        for x in ikeys:
            if okey[0] not in sa.oi_map:
                if options.verbose:
                    print >> sys.stderr, 'invalid keyword encountered: [%s]' % okey[0]
                return []
            for y in sa.oi_map[okey[0]]:
                r.append(x + [y])
        return g(r, okey[1:], depth + 1)
    indexer = lambda okey: [u' '.join(ikey) for ikey in g([[]], okey.split(), 0)]

    userfreq_file = "%s-userfreq.txt" % filename_prefix
    userfreq_table = list()
    for line in open(userfreq_file):
        x = line.strip().decode('utf-8').lstrip(u'\ufeff')
        if not x or x.startswith(u'#'):
            continue
        try:
            ll = x.split(u'\t', 2)
            (phrase, freq_str, okey) = ll
            freq = int(freq_str)
            if u' ' in phrase:
                phrase = phrase.replace(u' ', '')
        except:
            print >> sys.stderr, 'error: invalid format (%s) %s' % (userfreq_file, x)
            exit()
        userfreq_table.append(((phrase, okey), freq))
    if options.verbose:
        print >> sys.stderr, 'checking new phrases...'
    def reporter(phrase, okey):
        print >> sys.stderr, 'INFO: introducing new phrase %s %s' % (phrase, okey)
    db.add_phrases([(k, 0) for (k, ufreq) in userfreq_table], indexer, reporter=reporter)
    if options.verbose:
        print >> sys.stderr, 'adjusting user freq...'
    db.restore_user_freq(userfreq_table)
    print >> sys.stderr, '%d records restored from %s' % (len(userfreq_table), userfreq_file)

    usergram_file = "%s-usergram.txt" % filename_prefix
    usergram_table = list()
    for line in open(usergram_file):
        x = line.strip().decode('utf-8').lstrip(u'\ufeff')
        if not x or x.startswith(u'#'):
            continue
        try:
            ll = x.split(u'\t', 4)
            (phrase1, phrase2, freq_str, okey1, okey2) = ll
            freq = int(freq_str)
            if u' ' in phrase1:
                phrase1 = phrase1.replace(u' ', '')
            if u' ' in phrase2:
                phrase2 = phrase2.replace(u' ', '')
        except:
            print >> sys.stderr, 'error: invalid format (%s) %s' % (usergram_file, x)
            exit()
        usergram_table.append(((phrase1, okey1), (phrase2, okey2), freq))
    if options.verbose:
        print >> sys.stderr, 'restoring user grams...'
    db.restore_user_gram(usergram_table, indexer)
    print >> sys.stderr, '%d records restored from %s' % (len(usergram_table), usergram_file)

    if options.compact:
        DB.compact()
    DB.flush(True)
    print >> sys.stderr, 'done.'


if options.install_schema:
    install_schema(options.install_schema)
elif options.uninstall_schema:
    uninstall_schema(options.uninstall_schema)
elif options.save_userdata:
    save_userdata(options.save_userdata)
elif options.restore_userdata:
    restore_userdata(options.restore_userdata)
else:
    list_schema()
