#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim:set et sts=4 sw=4:

import os
import sys

here = os.path.dirname(__file__)
engine_path = os.path.normpath(os.path.join(here, '..', 'engine'))
sys.path.append(engine_path)

test_db = os.path.join(here, 'test.db')
os.environ["ZIME_DATABASE"] = test_db

import ibus
from core import *
from engine import *


class TestSession(Frontend):

    '''A test session to verify rime engine's functionality.

    Not a unit test.
    The output of the engine for the frontend is printed in detail.

    '''

    def __init__(self, schema_id=None):
        self.__lookup_table = ibus.LookupTable()
        self.__backend = Engine(self, schema_id)

    def process_key_event(self, keycode, mask):
        print "process_key_event: '%s'(%x), %08x" % \
            (keysyms.keycode_to_name(keycode), keycode, mask)
        return self.__backend.process_key_event(KeyEvent(keycode, mask))

    def commit_string(self, s):
        print u'commit: [%s]' % s

    def update_preedit(self, s, start=0, end=0):
        if start < end:
            print u'preedit: [%s[%s]%s]' % (s[:start], s[start:end], s[end:])
        else:
            print u'preedit: [%s]' % s
        if not s:
            return

    def update_aux(self, s, start=0, end=0):
        if start < end:
            print u'aux: [%s[%s]%s]' % (s[:start], s[start:end], s[end:])
        else:
            print u'aux: [%s]' % s
        if not s:
            return

    def update_candidates(self, candidates):
        self.__lookup_table.clean()
        self.__lookup_table.show_cursor(False)
        if not candidates:
            #self.hide_lookup_table()
            pass
        else:
            for c in candidates:
                self.__lookup_table.append_candidate(ibus.Text(c[0]))
            #self.update_lookup_table(self.__lookup_table, True, True)
            self.__candidates = candidates
            self.__update_lookup_table()

    def __update_lookup_table(self):
        start = self.__lookup_table.get_current_page_start()
        end = start + self.__lookup_table.get_page_size()
        cursor_pos = start + self.__lookup_table.get_cursor_pos_in_current_page()
        c = self.__candidates
        for i in range(len(c)):
            if i < start:
                continue
            if i >= end:
                break
            print u'candidate: %d%s %s' % (
                i + 1,
                u'*' if i == cursor_pos else u'.', 
                c[i][0]
            )
            
    def page_up(self):
        if self.__lookup_table.page_up():
            print u'page_up.'
            #self.update_lookup_table(self.__lookup_table, True, True)
            self.__update_lookup_table()
            return True
        return False

    def page_down(self):
        if self.__lookup_table.page_down():
            print u'page_down.'
            #self.update_lookup_table(self.__lookup_table, True, True)
            self.__update_lookup_table()
            return True
        return False

    def cursor_up(self):
        if self.__lookup_table.cursor_up():
            print u'cursor_up.'
            #self.update_lookup_table(self.__lookup_table, True, True)
            self.__update_lookup_table()
            return True
        return False

    def cursor_down(self):
        if self.__lookup_table.cursor_down():
            print u'cursor_down.'
            #self.update_lookup_table(self.__lookup_table, True, True)
            self.__update_lookup_table()
            return True
        return False

    def get_candidate_index(self, number):
        index = number + self.__lookup_table.get_current_page_start()
        print u'index = %d' % index
        return index

    def get_highlighted_candidate_index(self):
        index = self.__lookup_table.get_cursor_pos()
        print u'highlighted_candidate_index = %d' % index
        return index

    def feed(self, string):
        '''emulate input process with a key sequence.

        a key can be represented by the printable ascii letter it produces,
        or a {KeyName} form.
        example: "pin'yin shurufa{Return}"

        '''
        key_name = ''
        is_key_name = False
        for c in string:
            if c == '{':
                is_key_name = True
                key_name = ''
            elif c == '}':
                is_key_name = False
                self.process_key_event(keysyms.name_to_keycode(key_name), 0)
            elif is_key_name:
                key_name += c
            else:
                self.process_key_event(ord(c), 0)

def test_switcher():
    # calls schema switcher
    e = TestSession()
    e.process_key_event(keysyms.grave, modifier.CONTROL_MASK)  # Ctrl+grave
    e.process_key_event(keysyms.grave, modifier.CONTROL_MASK | modifier.RELEASE_MASK)
    # make a choice
    e.feed('2')
    # open
    e.process_key_event(keysyms.F1, 0)
    e.process_key_event(keysyms.F1, modifier.RELEASE_MASK)
    # send F1
    e.process_key_event(keysyms.F1, 0)
    e.process_key_event(keysyms.F1, modifier.RELEASE_MASK)
    # open
    e.process_key_event(keysyms.F1, 0)
    e.process_key_event(keysyms.F1, modifier.RELEASE_MASK)
    # make a choice
    e.feed('2')

def test_pinyin():
    e = TestSession(u'Pinyin')
    e.feed('jiongajiong ')

def test_rawmode():
    e = TestSession(u'Pinyin')
    e.feed('Rime 1.0!{Return}')

def test_editor():
    e = TestSession(u'Pinyin')
    #e.feed('jiongqiongxiongyong{Home}{Right}{Right}{Right}{Right}')
    #e.feed("pinyin-shurufa'ya'pinyin-shurufa{End}{Left}{Left}{Left}")
    #e.feed('henanquan{Home}{Tab} ')
    #e.feed('henanhenanquan{Tab} {Tab}{Tab}')
    e.feed('changan{Left}{Escape}')
    e.feed('changanshizhongguodeshoudu{Left}{Escape}')

def test_zhuyin():
    e = TestSession(u'Zhuyin')
    e.feed('rm/3rm/3u.3gp6zj/ {Escape}2k7al {Tab}{Return}')

def test_combo_pinyin():
    e = TestSession(u'ComboPinyin')
    e.process_key_event(keysyms.r, 0)
    e.process_key_event(keysyms.j, 0)
    e.process_key_event(keysyms.k, 0)
    e.process_key_event(keysyms.l, 0)
    e.process_key_event(keysyms.r, modifier.RELEASE_MASK)
    e.process_key_event(keysyms.j, modifier.RELEASE_MASK)
    e.process_key_event(keysyms.k, modifier.RELEASE_MASK)
    e.process_key_event(keysyms.l, modifier.RELEASE_MASK)
    e.process_key_event(keysyms.space, 0)
    e.process_key_event(keysyms.space, modifier.RELEASE_MASK)

def test_jyutping():
    e = TestSession(u'Jyutping')
    e.feed('jyuhomindeoicangjatheizaugwodikjatzi')

def test_tonal_pinyin():
    e = TestSession(u'TonalPinyin')
    e.feed('woyebuzhidaoshibushi .jiong')
    e.feed('pkucn.com')
    e.feed('3.14wo1.0')

def main():
    #test_pinyin()
    #test_rawmode()
    #test_editor()
    #test_tonal_pinyin()
    #test_zhuyin()
    pass

if __name__ == "__main__":
    main()
