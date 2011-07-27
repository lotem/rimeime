# vim:set et sts=4 sw=4:

import os
import sys
import getopt
import ibus
import gobject
import factory

class IMApp:
    def __init__(self, exec_by_ibus):
        self.__component = ibus.Component("cn.zzsst.Rime",
                                          "Rime Component",
                                          "0.1.0",
                                          "GPL",
                                          "GONG Chen <chen.sst@gmail.com>")
        self.__component.add_engine("rime",
                                    "Rime",
                                    "ibus-rime, powered by Rime Input Method Engine",
                                    "zh_CN",
                                    "GPL",
                                    "GONG Chen <chen.sst@gmail.com>",
                                    "",
                                    "en")
        self.__mainloop = gobject.MainLoop()
        self.__bus = ibus.Bus()
        self.__bus.connect("destroy", self.__bus_destroy_cb)
        self.__factory = factory.EngineFactory(self.__bus)
        if exec_by_ibus:
            self.__bus.request_name("cn.zzsst.Rime", 0)
        else:
            self.__bus.register_component(self.__component)

    def run(self):
        self.__mainloop.run()

    def __bus_destroy_cb(self, bus):
        self.__mainloop.quit()


def print_help(out, v = 0):
    print >> out, "-i, --ibus             execute by ibus."
    print >> out, "-h, --help             show this message."
    print >> out, "-d, --daemonize        daemonize ibus"
    sys.exit(v)

def main():
    daemonize = False
    exec_by_ibus = False
    shortopt = "hdi"
    longopt = ["help", "daemonize", "ibus"]
    try:
        opts, args = getopt.getopt(sys.argv[1:], shortopt, longopt)
    except getopt.GetoptError, err:
        print_help(sys.stderr, 1)

    for o, a in opts:
        if o in ("-h", "--help"):
            print_help(sys.stdout)
        elif o in ("-d", "--daemonize"):
            daemonize = True
        elif o in ("-i", "--ibus"):
            exec_by_ibus = True
        else:
            print >> sys.stderr, "Unknown argument: %s" % o
            print_help(sys.stderr, 1)

    if daemonize:
        if os.fork():
            sys.exit()

    IMApp(exec_by_ibus).run()

if __name__ == "__main__":
    main()
