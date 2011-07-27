# -*- coding: utf-8 -*-
# vim:set et sts=4 sw=4:

import os
import sqlite3
import sys
import time


def debug(*what):
    print >> sys.stderr, u'[DEBUG]: ', u' '.join(map(unicode, what))


# sql for global tables

INIT_ZIME_DB_SQL = """
CREATE TABLE IF NOT EXISTS setting_paths (
    id INTEGER PRIMARY KEY,
    path TEXT UNIQUE
);

CREATE TABLE IF NOT EXISTS setting_values (
    path_id INTEGER,
    value TEXT
);

CREATE TABLE IF NOT EXISTS phrases (
    id INTEGER PRIMARY KEY,
    phrase TEXT UNIQUE
);
"""

QUERY_SETTING_SQL = """
SELECT value FROM setting_values WHERE path_id IN (SELECT id FROM setting_paths WHERE path = :path);
"""

QUERY_SETTING_ITEMS_SQL = """
SELECT path, value FROM setting_paths, setting_values WHERE path LIKE :pattern AND id = path_id;
"""

QUERY_SETTING_PATH_SQL = """
SELECT id FROM setting_paths WHERE path = :path;
"""

ADD_SETTING_PATH_SQL = """
INSERT INTO setting_paths VALUES (NULL, :path);
"""

ADD_SETTING_VALUE_SQL = """
INSERT INTO setting_values VALUES (:path_id, :value);
"""

UPDATE_SETTING_VALUE_SQL = """
UPDATE setting_values SET value = :value WHERE path_id == :path_id;
"""

CLEAR_SETTING_VALUE_SQL = """
DELETE FROM setting_values 
WHERE path_id IN (SELECT id FROM setting_paths WHERE path LIKE :path);
"""
CLEAR_SETTING_PATH_SQL = """
DELETE FROM setting_paths WHERE path LIKE :path;
"""

QUERY_SCHEMA_LIST_SQL = """
SELECT substr(path, length('SchemaList/') + 1), value FROM setting_paths p 
LEFT JOIN setting_values v ON p.id = v.path_id 
WHERE path LIKE 'SchemaList/%';
"""

QUERY_DICT_PREFIX_SQL = """
SELECT substr(path, 1, length(path) - length('/Dict')), value 
FROM setting_paths p LEFT JOIN setting_values v ON p.id = v.path_id 
WHERE path LIKE '%/Dict';
"""

QUERY_PHRASE_SQL = """
SELECT id FROM phrases WHERE phrase = :phrase;
"""

ADD_PHRASE_SQL = """
INSERT INTO phrases VALUES (NULL, :phrase);
"""

# dict specific sql

CREATE_DICT_SQL = """
CREATE TABLE IF NOT EXISTS %(prefix)s_keywords (
    keyword TEXT
);

CREATE TABLE IF NOT EXISTS %(prefix)s_keys (
    id INTEGER PRIMARY KEY,
    ikey TEXT UNIQUE
);

CREATE TABLE IF NOT EXISTS %(prefix)s_stats (
    sfreq INTEGER,
    ufreq INTEGER
);
INSERT INTO %(prefix)s_stats VALUES (0, 0);

CREATE TABLE IF NOT EXISTS %(prefix)s_unigram (
    id INTEGER PRIMARY KEY,
    p_id INTEGER,
    okey TEXT,
    sfreq INTEGER,
    ufreq INTEGER
);
CREATE UNIQUE INDEX IF NOT EXISTS %(prefix)s_entry_idx
ON %(prefix)s_unigram (p_id, okey);

CREATE TABLE IF NOT EXISTS %(prefix)s_ku (
    k_id INTEGER,
    u_id INTEGER,
    PRIMARY KEY (k_id, u_id)
);

CREATE TABLE IF NOT EXISTS %(prefix)s_bigram (
    e1 INTEGER,
    e2 INTEGER,
    bfreq INTEGER,
    PRIMARY KEY (e1, e2)
);

CREATE TABLE IF NOT EXISTS %(prefix)s_kb (
    k_id INTEGER,
    b_id INTEGER,
    PRIMARY KEY (k_id, b_id)
);
"""

DROP_DICT_SQL = """
DROP TABLE IF EXISTS %(prefix)s_keywords;
DROP TABLE IF EXISTS %(prefix)s_keys;
DROP TABLE IF EXISTS %(prefix)s_stats;
DROP INDEX IF EXISTS %(prefix)s_entry_idx;
DROP TABLE IF EXISTS %(prefix)s_unigram;
DROP TABLE IF EXISTS %(prefix)s_ku;
DROP TABLE IF EXISTS %(prefix)s_bigram;
DROP TABLE IF EXISTS %(prefix)s_kb;
"""

LIST_KEYWORDS_SQL = """
SELECT keyword FROM %(prefix)s_keywords;
"""

QUERY_KEY_SQL = """
SELECT id FROM %(prefix)s_keys WHERE ikey = :ikey;
"""

ADD_KEY_SQL = """
INSERT INTO %(prefix)s_keys VALUES (NULL, :ikey);
"""

QUERY_STATS_SQL = """
SELECT sfreq + ufreq AS freq, ufreq FROM %(prefix)s_stats;
"""

UPDATE_SFREQ_TOTAL_SQL = """
UPDATE %(prefix)s_stats SET ufreq = ufreq + :n;
"""

UPDATE_UFREQ_TOTAL_SQL = """
UPDATE %(prefix)s_stats SET sfreq = sfreq + :n;
"""

QUERY_UNIGRAM_SQL = """
SELECT phrase, okey, u.id, sfreq + ufreq AS freq, ufreq 
FROM %(prefix)s_unigram u, %(prefix)s_ku ku, %(prefix)s_keys k, phrases p 
WHERE ikey = :ikey AND k.id = k_id AND u_id = u.id AND p_id = p.id
ORDER BY freq DESC;
"""

UNIGRAM_EXIST_SQL = """
SELECT id FROM %(prefix)s_unigram WHERE p_id = :p_id AND okey = :okey;
"""

ADD_UNIGRAM_SQL = """
INSERT INTO %(prefix)s_unigram VALUES (NULL, :p_id, :okey, :freq, 0);
"""

INC_SFREQ_SQL = """
UPDATE %(prefix)s_unigram SET sfreq = sfreq + :freq WHERE id = :id;
"""

INC_UFREQ_SQL = """
UPDATE %(prefix)s_unigram SET ufreq = ufreq + :freq WHERE id = :id;
"""

QUERY_BIGRAM_SQL = """
SELECT e1, e2, bfreq AS freq FROM %(prefix)s_bigram b , %(prefix)s_kb kb, %(prefix)s_keys k
WHERE ikey = :ikey AND k.id = k_id AND b_id = b.rowid
ORDER BY freq;
"""

QUERY_BIGRAM_BY_ENTRY_SQL = """
SELECT e2, bfreq FROM %(prefix)s_bigram WHERE e1 = :e1;
"""

BIGRAM_EXIST_SQL = """
SELECT rowid FROM %(prefix)s_bigram WHERE e1 = :e1 AND e2 = :e2;
"""

ADD_BIGRAM_SQL = """
INSERT INTO %(prefix)s_bigram VALUES (:e1, :e2, 1);
"""

INC_BFREQ_SQL = """
UPDATE %(prefix)s_bigram SET bfreq = bfreq + :freq WHERE e1 = :e1 AND e2 = :e2;
"""

QUERY_KB_SQL = """
SELECT rowid FROM %(prefix)s_kb WHERE k_id = :k_id AND b_id = :b_id;
"""

ADD_KB_SQL = """
INSERT INTO %(prefix)s_kb VALUES (:k_id, :b_id);
"""

ADD_KEYWORD_SQL = """
INSERT INTO %(prefix)s_keywords VALUES (:keyword);
"""

ADD_KU_SQL = """
INSERT INTO %(prefix)s_ku VALUES (:k_id, :u_id);
"""

QUERY_USER_FREQ_SQL = """
SELECT phrase, ufreq, okey
FROM %(prefix)s_unigram u LEFT JOIN phrases p ON p_id = p.id
WHERE ufreq > 0
"""

QUERY_USER_GRAM_SQL = """
SELECT p1.phrase, p2.phrase, bfreq, u1.okey, u2.okey
FROM %(prefix)s_bigram b, 
     %(prefix)s_unigram u1 LEFT JOIN phrases p1 ON u1.p_id = p1.id,
     %(prefix)s_unigram u2 LEFT JOIN phrases p2 ON u2.p_id = p2.id
WHERE e1 = u1.id AND e2 = u2.id AND bfreq > 0
"""

UPDATE_USER_FREQ_SQL = """
UPDATE OR IGNORE %(prefix)s_unigram SET ufreq = ufreq + :freq
WHERE p_id IN (SELECT id FROM phrases WHERE phrase = :phrase) AND okey = :okey;
"""

def _generate_dict_specific_sql(db, prefix_args):
    db._create_dict_sql = CREATE_DICT_SQL % prefix_args
    db._drop_dict_sql = DROP_DICT_SQL % prefix_args
    db._list_keywords_sql = LIST_KEYWORDS_SQL % prefix_args
    db._add_keyword_sql = ADD_KEYWORD_SQL % prefix_args
    db._query_key_sql = QUERY_KEY_SQL % prefix_args 
    db._add_key_sql = ADD_KEY_SQL % prefix_args
    db._query_stats_sql = QUERY_STATS_SQL % prefix_args
    db._update_ufreq_total_sql = UPDATE_UFREQ_TOTAL_SQL % prefix_args
    db._update_sfreq_total_sql = UPDATE_SFREQ_TOTAL_SQL % prefix_args
    db._query_unigram_sql = QUERY_UNIGRAM_SQL % prefix_args
    db._unigram_exist_sql = UNIGRAM_EXIST_SQL % prefix_args
    db._add_unigram_sql = ADD_UNIGRAM_SQL % prefix_args
    db._inc_sfreq_sql = INC_SFREQ_SQL % prefix_args
    db._inc_ufreq_sql = INC_UFREQ_SQL % prefix_args
    db._add_ku_sql = ADD_KU_SQL % prefix_args
    db._query_bigram_sql = QUERY_BIGRAM_SQL % prefix_args
    db._query_bigram_by_entry_sql = QUERY_BIGRAM_BY_ENTRY_SQL % prefix_args
    db._bigram_exist_sql = BIGRAM_EXIST_SQL % prefix_args
    db._add_bigram_sql = ADD_BIGRAM_SQL % prefix_args
    db._inc_bfreq_sql = INC_BFREQ_SQL % prefix_args
    db._query_kb_sql = QUERY_KB_SQL % prefix_args
    db._add_kb_sql = ADD_KB_SQL % prefix_args
    db._query_user_freq_sql = QUERY_USER_FREQ_SQL % prefix_args
    db._query_user_gram_sql = QUERY_USER_GRAM_SQL % prefix_args
    db._update_user_freq_sql = UPDATE_USER_FREQ_SQL % prefix_args


class DB:

    UNIG_LIMIT = 1000
    BIG_LIMIT = 50

    FLUSH_INTERVAL = 2 * 60  # 2 minutes
    __last_flush_time = 0
    __conn = None

    @classmethod
    def open(cls, db_file, read_only=False):
        #debug('opening db file:', db_file)
        if cls.__conn:
            return
        cls.__conn = sqlite3.connect(db_file)
        cls.read_only = read_only
        if not read_only:
            cls.__conn.executescript(INIT_ZIME_DB_SQL)
            cls.flush(True)

    @classmethod
    def read_setting(cls, key):
        r = cls.__conn.execute(QUERY_SETTING_SQL, {'path': key}).fetchone()
        return r[0] if r else None

    @classmethod
    def read_setting_list(cls, key):
        r = cls.__conn.execute(QUERY_SETTING_SQL, {'path': key}).fetchall()
        return [x[0] for x in r]

    @classmethod
    def read_setting_items(cls, key):
        r = cls.__conn.execute(QUERY_SETTING_ITEMS_SQL, {'pattern': key + '%'}).fetchall()
        return [(x[0][len(key):], x[1]) for x in r]

    @classmethod
    def add_setting(cls, key, value):
        if cls.read_only:
            return False
        path_id = cls.__get_or_insert_setting_path(key)
        args = {'path_id': path_id, 'value': value}
        cls.__conn.execute(ADD_SETTING_VALUE_SQL, args)
        return True

    @classmethod
    def update_setting(cls, key, value):
        if cls.read_only:
            return False
        path_id = cls.__get_or_insert_setting_path(key)
        args = {'path_id': path_id, 'value': value}
        if cls.read_setting(key) is None:
            cls.__conn.execute(ADD_SETTING_VALUE_SQL, args)
        else:
            cls.__conn.execute(UPDATE_SETTING_VALUE_SQL, args)
        return True

    @classmethod
    def __get_or_insert_setting_path(cls, path):
        cur = cls.__conn.cursor()
        args = {'path' : path}
        r = cur.execute(QUERY_SETTING_PATH_SQL, args).fetchone()
        if r:
            return r[0]
        else:
            cur.execute(ADD_SETTING_PATH_SQL, args)
            return cur.lastrowid

    @classmethod
    def clear_setting(cls, path):
        cur = cls.__conn.cursor()
        cur.execute(CLEAR_SETTING_VALUE_SQL, {'path' : path})
        cur.execute(CLEAR_SETTING_PATH_SQL, {'path' : path})

    @classmethod
    def flush(cls, immediate=False):
        now = time.time()
        if immediate or now - cls.__last_flush_time > cls.FLUSH_INTERVAL:
            cls.__conn.commit()
            cls.__last_flush_time = now

    def __init__(self, name):
        self.__name = name
        self.__section = '%s/' % name
        prefix_args = {'prefix' : self.read_config_value('Dict')}
        _generate_dict_specific_sql(self, prefix_args)
        # for recovery from learning accidental user input
        self.__pending_updates = []

    def recreate_tables(self):
        cur = DB.__conn.cursor()
        cur.executescript(self._drop_dict_sql)
        cur.executescript(self._create_dict_sql)

    def read_config_value(self, key):
        return DB.read_setting(self.__section + key)

    def read_config_list(self, key):
        return DB.read_setting_list(self.__section + key)
        
    def list_keywords(self):
        return [x[0] for x in DB.__conn.execute(self._list_keywords_sql, ()).fetchall()]

    def lookup_freq_total(self):
        self.proceed_pending_updates()
        r = DB.__conn.execute(self._query_stats_sql).fetchone()
        return r

    def lookup_unigram(self, key):
        #print 'lookup_unigram:', key
        args = {'ikey' : key}
        r = DB.__conn.execute(self._query_unigram_sql, args).fetchmany(DB.UNIG_LIMIT)
        return r

    def lookup_bigram(self, key):
        #print 'lookup_bigram:', key
        args = {'ikey' : key}
        r = DB.__conn.execute(self._query_bigram_sql, args).fetchmany(DB.BIG_LIMIT)
        return r

    def lookup_bigram_by_entry(self, e):
        #print 'lookup_bigram_by_entry:', unicode(e)
        args = {'e1' : e.get_eid()}
        r = DB.__conn.execute(self._query_bigram_by_entry_sql, args).fetchmany(DB.BIG_LIMIT)
        return r

    def update_freq_total(self, n):
        #print 'update_freq_total:', n
        self.__pending_updates.append(lambda: self.__update_ufreq_total(n))

    def update_unigram(self, e):
        #print 'update_unigram:', unicode(e)
        self.__pending_updates.append(lambda: self.__update_unigram(e))

    def update_bigram(self, a, b, indexer):
        #print 'update_bigram:', unicode(a), unicode(b)
        self.__pending_updates.append(lambda: self.__update_bigram(a, b, indexer))

    def proceed_pending_updates(self):
        if self.__pending_updates:
            for f in self.__pending_updates:
                f()
            self.__pending_updates = []

    def cancel_pending_updates(self):
        if self.__pending_updates:
            self.__pending_updates = []

    def __update_ufreq_total(self, n):
        if DB.read_only:
            return
        args = {'n' : n}
        DB.__conn.execute(self._update_ufreq_total_sql, args)
        DB.flush()
        
    def __update_unigram(self, e):
        if DB.read_only:
            return
        args = {'id' : e.get_eid(), 'freq': 1}
        DB.__conn.execute(self._inc_ufreq_sql, args)

    def __update_bigram(self, a, b, indexer):
        if DB.read_only:
            return
        cur = DB.__conn.cursor()
        args = {'e1' : a.get_eid(), 'e2' : b.get_eid(), 'freq': 1}
        if cur.execute(self._bigram_exist_sql, args).fetchone():
            cur.execute(self._inc_bfreq_sql, args)
        else:
            cur.execute(self._add_bigram_sql, args)
            # generate ikey-bigram index
            b_id = cur.execute(self._bigram_exist_sql, args).fetchone()[0]
            okey = u' '.join([a.get_okey(), b.get_okey()])
            k_ids = [self.__get_or_insert_key(k) for k in indexer(okey)]
            for k_id in k_ids:
                self.__add_kb(k_id, b_id)

    def __get_or_insert_key(self, key):
        cur = DB.__conn.cursor()
        args = {'ikey' : key}
        r = None
        while not r:
            r = cur.execute(self._query_key_sql, args).fetchone()
            if not r:
                cur.execute(self._add_key_sql, args)
        return r[0]

    def __add_kb(self, k_id, b_id):
        args = {'k_id' : k_id, 'b_id' : b_id}
        if not DB.__conn.execute(self._query_kb_sql, args).fetchone():
            DB.__conn.execute(self._add_kb_sql, args)

    # used by zimedb-admin.py

    @classmethod
    def get_schema_list(self):
        schema_list = DB.__conn.execute(QUERY_SCHEMA_LIST_SQL).fetchall()
        return schema_list

    @classmethod
    def get_installed_dicts(self):
        prefixes = DB.__conn.execute(QUERY_DICT_PREFIX_SQL).fetchall()
        return prefixes

    def drop_tables(self, compact=False):
        DB.__conn.executescript(self._drop_dict_sql)

    @classmethod
    def compact(cls):
        DB.__conn.execute("""VACUUM;""")
    
    def add_keywords(self, keywords):
        args = [{'keyword': k} for k in keywords]
        DB.__conn.executemany(self._add_keyword_sql, args)

    def add_phrases(self, phrase_table, indexer, reporter=None):
        '''批量添加詞條並以indexer建立編碼索引'''
        # 第一趟，讀取phrase id，寫入新增詞條
        phrase_id = dict()
        missing_phrases = set()
        for (k, freq) in phrase_table:
            phrase = k[0]
            p_id = self.__get_phrase_id(phrase)
            if p_id:
                phrase_id[phrase] = p_id
            else:
                missing_phrases.add(phrase)
        if missing_phrases:
            table = [{'phrase': p} for p in missing_phrases]
            DB.__conn.executemany(ADD_PHRASE_SQL, table)
        for phrase in missing_phrases:
            p_id = self.__get_phrase_id(phrase)
            if p_id:
                phrase_id[phrase] = p_id
        # 第二趟，累計詞頻、生成unigram
        unigram_freq = dict()
        total = 0
        for (k, freq) in phrase_table:
            if k in unigram_freq:
                unigram_freq[k] += freq
            else:
                unigram_freq[k] = freq
            total += freq
        increment = list()
        missing_unigrams = set()
        for (phrase, okey), freq in unigram_freq.iteritems():
            p_id = phrase_id[phrase]
            u_id = self.__get_unigram_id(p_id, okey)
            if u_id:
                # 已有unigram，累計詞頻
                if freq > 0:
                    increment.append({'id': u_id, 'freq': freq})
            else:
                missing_unigrams.add((phrase, okey))
                if reporter:
                    reporter(phrase, okey)
        if missing_unigrams:
            table = [{'p_id': phrase_id[k[0]], 'okey': k[1], 'freq': unigram_freq[k]}
                     for k in missing_unigrams]
            DB.__conn.executemany(self._add_unigram_sql, table)
        if increment:
            DB.__conn.executemany(self._inc_sfreq_sql, increment)
        if total > 0:
            self.__inc_freq_total(total)
        
        # 建立索引
        key_id = dict()
        missing_keys = set()
        missing_ku_links = set()
        for (phrase, okey) in missing_unigrams:
            u_id = self.__get_unigram_id(phrase_id[phrase], okey)
            if not u_id:
                # shouldn't happen!
                continue
            for key in indexer(okey):
                missing_ku_links.add((key, u_id))
                k_id = self.__get_key_id(key)
                if k_id:
                    key_id[key] = k_id
                else:
                    missing_keys.add(key)
        if missing_keys:
            table = [{'ikey': k} for k in missing_keys]
            DB.__conn.executemany(self._add_key_sql, table)
        for key in missing_keys:
            k_id = self.__get_key_id(key)
            if k_id:
                key_id[key] = k_id
        if missing_ku_links:
            table = [{'k_id': key_id[k], 'u_id': u} for (k, u) in missing_ku_links]
            DB.__conn.executemany(self._add_ku_sql, table)

    def __get_phrase_id(self, phrase):
        args = {'phrase': phrase}
        r = DB.__conn.execute(QUERY_PHRASE_SQL, args).fetchone()
        return r[0] if r else None

    def __get_key_id(self, key):
        args = {'ikey': key}
        r = DB.__conn.execute(self._query_key_sql, args).fetchone()
        return r[0] if r else None

    def __get_unigram_id(self, p_id, okey):
        args = {'p_id': p_id, 'okey': okey}
        r = DB.__conn.execute(self._unigram_exist_sql, args).fetchone()
        return r[0] if r else None

    def __inc_freq_total(self, n):
        args = {'n' : n}
        DB.__conn.execute(self._update_sfreq_total_sql, args)

    def dump_user_freq(self):
        return DB.__conn.execute(self._query_user_freq_sql).fetchall()
    
    def dump_user_gram(self):
        return DB.__conn.execute(self._query_user_gram_sql).fetchall()

    def restore_user_freq(self, freq_table):
        cur = DB.__conn.cursor()
        unigram_freq = dict()
        for (u, n) in freq_table:
            if u in unigram_freq:
                unigram_freq[u] += n
            else:
                unigram_freq[u] = n
        table = list()
        total_increment = 0
        for (phrase, okey), n in unigram_freq.iteritems():
            table.append({'phrase': phrase, 'okey': okey, 'freq': n})
            total_increment += n
        cur.executemany(self._update_user_freq_sql, table)
        if total_increment > 0:
            cur.execute(self._update_ufreq_total_sql, {'n': total_increment})

    def restore_user_gram(self, freq_table, indexer):
        cur = DB.__conn.cursor()
        bigram_freq = dict()
        for (a, b, n) in freq_table:
            k = (a, b)
            if k in bigram_freq:
                bigram_freq[k] += n
            else:
                bigram_freq[k] = n
        missing = list()
        increment = list()
        for ((phrase1, okey1), (phrase2, okey2)), n in bigram_freq.iteritems():
            p1 = self.__get_phrase_id(phrase1)
            if not p1:
                continue
            e1 = self.__get_unigram_id(p1, okey1)
            if not e1:
                continue
            p2 = self.__get_phrase_id(phrase2)
            if not p2:
                continue
            e2 = self.__get_unigram_id(p2, okey2)
            if not e2:
                continue
            args = {'e1': e1, 'e2': e2, 'freq': n, 'okey': u' '.join([okey1, okey2])}
            if cur.execute(self._bigram_exist_sql, args).fetchone():
                increment.append(args)
            else:
                missing.append(args)
        cur.executemany(self._inc_bfreq_sql, increment)
        cur.executemany(self._add_bigram_sql, missing)
        # generate ikey-bigram index
        for args in missing:
            b_id = cur.execute(self._bigram_exist_sql, args).fetchone()[0]
            k_ids = [self.__get_or_insert_key(k) for k in indexer(args['okey'])]
            for k_id in k_ids:
                self.__add_kb(k_id, b_id)
