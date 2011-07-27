# -*- coding: utf-8 -*-
# vim:set et sts=4 sw=4:

import ibus
from ibus import keysyms
from ibus import modifier

from storage import DB

__all__ = (
    "ibus",
    "keysyms",
    "modifier",
    "KeyEvent",
    "Frontend",
    "Processor",
    "Schema",    
    "Spelling",
    "Commit", 
)

class KeyEvent(object):
    '''鍵盤事件

    按ibus／GTK對鍵值的定義，keycode與字符對應而非與按鍵對應，即區分A與a
    mask含各種功能鍵狀態及按鍵的RELEASE狀態
    coined，是否偽造的按鍵，有時會在程序裡產生不同於實際輸入的鍵盤事件以模擬某個功能

    '''
    def __init__(self, keycode, mask, coined=False):
        self.keycode = keycode
        self.mask = mask
        self.coined = coined

    def __str__(self):
        return "<KeyEvent: '%s'(%x), %08x>" % (keysyms.keycode_to_name(self.keycode), self.keycode, self.mask)

    def get_char(self):
        return unichr(self.keycode)

    def is_modified_key(self):
        return bool(self.mask & (modifier.CONTROL_MASK | \
                                 modifier.ALT_MASK | \
                                 modifier.SUPER_MASK | \
                                 modifier.HYPER_MASK | \
                                 modifier.META_MASK)) 

    def is_key_up(self):
        return bool(self.mask & modifier.RELEASE_MASK)


class Frontend(object):

    '''抽象的前端
    '''

    def commit_string(self, s):
        '''文字上屏
        '''
        pass

    def update_preedit(self, s, start=0, end=0):
        '''更新寫作串
        [start, end) 定義了串中的高亮區間
        '''
        pass

    def update_aux(self, s, start=0, end=0):
        '''更新輔助串
        [start, end) 定義了串中的高亮區間
        '''
        pass

    def update_candidates(self, candidates):
        '''更新候選列表
        '''
        pass

    def page_up(self):
        '''上翻頁
        '''
        pass

    def page_down(self):
        '''下翻頁
        '''
        pass

    def cursor_up(self):
        '''高亮上一候選
        '''
        pass

    def cursor_down(self):
        '''高亮下一候選
        '''
        pass

    def get_highlighted_candidate_index(self):
        '''依選詞光標取得高亮候選詞在候選詞列表中的索引
        '''
        return -1

    def get_candidate_index(self, number):
        '''依候選詞在當前頁中的序號，取得其在候選詞列表中的索引
        '''
        return -1


class Processor(object):

    '''抽象的輸入事件處理邏輯
    '''

    def process_key_event(self, key_event):
        '''處理鍵盤事件
        
        返回True表示已處理過；返回False表示不關心該事件
        '''
        return False


# TODO: 這兩個類要取消

class Spelling:

    '''拼寫
    
    高亮顯示未完成輸入的編碼／未選定的標點符號
    其內容尚未記入編碼串中因此不會做轉換

    '''

    def __init__(self, text=None, start=0, end=0, padding=None):
        # padding 用於分隔前文與此拼寫
        if text and not end:
            end = len(text)
        if text and padding:
            self.text = padding + text
            self.start = len(padding) + start
            self.end = len(padding) + end
        else:
            self.text = text
            self.start = start
            self.end = end

    def is_empty(self):
        return not self.text


class Commit(unicode):
    '''上屏動作'''
    pass


class Schema:

    '''輸入方案
    '''

    def __init__(self, schema_id):
        self.schema_id = schema_id
        self.__db = DB(schema_id)

    def get_db(self):
        return self.__db

    def get_config_value(self, key):
        '''取單一設定值'''
        return self.__db.read_config_value(key)

    def get_config_char_sequence(self, key):
        '''
        讀字符序列設定
        可將字符序列寫在[]內以包含空白字符
        '''
        r = self.__db.read_config_value(key)
        if r and r.startswith(u'[') and r.endswith(u']'):
            return r[1:-1]
        return r

    def get_config_list(self, key):
        '''取多個設定值'''
        return self.__db.read_config_list(key)

