#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
from core import *


class Composer(Processor):

    '''完成按鍵到編碼串的轉換'''

    __factories = dict()

    @classmethod
    def register_factory(cls, composer_name, factory):
        cls.__factories[composer_name] = factory

    @classmethod
    def get_factory(cls, composer_name):
        return cls.__factories[composer_name]

    @classmethod
    def create(cls, schema):
        composer_name = schema.get_config_value(u'Parser')
        return cls.get_factory(composer_name) (schema)

    def __init__(self, schema):
        self.schema = schema
        # 從Schema中讀取用到的一些設定值
        self.auto_prompt = schema.get_config_value(u'AutoPrompt') in (u'yes', u'true')
        self.auto_predict = schema.get_config_value(u'Predict') in (None, u'yes', u'true')
        self.alphabet = schema.get_config_char_sequence(u'Alphabet') or u'abcdefghijklmnopqrstuvwxyz'
        self.initial = self.alphabet.split(None, 1)[0]
        self.delimiter = schema.get_config_char_sequence(u'Delimiter') or u' '
        self.quote = schema.get_config_char_sequence('Quote') or u'`'
        acc = (schema.get_config_char_sequence('Acceptable') or \
               u'''ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz
                   0123456789!@#$%^&*()`~-_=+[{]}\\|;:'",<.>/?''').split(None, 1)
        self.acceptable = lambda x: x == u' ' or any([x in s for s in acc])
        self.initial_acceptable = lambda x: x in self.quote or x in acc[0]
        get_rules = lambda f, key: [f(r.split()) for r in schema.get_config_list(key)]
        compile_repl_pattern = lambda x: (re.compile(x[0]), x[1])
        transform = lambda s, r: r[0].sub(r[1], s)
        self.xform_rules = get_rules(compile_repl_pattern, u'TransformRule')
        self.xform = lambda s: reduce(transform, self.xform_rules, s)
        punct_mapping = lambda(x, y): (x, (0, y.split(u' ')) if u' ' in y else \
                                           (2, y.split(u'~', 1)) if u'~' in y else \
                                           (1, y))
        self.__punct = dict([punct_mapping(c.split(None, 1)) for c in schema.get_config_list(u'Punct')])
        key_mapping = lambda(x, y): (keysyms.name_to_keycode(x), keysyms.name_to_keycode(y))
        self.__edit_keys = dict([key_mapping(c.split(None, 1)) for c in schema.get_config_list(u'EditKey')])
        # 初始化一個Spelling對象
        self.spelling = u''

    def start_raw_mode(self, ch):
        '''進入西文模式

        ch為進入西文模式的前導編碼
        用Spelling來表現西文模式下的輸入串（反白顯示且不作為編碼輸入）

        '''
        self.spelling = ch
        return Spelling(self.spelling)

    def process_raw_mode(self, event):
        '''處理西文模式下的輸入
        '''
        p = self.spelling
        ch = event.get_char()
        if event.keycode == keysyms.Return:
            if len(p) > 1 and p[0] in self.quote:
                # 以quote做前導的西文，上屏時不包含quote
                return Commit(p[1:]) 
            else:
                return Commit(p)
        if event.keycode == keysyms.Escape:
            self.clear()
            return Spelling()
        if event.keycode == keysyms.BackSpace:
            self.spelling = p[:-1]
            return Spelling(self.spelling)
        if ch in self.quote and p[0] in self.quote:
            # 成對的quote與引文一同上屏
            return Commit(p + ch)
        if self.acceptable(ch):
            self.spelling += ch
            return Spelling(self.spelling)
        return True

    def check_punct(self, event):
        '''查標點輸入

        結果中包含查表所得的標點符號

        '''
        ch = event.get_char()
        if ch in self.__punct:
            if event.mask & modifier.RELEASE_MASK:
                return True, None
            p = self.__punct[ch]
            if p[0] == 1:
                # 唯一的標點，直接上屏
                return True, p[1]
            elif p[0] == 2:
                # 成對使用的標號，如以"輸入“”，前後引交替著出
                x = p[1][0]
                p[1].reverse()
                return True, x
            else:
                # 一鍵表示多種標點，反覆按鍵輪循
                return True, p[1]
        return False, None

    def check_edit_key(self, event):
        '''檢查自定義編輯鍵

        擊自定義編輯鍵，會返回一個偽造的等效預設編輯鍵

        '''
        if not event.coined and event.keycode in self.__edit_keys:
            return KeyEvent(self.__edit_keys[event.keycode], 0, coined=event)
        return None


class RomanComposer(Composer):
    def __init__(self, schema):
        super(RomanComposer, self).__init__(schema)
        self.clear()
    def clear(self):
        self.__input = []
        self.spelling = u''
    def is_empty(self):
        return not bool(self.__input)
    def __get_input(self):
        if self.xform_rules:
            # apply transform rules
            s = self.xform(u''.join(self.__input))
            return list(s)
        else:
            return self.__input[:]
    def process_input(self, event, ctx):
        if event.mask & modifier.RELEASE_MASK:
            return False
        if self.spelling:
            return self.process_raw_mode(event)
        # disable input in conversion mode
        if not self.auto_prompt and ctx.being_converted():
            return False
        # normal mode
        if event.keycode == keysyms.Escape:
            self.clear()
            if ctx.has_error():
                ctx.edit([])
                return True
            return False
        if event.keycode == keysyms.BackSpace:
            if self.is_empty():
                return False
            self.__input.pop()
            ctx.input = self.__get_input()
            return []
        if event.keycode == keysyms.space:
            return False
        ch = event.get_char()
        if self.is_empty() and ch in self.initial or \
           not self.is_empty() and (ch in self.alphabet or ch in self.delimiter):
            self.__input.append(ch)
            ctx.input = self.__get_input()
            return []
        # 進入西文模式
        if self.is_empty() and self.initial_acceptable(ch):
            return self.start_raw_mode(ch)
        # 在輸入串後追加quote按鍵，轉入西文模式
        if ch in self.quote and not self.is_empty() and self.__input[0] not in self.quote:
            self.spelling = u''.join(self.__input)
            self.__input = []
            ctx.edit([])
            return Spelling(self.spelling)
        # 不可轉換的輸入串，追加符號後轉入西文模式
        if ctx.err and self.acceptable(ch) and not ch in self.alphabet:
            self.spelling = u''.join(self.__input)
            self.__input = []
            ctx.edit([])
            return self.process_raw_mode(event)
        # unused
        return False

class TableComposer(Composer):
    def __init__(self, schema):
        super(TableComposer, self).__init__(schema)
        self.__auto_commit_keyword_length = int(schema.get_config_value(u'AutoCommitKeywordLength') or schema.get_config_value(u'MaxKeywordLength') or u'4')
        self.clear()
    def clear(self):
        self.__input = []
        self.__keyword = []
        self.spelling = u''
    def is_empty(self):
        return not bool(self.__input) and not bool(self.__keyword)
    def __is_keyword_empty(self):
        return not bool(self.__keyword)
    def __get_keyword(self):
        if self.xform_rules:
            # apply transform rules
            return self.xform(u''.join(self.__keyword))
        else:
            return u''.join(self.__keyword)
    def process_input(self, event, ctx):
        if event.mask & modifier.RELEASE_MASK:
            return False
        if self.spelling:
            return self.process_raw_mode(event)
        # disable input in conversion mode
        if not self.auto_prompt and ctx.being_converted():
            return False
        # normal mode
        if event.keycode == keysyms.Escape:
            self.clear()
            return False
        if event.keycode == keysyms.Return:
            self.clear()
            return False
        if event.keycode == keysyms.space:
            self.clear()
            return False
        if event.keycode == keysyms.BackSpace:
            if self.is_empty():
                return False
            if self.__is_keyword_empty():
                self.__keyword = self.__input.pop()
            # back a character
            self.__keyword.pop()
            if self.__is_keyword_empty():
                ctx.pop_input()
            else:
                ctx.input[-1] = self.__get_keyword()
            return []
        ch = event.get_char()
        # finish current keyword
        if not self.is_empty() and ch in self.delimiter:
            if not self.__is_keyword_empty():
                self.__input.append(self.__keyword)
            self.__input.append([ch])
            self.__keyword = []
            return [ch]
        if ch in self.initial:
            # auto-commit keywords with max keyword length
            is_keword_complete = len(self.__keyword) == self.__auto_commit_keyword_length
            if is_keword_complete:
                self.__input.append(self.__keyword)
                self.__keyword = []
            # start a new keyword
            if self.__is_keyword_empty():
                self.__keyword.append(ch)
                result = []
                # add default delimiter char into continual input
                if self.__input and self.__input[-1][0] not in self.delimiter:
                    result.append(self.delimiter[0])
                result.append(self.__get_keyword())
                return result
        if not self.__is_keyword_empty():
            # continue current keyword
            if ch in self.alphabet:
                self.__keyword.append(ch)
                ctx.input[-1] = self.__get_keyword()
                return []
        # start raw mode
        if self.is_empty() and self.initial_acceptable(ch):
            return self.start_raw_mode(ch)
        # unused
        return False

class GroupComposer(Composer):
    def __init__(self, schema):
        super(GroupComposer, self).__init__(schema)
        self.__prompt_pattern = schema.get_config_char_sequence(u'PromptPattern') or u'%s\u203a'
        self.__key_groups = schema.get_config_value(u'KeyGroups').split()
        self.__code_groups = schema.get_config_value(u'CodeGroups').split()
        self.__group_count = len(self.__key_groups)
        self.clear()
    def clear(self):
        self.__slots = [u''] * self.__group_count
        self.__cursor = 0
    def is_empty(self):
        return not any(self.__slots)
    def __get_spelling(self, first):
        text = self.__prompt_pattern % u''.join(self.__slots)
        start = end = 0
        k = self.__prompt_pattern.find(u'%s')
        if k != -1:
            start = k
            end = start + len(text) - len(self.__prompt_pattern) + len(u'%s')
        padding = None if first or self.auto_predict else self.delimiter[0]
        return Spelling(text, start=start, end=end, padding=padding)
    def process_input(self, event, ctx):
        if event.mask & modifier.RELEASE_MASK:
            return False
        if not self.auto_prompt and ctx.being_converted():
            return False
        if event.keycode == keysyms.Escape:
            self.clear()
            return False
        if event.keycode == keysyms.BackSpace:
            if self.is_empty():
                return False
            # delete last one symbol from current keyword
            j = self.__group_count - 1
            while j > 0 and not self.__slots[j]:
                j -= 1
            self.__slots[j] = u''
            while j > 0 and not self.__slots[j]:
                j -= 1
            self.__cursor = j
            if not self.is_empty():
                # update spelling
                return self.__get_spelling(ctx.is_empty())
            else:
                # keyword disposed
                self.clear()
                return Spelling()
        if event.keycode == keysyms.space:
            if self.is_empty():
                return False
            result = u''.join(self.__slots)
            self.clear()
            return [result] if ctx.is_empty() else [self.delimiter[0], result]
        # handle grouping input
        ch = event.get_char()
        k = self.__cursor
        while ch not in self.__key_groups[k]:
            k += 1
            if k >= self.__group_count:
                k = 0
            if k == self.__cursor:
                if self.is_empty():
                    return False
                else:
                    return True
        # update current keyword
        idx = self.__key_groups[k].index(ch)
        self.__slots[k] = self.__code_groups[k][idx]
        k += 1
        if k >= self.__group_count:
            keyword = u''.join(self.__slots)
            self.clear()
            return [keyword] if ctx.is_empty() else [self.delimiter[0], keyword]
        else:
            self.__cursor = k
            return self.__get_spelling(ctx.is_empty())

class ComboComposer(Composer):
    def __init__(self, schema):
        super(ComboComposer, self).__init__(schema)
        self.__prompt_pattern = schema.get_config_char_sequence(u'PromptPattern') or u'\u2039%s\u203a'
        self.__combo_keys = schema.get_config_char_sequence(u'ComboKeys') or u''
        self.__combo_codes = schema.get_config_char_sequence(u'ComboCodes') or u''
        self.__combo_max_length = min(len(self.__combo_keys), len(self.__combo_codes))
        self.__combo_space = schema.get_config_value(u'ComboSpace') or u'_'
        self.__combo = set()
        self.__held = set()
    def clear(self):
        self.__combo.clear()
        self.__held.clear()
    def is_empty(self):
        return not bool(self.__held)
    def __get_spelling(self, first):
        text = self.__prompt_pattern % self.__get_combo_string()
        start = end = 0
        k = self.__prompt_pattern.find(u'%s')
        if k != -1:
            start = k
            end = start + len(text) - len(self.__prompt_pattern) + len(u'%s')
        padding = None if first or self.auto_predict else self.delimiter[0]
        return Spelling(text, start=start, end=end, padding=padding)
    def __commit_combo(self, first):
        k = self.__get_combo_string()
        self.clear()
        #print '__commit_combo', k
        if k == self.__combo_space:
            return KeyEvent(keysyms.space, 0, coined=True)
        elif not k:
            return Spelling()
        else:
            return [k] if first else [self.delimiter[0], k]
    def __get_combo_string(self):
        s = u''.join([self.__combo_codes[i] for i in range(self.__combo_max_length) \
                                                 if self.__combo_keys[i] in self.__combo])
        return self.xform(s)
    def process_input(self, event, ctx):
        # handle combo input
        ch = event.get_char()
        if event.mask & modifier.RELEASE_MASK:
            if ch in self.__held:
                #print 'released:', ch
                self.__held.remove(ch)
                if self.is_empty():
                    return self.__commit_combo(ctx.is_empty())
                return True
            return False
        if ch in self.__combo_keys:
            #print 'pressed:', ch
            self.__combo.add(ch)
            self.__held.add(ch)
            return self.__get_spelling(ctx.is_empty())
        # non-combo keys
        if not self.is_empty():
            self.clear()
            return Spelling()
        return False


def initialize():
    Composer.register_factory('roman', RomanComposer)
    Composer.register_factory('table', TableComposer)
    Composer.register_factory('grouping', GroupComposer)
    Composer.register_factory('combo', ComboComposer)

initialize()
