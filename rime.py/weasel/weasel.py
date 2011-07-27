#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim:set et sts=4 sw=4:

__all__ = (
    "WeaselSession",
    "WeaselService",
    "service",
)

import logging
import logging.config
import os
import time
import threading

logfile = os.path.join(os.path.dirname(__file__), "logging.conf")

logging.config.fileConfig(logfile)
logger = logging.getLogger("weasel")

import ibus
from core import *
from engine import *
import storage


def add_text(actions, msg, field, text):
    actions.add(u'ctx')
    (s, attrs, cursor) = text
    msg.append(u'ctx.%s=%s\n' % (field, s))
    if attrs:
        msg.append(u'ctx.%s.attr.length=%d\n' % (field, len(attrs)))
        for i in range(len(attrs)):
            (extent, type_) = attrs[i]
            msg.append(u'ctx.%s.attr.%d.range=%d,%d\n' % (field, i, extent[0], extent[1]))
            msg.append(u'ctx.%s.attr.%d.type=%s\n' % (field, i, type_))
    if cursor:
        msg.append(u'ctx.%s.cursor=%d,%d\n' % (field, cursor[0], cursor[1]))

def add_cand(actions, msg, cand_info):
    actions.add(u'ctx')
    (current_page, total_pages, cursor, cands) = cand_info
    n = len(cands)
    msg.append(u'ctx.cand.length=%d\n' % n)
    for i in range(n):
        msg.append(u'ctx.cand.%d=%s\n' % (i, cands[i][0]))
    msg.append(u'ctx.cand.cursor=%d\n' % cursor)
    msg.append(u'ctx.cand.page=%d/%d\n' % (current_page, total_pages))
    #msg.append(u'ctx.cand.current_page=%d\n' % current_page)
    #msg.append(u'ctx.cand.total_pages=%d\n' % total_pages)


class WeaselSession:

    '''【小狼毫】會話

    承擔Rime算法引擎與【小狼毫】前端的交互

    '''

    def __init__(self, params=None):
        logger.info("init weasel session: %s", params)
        self.__page_size = storage.DB.read_setting(u'Option/PageSize') or 5
        self.__lookup_table = ibus.LookupTable(self.__page_size)
        self.__clear()
        self.__backend = Engine(self, params)

    def __clear(self):
        self.__commit = None
        self.__preedit = None
        self.__aux = None
        self.__cand = None

    def process_key_event(self, keycode, mask):
        '''處理鍵盤事件'''
        logger.debug("process_key_event: '%s'(%x), %08x" % \
                     (keysyms.keycode_to_name(keycode), keycode, mask))
        self.__clear()
        taken = self.__backend.process_key_event(KeyEvent(keycode, mask))
        return taken

    def get_response(self):
        '''生成回應消息'''
        actions = set()
        msg = list()
        if self.__commit:
            actions.add(u'commit')
            msg.append(u'commit=%s\n' % u''.join(self.__commit)) 
        if self.__preedit:
            add_text(actions, msg, u'preedit', self.__preedit)
        if self.__aux:
            add_text(actions, msg, u'aux', self.__aux)
        if self.__cand:
            add_cand(actions, msg, self.__cand)
        #self.__clear()
        if not actions:
            return u'action=noop\n.\n'
        else:
            # starts with an action list
            msg.insert(0, u'action=%s\n' % u','.join(sorted(actions)))
            # ends with a single dot
            msg.append(u'.\n')
            return u''.join(msg)
    
    # implement a frontend proxy for rime engine

    def commit_string(self, s):
        '''文字上屏'''
        logger.debug(u'commit: [%s]' % s)
        if self.__commit:
            self.__commit.append(s)
        else:
            self.__commit = [s]

    def update_preedit(self, s, start=0, end=0):
        '''更新寫作串

        [start, end) 定義了串中的高亮區間

        '''
        if start < end:
            logger.debug(u'preedit: [%s[%s]%s]' % (s[:start], s[start:end], s[end:]))
        else:
            logger.debug(u'preedit: [%s]' % s)
        #attrs = [((start, end), u'HIGHLIGHTED')] if start < end else None
        #self.__preedit = (s, attrs)
        cursor = (start, end) if start < end else None
        self.__preedit = (s, None, cursor)

    def update_aux(self, s, start=0, end=0):
        '''更新輔助串

        [start, end) 定義了串中的高亮區間

        '''
        if start < end:
            logger.debug(u'aux: [%s[%s]%s]' % (s[:start], s[start:end], s[end:]))
        else:
            logger.debug(u'aux: [%s]' % s)
        cursor = (start, end) if start < end else None
        self.__aux = (s, None, cursor)

    def update_candidates(self, candidates):
        '''更新候選列表'''
        self.__lookup_table.clean()
        self.__lookup_table.show_cursor(False)
        if not candidates:
            self.__cand = (0, 0, 0, [])
        else:
            for c in candidates:
                self.__lookup_table.append_candidate(ibus.Text(c[0]))
            self.__update_page()

    def __update_page(self):
        candidates = self.__lookup_table.get_candidates_in_current_page()
        n = self.__lookup_table.get_number_of_candidates()
        c = self.__lookup_table.get_cursor_pos()
        p = self.__lookup_table.get_page_size()
        current_page = c / p
        total_pages = (n + p - 1) / p
        cands = [(x.get_text(), None) for x in candidates]
        self.__cand = (current_page, total_pages, c % p, cands)
            
    def page_up(self):
        if self.__lookup_table.page_up():
            #print u'page up.'
            self.__update_page()
            return True
        return False

    def page_down(self):
        if self.__lookup_table.page_down():
            #print u'page down.'
            self.__update_page()
            return True
        return False

    def cursor_up(self):
        if self.__lookup_table.cursor_up():
            #print u'cursor up.'
            self.__update_page()
            return True
        return False

    def cursor_down(self):
        if self.__lookup_table.cursor_down():
            #print u'cursor down.'
            self.__update_page()
            return True
        return False

    def get_candidate_index(self, number):
        if number >= self.__page_size:
            return -1
        index = number + self.__lookup_table.get_current_page_start()
        #print u'cand index = %d' % index
        return index

    def get_highlighted_candidate_index(self):
        index = self.__lookup_table.get_cursor_pos()
        #print u'highlighted cand index = %d' % index
        return index


class WeaselService:

    '''【小狼毫】算法服務

    管理一組會話
    每個會話對象持有一個算法引擎實例，並響應一個IME前端的輸入請求

    '''
    
    SESSION_EXPIRE_TIME = 3 * 60  # 3 min.

    def __init__(self):
        self.__sessions = dict()
        self.__timer = None

    def cleanup(self):
        '''清除所有會話'''
        logger.info("cleaning up %d remaining sessions." % len(self.__sessions))
        self.cancel_check()
        self.__sessions.clear()

    def schedule_next_check(self):
        self.cancel_check()
        self.__timer = threading.Timer(WeaselService.SESSION_EXPIRE_TIME + 10, \
                                       lambda: self.check_stale_sessions())
        self.__timer.start()

    def cancel_check(self):
        if self.__timer:
            self.__timer.cancel()
            self.__timer = None

    def check_stale_sessions(self):
        '''檢查過期的回話'''
        logger.info("check_stale_sessions...")
        expire_time = time.time() - WeaselService.SESSION_EXPIRE_TIME
        for sid in self.__sessions.keys():
            if self.__sessions[sid].last_active_time < expire_time:
                logger.info("removing stale session #%x." % sid)
                self.destroy_session(sid)
        # 還有活動會話，計劃下一次檢查
        self.__timer = None
        if self.__sessions:
            self.schedule_next_check()

    def has_session(self, sid):
        '''檢查指定會話的存在狀態'''
        if sid in self.__sessions:
            return True
        else:
            return False

    def get_session(self, sid):
        '''按標識獲取會話對象
        
        以傳遞按鍵消息等

        '''
        if sid in self.__sessions:
            session = self.__sessions[sid]
            session.last_active_time = time.time()
            return session
        else:
            return None

    def create_session(self):
        '''創建會話

        IME前端開啟輸入法時調用
        返回會話的標識（正整數）

        '''
        try:
            session = WeaselSession()
            session.last_active_time = time.time()
        except Exception, e:
            logger.error("create_session: error creating session: %s" % e)
            return None
        sid = id(session)
        self.__sessions[sid] = session
        logger.info("create_session: session #%x, total %d active sessions." % \
                    (sid, len(self.__sessions)))
        # 啟動過期會話檢查
        if self.__sessions and not self.__timer:
            self.schedule_next_check()
        return sid

    def destroy_session(self, sid):
        '''結束指定的會話

        IME前端關閉輸入法時調用

        '''
        if sid not in self.__sessions:
            logger.warning("destroy_session: invalid session #%x." % sid)
            return False
        del self.__sessions[sid]
        logger.info("destroy_session: session #%x, %d active sessions left." % \
                    (sid, len(self.__sessions)))
        # 已經無有會話時，停了過期會話檢查
        if not self.__sessions and self.__timer:
            self.cancel_check()
        return True


# a ready-to-use service instance
service = WeaselService()

