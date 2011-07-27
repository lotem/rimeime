# -*- coding: utf-8 -*-
# vim:set et sts=4 sw=4:

# TODO: 細分為保存寫作狀態的Context對象，和實現各種編輯操作的Editor

from builder import *

# 识别一组非整句的词组候选
is_phrase_list = lambda x: x and (len(x) != 1 or x[0].use_count != 0)

class Context:

    '''輸入上下文
    '''

    def __init__(self, schema):
        self.schema = schema
        # 上下文更新後通過on_update() callback反饋給前端
        self.__update_notifiers = []
        # Context調用Model完成輸入串到預測結果的轉換，並取得所有相關候選詞
        self.__model = Model(schema)
        # 以下讀取Context關心的設定值
        self.__delimiter = schema.get_config_char_sequence(u'Delimiter') or u' '
        self.__auto_delimit = schema.get_config_value(u'AutoDelimit') in (u'yes', u'true')
        self.__aux_length = int(schema.get_config_value(u'AuxLength') or 50)
        self.__auto_predict = schema.get_config_value(u'Predict') in (None, u'yes', u'true')
        prompt_char = schema.get_config_char_sequence(u'PromptChar')
        if prompt_char:
            alphabet = schema.get_config_char_sequence(u'Alphabet') or u'abcdefghijklmnopqrstuvwxyz'
            xlit = dict(zip(list(alphabet), list(prompt_char)))
            self.__translit = lambda s: u''.join([xlit[c] if c in xlit else c for c in s])
        else:
            self.__translit = None
        # 置為初始狀態
        self.__reset()

    def add_update_notifier(self, notifier):
        self.__update_notifiers.append(notifier)

    def notify_update(self):
        for notifier in self.__update_notifiers:
            notifier.on_update()

    def __reset(self, keep_context=False):
        # 輸入串，可以是字符序列（如在羅馬字解析方式下）或音節編碼的序列
        self.input = []
        # 錯誤狀態，非空時為一個Entry對象標記輸入串中輸入出錯的位置
        self.err = None
        # 當前候選詞，可能是多個單詞組成的詞組
        self.cur = []
        if not keep_context:
            # 清除手工編輯狀態
            self.sel = []
            self.confirmed = 0
            # 這個結構中保存的信息是詞庫查詢結果和由語言模型生成的轉換狀態，可用於增量計算
            self.info = self.__model.create_context_info()
        # 候選列表
        self.__candidates = []
        # 輸入串的介面展現形式，譬如字母變鍵名、音節自動添加隔音符之後的結果，及如何對應到原始輸入串
        self.__display = (u'', [0])
    
    def clear(self):
        self.__reset()
        self.notify_update()
    
    def is_empty(self):
        return not self.input
    
    def pop_input(self, till=-1):
        '''
        刪除輸入串末尾的編碼
        可選的參數，指定從某位置之後全刪掉；缺席時刪除最末一個編碼
        '''
        if till == -1:
            till = max(0, len(self.input) - 1)
        while len(self.input) > till:
            self.input.pop()
            # 刪除編碼後也清除末尾處自動添加上的隔音符
            if self.input and self.input[-1] == self.__delimiter[0]:
                self.input.pop()

    def commit(self):
        '''
        處理結果上屏事件
        當前算法，上屏動作由Engine發出，這是上屏後由Context響應的事件處理函數，並無上屏的具體操作
        '''
        if self.is_completed():
            # 學一遍
            self.__model.train(self, self.sel + self.cur)
            # 這樣清除Context可保留「上文信息」
            self.edit([])
        else:
            # 未完成轉換；捨棄結果
            self.clear()

    def edit(self, input, start_conversion=False):
        '''
        編輯輸入串
        替換輸入串內容並重新執行候選信息的計算
        '''
        self.__reset(keep_context=True)
        self.input = input
        if input:
            self.__model.query(self)
            m, n = self.info.m, self.info.n
            self.__calculate_display_string(input, self.info.d, n, m)
            if m != n:
                # 未完成整個輸入串的轉換
                self.err = Entry(None, m, n)
            elif start_conversion:
                # 轉換模式下需要顯示候選詞列表
                self.__update_candidates()
                return
            if self.__auto_predict:
                # 使用設定值Predict = yes，顯示預測的轉換結果，而不是輸入串本身，否則需要按空格手動轉換
                self.__predict()
        # 更新到前端
        self.notify_update()

    def has_error(self):
        '''錯誤的輸入串'''
        return self.err is not None

    def cancel_conversion(self):
        '''取消轉換，回到輸入串編輯狀態'''
        self.edit(self.input)

    def __predict(self):
        '''
        預測轉換結果
        依據未確認部份由Model算出的最優整句變換結果自動選詞
        '''
        # 處理的起始位置為句首或已確認部份之後
        # 如果Context中記錄了上文信息，則以位置-1（前一回上屏的末一個單詞）代替句首
        i = self.sel[-1].j if self.sel else (-1 if self.info.last else 0)
        # 取得詞組的後續部份或從後續位置起的最佳預測結果
        p = (self.sel[-1].next if self.sel else None) or self.info.pred[i]
        while p:
            # 組成當前詞組的單詞序列，如［中國｜功夫］
            s = p.get_all()
            # 詞組應排除上文的尾詞，方得到屬於當前Context的有效部份
            # 如上一次輸入了［我｜喜歡｜中國］，上文信息為［中國］
            # 又輸入［gungfu］，則組成詞組［（中國）｜功夫］，預測結果為［功夫］
            if s[0].i < 0:
                del s[0]
            if s:
                p = s[-1]
                # 選用當前詞組
                self.sel.extend(s)
            # 預測後續詞句
            i = p.j
            p = self.info.pred[i]
        # 返回結束位置
        return max(0, i)

    def home(self):
        '''選詞光標回退至句首'''
        if not self.being_converted():
            return False
        if self.cur[-1].j == self.info.m:
            j = 0  # 最短词
        else:
            j = -1  # 最长词
        # 清除手工選詞的記錄
        self.sel = []
        self.confirmed = 0
        # 顯示句首的候選詞
        self.__update_candidates(0, j)
        return True

    def end(self, start_conversion=False):
        '''選詞光標前進至句尾'''
        if not self.being_converted():
            if not start_conversion or self.has_error():
                return False
            # do a fresh new prediction in case of a full prediction is present
            self.sel = []
            self.confirmed = 0
        if len(self.sel) > self.confirmed:
            # 回到未確認部份的起始處
            del self.sel[self.confirmed:]
        else:
            # 預測轉換結果，並顯示句尾的候選詞
            self.__predict()
            if self.sel:
                del self.sel[-1]
        self.__update_candidates()
        return True

    def left(self):
        '''
        選詞光標左移
        首先向左縮小選區範圍，已縮小到最短編碼時選詞光標位置回退到上一個詞
        '''
        if not self.being_converted():
            return
        i = self.cur[0].i
        j = self.cur[-1].j
        # 選擇範圍是整個語句，且語句中包含多個詞組的，再向左則繞向最末一個詞組
        if i == 0 and j == self.info.m and len(self.cur) > 1:
            self.end()
            return
        # 按长度由大到小枚舉各種長度的子編碼串
        for k in range(j - 1, i, -1):
            # 遇到最長的、有候選詞的子編碼串，就以這個範圍生成候選詞列表
            if self.info.cand[i][k]:  # or is_phrase_list(self.info.fraz[i][k]):
                self.__update_candidates(i, k)
                return
        self.back()

    def right(self):
        '''
        選詞光標右移
        首先向右擴大選區範圍，已擴大到最長編碼串時選詞光標位置前進到下一個詞
        '''
        if not self.being_converted():
            return
        i = self.cur[0].i
        j = self.cur[-1].j
        for k in range(j + 1, self.info.m + 1):
            if self.info.cand[i][k] or is_phrase_list(self.info.fraz[i][k]):
                self.__update_candidates(i, k)
                return
        self.forth()

    def back(self):
        '''向後移動選詞光標'''
        if not self.being_converted():
            return False
        if self.sel:
            e = self.sel.pop()
            self.confirmed = min(self.confirmed, len(self.sel))
            i = e.i
            j = self.info.m - 1
            # 按长度由大到小枚舉各種長度的子編碼串
            for k in range(j, i, -1):
                # 遇到最長的、有候選詞的子編碼串，就以這個範圍生成候選詞列表
                if self.info.cand[i][k]:  # or is_phrase_list(self.info.fraz[i][k]):
                    self.__update_candidates(i, k)
                    return True
        return False

    def forth(self):
        '''向前移動選詞光標'''
        if not self.being_converted():
            return False
        i = self.cur[0].i
        j = self.cur[-1].j
        p = (self.sel[-1].next if self.sel else None) or self.info.pred[i]
        if p and p.j < self.info.m:
            self.sel.append(p)
            i = p.j
            j = 0
            # 找到前方最長的詞
            for k in range(self.info.m, i, -1):
                if self.info.cand[i][k] or is_phrase_list(self.info.fraz[i][k]):
                    j = k
                    break
            self.__update_candidates(i, j)
            return True
        return False

    def forward(self):
        '''確認當前候選詞，並將選詞光標移動到後續的詞'''
        c = self.cur
        if c:
            self.sel.extend(c)
            self.confirmed = len(self.sel)
            self.__update_candidates(c[-1].j)

    def __update_candidates(self, i=-1, j=-1):
        '''更新候選詞列表'''
        #print '__update_candidates:', i, j
        self.__candidates = self.__model.make_candidate_list(self, i, j)
        if self.__candidates:
            # 高亮顯示第一個候選詞
            self.cur = self.__candidates[0][1].get_all()
        else:
            # 無候選詞，將對應的編碼範圍標記為錯誤編碼
            err_pos = self.cur[-1].i if self.cur else 0
            self.err = Entry(None, err_pos, len(self.input))
            self.cur = []
        # 更新到前端
        self.notify_update()

    def select(self, e):
        '''從候選詞列表中手工選定一條候選詞'''
        self.cur = e.get_all()

    def being_converted(self):
        '''轉換模式'''
        return bool(self.cur)

    def is_completed(self):
        '''轉換完畢'''
        return self.cur and self.cur[-1].j == len(self.input)

    def __calculate_display_string(self, s, d, n, m):
        '''計算編碼展現串'''
        if n == 0:
            return
        t = [0 for i in range(n + 1)]
        p = []
        c = 0
        for i in range(n):
            if self.__auto_delimit and i > 0 and i in d and s[i - 1] not in self.__delimiter:
                p.append(self.__delimiter[0])
                c += 1
            t[i] = c
            w = self.__translit(s[i]) if self.__translit else s[i]
            p.append(w)
            c += len(w)
        t[-1] = c
        self.__display = (u''.join(p), t)

    def get_sentence(self):
        '''取得編輯中的文字'''
        if self.is_empty():
            return u''
        r = []
        rest = 0
        start = 0
        for s in self.sel:
            w = s.get_word()
            r.append(w)
            start += len(w)
            rest = s.j
        end = start
        for s in self.cur:
            w = s.get_word()
            r.append(w)
            end += len(w)
            rest = s.j
        if rest < self.info.n:
            s, t = self.__display
            if self.has_error():
                r.append(s[t[rest]:])
                diff = t[rest] - end
                start, end = t[self.err.i] - diff, t[self.err.j] - diff
            else:
                r.append(u'...')
        return u''.join(r)

    def get_commit_string(self):
        '''取得上屏文字'''
        i = 0
        r = []
        for s in self.sel + self.cur:
            r.append(s.get_word())
            i = s.j
        if i < len(self.input):
            s, t = self.__display
            r.append(s[t[i]:])
        return u''.join(r)

    def get_display_string(self):
        '''取得編碼串'''
        return self.__display[0]

    def get_input_string(self):
        '''取得輸入串'''
        return u''.join(self.input)
        
    def get_prompt(self):
        '''取得回顯串（已確認文字＋選擇區編碼）'''
        if self.is_empty():
            return u'', 0, 0
        r = []
        start = 0
        end = 0
        # 已確認文字＋未轉換的編碼＋錯誤的編碼
        if self.has_error():
            k = 0
            if self.confirmed > 0:
                for x in self.sel[:self.confirmed]:
                    w = x.get_word()
                    r.append(w)
                    start += len(w)
                    k = x.j
                end = start
            s, t = self.__display
            r.append(s[t[k]:])
            r.append(u'\u203a')
            diff = t[k] - end
            start, end = t[self.err.i] - diff, t[self.err.j] - diff
            return u''.join(r), start, end
        # 計算已經變換的文字長度
        selector = 0
        for x in self.sel:
            w = x.get_word()
            r.append(w)
            start += len(w)
            selector = x.j
        end = start
        # 正在變換的部份高亮顯示為編碼
        if self.cur:
            cursor = self.cur[-1].j
        else:
            cursor = selector
        if selector < self.info.n:
            s, t = self.__display
            # 插入光標符號
            if self.cur:
                p, q = t[selector], t[cursor]
                # 排除後面的空白
                if q > 0 and s[q - 1] == u' ':
                    q -= 1
            r.append(s[p:q])
            r.append(u'\u203a')
            diff = p - end
            start, end = p - diff, q - diff
        # 光標之後還有編碼，略去
        if cursor < self.info.n:
            r.append(u'...')
        return u''.join(r), start, end

    def get_candidates(self):
        '''取得當前候選詞'''
        return self.__candidates

    def delete_phrase(self, e):
        '''手工刪詞（未實作）'''
        pass

