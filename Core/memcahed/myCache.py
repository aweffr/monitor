# coding=utf-8

import MyMemcacheUtils


class MyCache(object):
    def __init__(self, addr):
        self.mc = MyMemcacheUtils.Client([addr], debug=0)

    def set(self, key, val):
        self.mc.set(key, val)

    def get(self, key):
        self.mc.get(key)


if __name__ == "__main__":
    import random
    from pprint import pprint

    mc = MyMemcacheUtils.Client(['101.37.77.231:20174'], debug=1)
    # mc.set("abc", "acd")
    # mc.set("lal", "lol")
    print mc.get("abc")
    print mc.get("lal")
    # print mc.get("rainbow")
