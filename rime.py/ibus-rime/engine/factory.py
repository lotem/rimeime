# vim:set et sts=4 sw=4:

import ibus
import os
from rime import RimeSession

#from gettext import dgettext
#_  = lambda a : dgettext("ibus-rime", a)
_ = lambda a : a
N_ = lambda a : a

engine_path = os.path.dirname(__file__)
icon_path = os.path.normpath(os.path.join(engine_path, '..', 'icons'))

class EngineFactory(ibus.EngineFactoryBase):
    FACTORY_PATH = "/cn/zzsst/Rime/Factory"
    ENGINE_PATH = "/cn/zzsst/Rime/Engine"
    NAME = _("Rime")
    LANG = "zh_CN"
    ICON = os.path.join(icon_path, "zhung.png")
    AUTHORS = "GONG Chen <chen.sst@gmail.com>"
    CREDITS = "GPLv3"

    def __init__(self, bus):
        self.__bus = bus
        super(EngineFactory, self).__init__(bus)

        self.__id = 0
        self.__config = self.__bus.get_config()

        self.__config.connect("reloaded", self.__config_reloaded_cb)
        self.__config.connect("value-changed", self.__config_value_changed_cb)

    def create_engine(self, engine_name):
        if engine_name == "rime":
            self.__id += 1
            return RimeSession(self.__bus, "%s/%d" % (self.ENGINE_PATH, self.__id))
        return super(EngineFactory, self).create_engine(engine_name)

    def __config_reloaded_cb(self, config):
        pass

    def __config_value_changed_cb(self, config, section, name, value):
        pass

