#!/usr/bin/env python
# -*- coding: utf-8 -*-

__all__ = (
    "MenuProcessor",
    "Switcher",
)

import time
from core import *
from storage import DB

class MenuProcessor(Processor):

    '''選單相關的按鍵處理框架'''

    def __init__(self, handler):
        self.handler = handler
        self.active = False

    def activate(self):
        self.active = True

    def deactivate(self):
        self.active = False

    def handle_additional_function_key(self, event):
        '''處理其他功能鍵'''
        return False

    def triggered(self, event):
        '''判斷開啟選單的條件'''
        return True

    def on_escape(self):
        '''響應取消選取的動作'''
        self.deactivate()
        
    def on_select(self, index):
        '''響應選取菜單項的動作'''
        pass
        
    def process_key_event(self, event):
        '''按鍵處理流程'''
        if not self.active:
            if self.triggered(event):
                self.activate()
                return True
            # 不做處理！
            return False
        # 快捷鍵有效
        if event.is_modified_key():
            return False
        if event.is_key_up():
            return True
        if self.handle_additional_function_key(event):
            return True
        # 選單相關的功能鍵
        if event.keycode == keysyms.Escape:
            self.on_escape()
            return True
        if event.keycode == keysyms.Page_Up:
            self.handler.on_page_up()
            return True
        if event.keycode == keysyms.Page_Down:
            self.handler.on_page_down()
            return True
        if event.keycode == keysyms.Up:
            self.handler.on_cursor_up()
            return True
        if event.keycode == keysyms.Down:
            self.handler.on_cursor_down()
            return True
        if event.keycode >= keysyms._1 and event.keycode <= keysyms._9:
            index = self.handler.query_index(event.keycode - keysyms._1)
            self.on_select(index)
            return True
        if event.keycode == keysyms._0:
            index = self.handler.query_index(9)
            self.on_select(index)
            return True
        if event.keycode in (keysyms.space, keysyms.Return):
            index = self.handler.query_index()
            self.on_select(index)
            return True    
        # 不響應其他按鍵！
        return True


class Switcher(MenuProcessor):
    '''切換輸入方案

    以熱鍵呼出方案選單，選取後將以相應的輸入方案創建會話

    '''

    def __init__(self, handler, schema_id=None):
        super(Switcher, self).__init__(handler)
        self.__load_schema_list()
        self.choose(schema_id)

    def __load_schema_list(self):
        '''載入方案列表'''
        tempo = dict()
        for schema, t in DB.read_setting_items(u'SchemaChooser/LastUsed/'):
            tempo[schema] = float(t)
        # 按最近選用的時間順序排列
        last_used_time = lambda s: tempo[s[0]] if s[0] in tempo else 0.0
        schema_list = sorted(DB.read_setting_items(u'SchemaList/'),
                             key=last_used_time, reverse=True)
        self.__schema_list = schema_list

    def choose(self, schema_id):
        '''切換方案'''
        schema_ids = [x[0] for x in self.__schema_list]
        names = [x[1] for x in self.__schema_list]
        index = -1
        if schema_id and schema_id in schema_ids:
            # 參數指定了方案標識
            index = schema_ids.index(schema_id)
        elif len(schema_ids) > 0:
            # 默認選取第一項
            index = 0
        if index == -1:
            # 無可用的方案
            return
        # 記錄選用方案的時間
        now = time.time()        
        DB.update_setting(
            u'SchemaChooser/LastUsed/%s' % schema_ids[index],
            unicode(now)
        )
        # 執行切換
        self.deactivate()
        self.handler.on_schema_change(schema_ids[index], names[index])

    def activate(self):
        '''開啟選單'''
        #print "activating switcher"
        self.active = True
        self.__load_schema_list()
        self.handler.on_switcher_active(self.__schema_list)

    def deactivate(self):
        '''關閉選單'''
        #print "deactivating switcher"
        self.active = False
        self.__schema_list = []

    def on_escape(self):
        '''關閉選單，返回上一會話'''
        self.deactivate()
        self.handler.on_update()

    def on_select(self, index):
        '''選用方案'''
        if index >= 0 and index < len(self.__schema_list):
            schema_id = self.__schema_list[index][0]
            self.choose(schema_id)

    def triggered(self, event):
        '''以Ctrl-`或F1開啟選單'''
        if event.keycode == keysyms.grave and event.mask & modifier.CONTROL_MASK:
            return True
        if event.keycode == keysyms.F1 and not event.is_key_up():
            self.__F1_released = False
            return True
        return False

    def process_key_event(self, event):
        #print "Swither.process_key_event(), event=%s, active=%s" % (event, self.active)
        if self.active:
            # on pressing F1 a second time, close switcher and send F1 key
            if event.keycode == keysyms.F1:
                if event.is_key_up():
                    self.__F1_released = True
                    return True
                elif self.__F1_released:
                    self.on_escape()
                    return False
                else:
                    # 防止長按F1而發生重複
                    return True
        return super(Switcher, self).process_key_event(event)

    def handle_additional_function_key(self, event):
        '''處理其他功能鍵'''
        if event.is_key_up():
            return False
        if event.keycode in (keysyms.comma, keysyms.minus):
            self.handler.on_page_up()
            return True
        if event.keycode in (keysyms.period, keysyms.equal):
            self.handler.on_page_down()
            return True
        return False
