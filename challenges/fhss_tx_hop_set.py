# this module will be imported in the into your flowgraph
    #generate 60 seconds worth of hop data
import random
import time
import math

def mkhopset(seed,randlow,randhigh,hps,seconds):
    # self.message_port_pub(pmt.intern('debug'), pmt.intern('Generating New Hopset'))
    # random.seed(math.ceil(time.time()))       
    random.seed(seed)       
    hops = []
    for i in range(int(math.ceil(hps*seconds))):
        hops.append(random.randint(randlow,randhigh))
    return hops