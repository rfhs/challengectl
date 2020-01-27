import os
import time

def tx():
    tx_cycle=0
    while True:
        print("Starting TX "+str(tx_cycle))
        os.system('python ft8_tx.py odd')# 2> /dev/null')
        time.sleep(8)
        print("Exiting TX "+str(tx_cycle))
        tx_cycle += 1
tx()
