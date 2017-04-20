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

    mc = MyMemcacheUtils.Client(['localhost:20174'], debug=1)
    mc.set('key1', 'goodgoodsutdy')
    s = list('goodgoodsutdygoodgoodsutdygoodgoodsutdygoodgoodsutdygoodgoodsutdy')
    for i in range(10000):
        random.shuffle(s)
        mc.set(str(i), "".join(s))
    value = mc.get('key1')
    print value
    slab_set = mc.get_slab_stats()
    print slab_set
    # print slab_set
    pprint(mc.get_keys([1, ]))
