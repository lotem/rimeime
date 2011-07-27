__all__ = (
        "ATTR_TYPE_UNDERLINE",
        "ATTR_TYPE_FOREGROUND",
        "ATTR_TYPE_BACKGROUND",
        "ATTR_UNDERLINE_NONE",
        "ATTR_UNDERLINE_SINGLE",
        "ATTR_UNDERLINE_DOUBLE",
        "ATTR_UNDERLINE_LOW",
        "ATTR_UNDERLINE_ERROR",
        "Attribute",
        "AttributeUnderline",
        "AttributeForeground",
        "AttributeBackground",
        "AttrList",
        "ARGB", "RGB",
        "Text",
    )

ATTR_TYPE_UNDERLINE = 1
ATTR_TYPE_FOREGROUND = 2
ATTR_TYPE_BACKGROUND = 3

ATTR_UNDERLINE_NONE = 0
ATTR_UNDERLINE_SINGLE = 1
ATTR_UNDERLINE_DOUBLE = 2
ATTR_UNDERLINE_LOW = 3
ATTR_UNDERLINE_ERROR = 4

class Attribute(object):
    def __init__ (self, type=0, value=0, start_index=0, end_index=0):
        self.__type = type
        self.__value = value
        self.__start_index = start_index
        self.__end_index = end_index

    def get_type(self):
        return self.__type

    def get_value(self):
        return self.__value

    def get_start_index(self):
        return self.__start_index

    def get_end_index(self):
        return self.__end_index

    type        = property(get_type)
    value       = property(get_value)
    start_index = property(get_start_index)
    end_index   = property(get_end_index)

class AttributeUnderline (Attribute):
    def __init__(self, value, start_index, end_index):
        Attribute.__init__ (self, ATTR_TYPE_UNDERLINE, value, start_index, end_index)

class AttributeForeground (Attribute):
    def __init__(self, value, start_index, end_index):
        Attribute.__init__ (self, ATTR_TYPE_FOREGROUND, value, start_index, end_index)

class AttributeBackground (Attribute):
    def __init__(self, value, start_index, end_index):
        Attribute.__init__ (self, ATTR_TYPE_BACKGROUND, value, start_index, end_index)

def ARGB (a, r, g, b):
    return ((a & 0xff)<<24) + ((r & 0xff) << 16) + ((g & 0xff) << 8) + (b & 0xff)

def RGB (r, g, b):
    return ARGB (255, r, g, b)

class AttrList(object):
    def __init__ (self, attrs = []):
        self._attrs = []
        for attr in attrs:
            self.append (attr)

    def append (self, attr):
        assert isinstance (attr, Attribute)
        self._attrs.append (attr)

    def __iter__ (self):
        return self._attrs.__iter__ ()

class Text(object):
    def __init__ (self, text="", attrs=None):
        self.__text = text
        self.__attrs = attrs

    def get_text(self):
        return self.__text

    def get_attributes(self):
        return self.__attrs

    text        = property(get_text)
    attributes  = property(get_attributes)

def test():
    attr_list = AttrList()
    attr_list.append (Attribute())
    attr_list.append (Attribute())
    attr_list.append (Attribute())
    attr_list.append (Attribute())
    attr_list.append (Attribute())
    text = Text("Hello", attr_list)

if __name__ == "__main__":
    test()
