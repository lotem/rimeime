# -*- coding: utf-8 -*-
# vim:set et sts=4 sw=4:

__all__ = (
    "RimeSession",
)

import os
import ibus
from core import *
from engine import *
import storage

class RimeSession(ibus.EngineBase, Frontend):

    '''Rime會話
    
    實現ibus輸入引擎，響應一個客戶程序的輸入請求

    '''

    def __init__(self, conn, object_path):
        super(RimeSession, self).__init__(conn, object_path)
        self.__page_size = storage.DB.read_setting(u'Option/PageSize') or 5
        self.__lookup_table = ibus.LookupTable(self.__page_size)
        self.__backend = Engine(self)

    def process_key_event(self, keyval, keycode, mask):
        '''處理鍵盤事件
        '''
        return self.__backend.process_key_event(KeyEvent(keyval, mask))

    def commit_string(self, s):
        '''文字上屏
        '''
        #logger.debug(u'commit: [%s]' % s)
        super(RimeSession, self).commit_text(ibus.Text(s))

    def update_preedit(self, s, start=0, end=0):
        '''更新寫作串
        [start, end) 定義了串中的高亮區間
        '''
        #logger.debug(u'preedit: [%s]' % s)
        if not s:
            super(RimeSession, self).hide_preedit_text()
            return
        length = len(s)
        attrs = ibus.AttrList()
        attrs.append(ibus.AttributeUnderline(ibus.ATTR_UNDERLINE_SINGLE, 0, length))
        if start < end:
            attrs.append(ibus.AttributeBackground(ibus.RGB(255, 255, 128), start, end))
            attrs.append(ibus.AttributeForeground(ibus.RGB(0, 0, 0), start, end))
        t = ibus.Text(s, attrs)
        super(RimeSession, self).update_preedit_text(t, length, True)

    def update_aux(self, s, start=0, end=0):
        '''更新輔助串
        [start, end) 定義了串中的高亮區間
        '''
        #logger.debug(u'aux: [%s]' % s)
        if not s:
            super(RimeSession, self).hide_auxiliary_text()
            return
        length = len(s)
        attrs = ibus.AttrList()
        if start < end:
            attrs.append(ibus.AttributeBackground(ibus.RGB(255, 255, 128), start, end))
            attrs.append(ibus.AttributeForeground(ibus.RGB(0, 0, 0), start, end))
        t = ibus.Text(s, attrs)
        super(RimeSession, self).update_auxiliary_text(t, True)

    def update_candidates(self, candidates):
        '''更新候選列表
        '''
        self.__lookup_table.clean()
        self.__lookup_table.show_cursor(False)
        if not candidates:
            self.hide_lookup_table()
        else:
            for c in candidates:
                self.__lookup_table.append_candidate(ibus.Text(c[0]))
            self.update_lookup_table(self.__lookup_table, True, True)
    
    def page_up(self):
        '''上翻頁
        '''
        if self.__lookup_table.page_up():
            self.update_lookup_table(self.__lookup_table, True, True)
            return True
        return False

    def page_down(self):
        '''下翻頁
        '''
        if self.__lookup_table.page_down():
            self.update_lookup_table(self.__lookup_table, True, True)
            return True
        return False

    def cursor_up(self):
        '''高亮上一候選
        '''
        if self.__lookup_table.cursor_up():
            self.update_lookup_table(self.__lookup_table, True, True)
            return True
        return False

    def cursor_down(self):
        '''高亮下一候選
        '''
        if self.__lookup_table.cursor_down():
            self.update_lookup_table(self.__lookup_table, True, True)
            return True
        return False

    def focus_in(self):
        self.__backend.on_update()

    def focus_out(self):
        switcher = self.__backend.switcher
        if switcher.active:
            switcher.on_escape()

    def get_highlighted_candidate_index(self):
        '''依選詞光標取得高亮候選詞在候選詞列表中的索引
        '''
        index = self.__lookup_table.get_cursor_pos()
        return index

    def get_candidate_index(self, number):
        '''依候選詞在當前頁中的序號，取得其在候選詞列表中的索引
        '''
        if number >= self.__page_size:
            return -1
        index = number + self.__lookup_table.get_current_page_start()
        return index

