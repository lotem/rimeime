__all__ = (
        "LookupTable",
    )

from exception import *

class LookupTable:
    def __init__(self, page_size=5, cursor_pos=0, coursor_visible=True, round=False, candidates=None, labels=None):
        self.__cursor_pos = cursor_pos
        self.__cursor_visible = True
        self.__round = round
        if candidates == None:
            self.__candidates = list()
        else:
            self.__candidates = candidates
        self.set_page_size(page_size)
        self.set_labels(labels)

    def set_page_size(self, page_size):
        self.__page_size = page_size

    def get_page_size(self):
        return self.__page_size

    def get_current_page_size(self):
        nr_candidate = len(self.__candidates)
        nr_page, last_page_size = divmod(nr_candidate, self.__page_size)
        if self.__cursor_pos / self.__page_size == nr_page:
            return last_page_size
        else:
            return self.__page_size

    def set_labels(self, labels):
        if labels == None:
            self.__labels = list()
        else:
            self.__labels = labels

    def get_labels(self):
        return self.__labels

    def show_cursor(self, show = True):
        self.__cursor_visible = show

    def is_cursor_visible(self):
        return self.__cursor_visible

    def get_current_page_start(self):
        return (self.__cursor_pos / self.__page_size) * self.__page_size

    def set_cursor_pos(self, pos):
        if pos >= len(self.__candidates) or pos < 0:
            return False
        self.__cursor_pos = pos
        return True

    def get_cursor_pos(self):
        return self.__cursor_pos

    def get_cursor_pos_in_current_page(self):
        page, pos_in_page = divmod(self.__cursor_pos, self.__page_size)
        return pos_in_page

    def set_cursor_pos_in_current_page(self, pos):
        if pos < 0 or pos >= self.__page_size:
            return False
        pos += self.get_current_page_start()
        if pos >= len(self.__candidates):
            return False
        self.__cursor_pos = pos
        return True

    def page_up(self):
        if self.__cursor_pos < self.__page_size:
            if self.__round:
                nr_candidates = len(self.__candidates)
                max_page = nr_candidates / self.__page_size
                self.__cursor_pos += max_page * self.__page_size
                if self.__cursor_pos > nr_candidates - 1:
                    self.__cursor_pos = nr_candidates - 1
                return True
            else:
                if self.__cursor_pos > 0:
                    self.__cursor_pos = 0
                    return True
                return False

        self.__cursor_pos -= self.__page_size
        return True

    def page_down(self):
        current_page = self.__cursor_pos / self.__page_size
        nr_candidates = len(self.__candidates)
        max_page = nr_candidates / self.__page_size

        if current_page >= max_page:
            if self.__round:
                self.__cursor_pos %= self.__page_size
                return True
            else:
                return False

        pos = self.__cursor_pos + self.__page_size
        if pos >= nr_candidates:
            pos = nr_candidates - 1
        self.__cursor_pos = pos

        return True

    def cursor_up(self):
        if self.__cursor_pos == 0:
            if self.__round:
                self.__cursor_pos = len(self.__candidates) - 1
                return True
            else:
                return False

        self.__cursor_pos -= 1
        return True

    def cursor_down(self):
        if self.__cursor_pos == len(self.__candidates) - 1:
            if self.__round:
                self.__cursor_pos = 0
                return True
            else:
                return False

        self.__cursor_pos += 1
        return True

    def clean(self):
        self.__candidates = list()
        self.__cursor_pos = 0

    def append_candidate(self, text):
        self.__candidates.append(text)

    def get_candidate(self, index):
        return self.__candidates[index]

    def append_label(self, text):
        self.__labels.append(text)

    def get_label(self, index):
        return self.__labels[index]

    def get_candidates_in_current_page(self):
        page = self.__cursor_pos / self.__page_size
        start_index = page * self.__page_size
        end_index = min((page + 1) * self.__page_size, len(self.__candidates))
        return self.__candidates[start_index:end_index]

    def get_current_candidate(self):
        return self.__candidates [self.__cursor_pos]

    def get_number_of_candidates(self):
        return len(self.__candidates)

    def __len__(self):
        return self.get_number_of_candidates()

    def get_current_page_as_lookup_table(self):
        candidates = self.get_candidates_in_current_page()
        return LookupTable(self.__page_size,
                           self.__cursor_pos % self.__page_size,
                           self.__cursor_visible,
                           self.__round,
                           candidates,
                           self.__labels)

def test():
    t = LookupTable()
    # attrs = AttrList()
    # attrs.append(AttributeBackground(RGB(233, 0,1), 0, 3))
    # attrs.append(AttributeUnderline(1, 3, 5))
    t.append_candidate("Hello")
    t = t.get_current_page_as_lookup_table()

if __name__ == "__main__":
    test()
