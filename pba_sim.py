# PBA Simulation

import random
import sys
import time


def pba(B, C, R_last):
    """
    PBA Rate selection algorithm,
    Input:
        B: Buffer occupancy, value from 0-64, expresses seconds of buffer,
        C: Predicted available bandwith (express in Kb, 6.5 Mbps= 650 Kbps),
        R_last: Last downloaded video rate, initialized to the highest rate,

    Output: 
        R_next: Video rate for the next chunck    
    """

    bufferMax = 64
    chunk = 4 # seconds of each chunk
    B_safe =  .9 * bufferMax # Set to 90%
    B_risky = .3 * bufferMax # Set to 30%
    encodeRates = [235, 375, 560, 750, 1050, 1750, 2350, 3000, 3850, 4300]
    ref = encodeRates[0] # Init to min rate
    R_next = encodeRates[0] # Init to smallest 
    R_current = R_last

    if (B > (bufferMax - chunk)):
        time.sleep(B + chunk - bufferMax)

    for j in encodeRates:
        if ref <= C:
            ref = j 

    ref = max(R_current, ref)

    if (B <= B_risky):            
        ref = max(encodeRates[encodeRates.index(ref)-1], encodeRates[0])
        if (ref < R_last):
            R_next = max((B/chunk)+(C/ref)-1 > 2, encodeRates[0])
        else:
            R_next = ref
    elif (B >= B_safe):
        R_next = max(ref, R_last)
    else:
        if (ref <= R_last):
            R_next = R_last
        else:
            deltaB = chunk * (C/(ref-1))
            B_empty = bufferMax - B
            if (deltaB > 0.15 * B_empty):
                R_next = ref
            else:
                R_next = encodeRates[encodeRates.index(ref)-1]
    return R_next

if (__name__== '__main__'):
    B = 0 #init buffer value
    C = 235 #init prediction value
    R_last = 0 #init last value

    i = 0 # chunk increment
    
    while (i < 90):
        start_t = time.process_time()
        
        chunkSize = pba(B,C,R_last)

        fname = 'data/data' + str(chunkSize) + '.dat'
        file = open(fname, 'rb')
        dataFile = file.read()
        file.close()


        end_t = time.process_time()
        elapse_t = end_t - start_t

        extra_t = 4 - elapse_t
        total_t = elapse_t + extra_t
        
        # Uncomment to force each chunk to take 4 total seconds
        # Warning: full 6 minutes to complete cycle
        # time.sleep(extra_t)

        # print("Simulating downloading ", chunkSize, "Kb in (",
        #         elapse_t, "+", extra_t,"=", total_t)
        print("Simulating downloading ", chunkSize, "Kb in (",
                '{:.4}'.format(elapse_t),"), {B, C, R_last}: {",
                B, ",", C, ",", R_last, "}")

        # Set new values for next run
        R_last = chunkSize

        # Randomize C
        C_old = C

        # wildly varying rate switches
        # C = random.randint(100, 5000)

        # smoother rate changes
        if (C > 200 and C < 5000):
            C = C + random.randint(-1500, 1500)
        elif (C > 5000):
            C = C + random.randint(-1500, 0)
        else:
            C = C + random.randint(0, 1500)
        # Keep C positive
        if (C < 200):
            C = 200 
            

        # Modify buffer by percent based upon data rates
        B += round((C/C_old) * random.uniform(-1,1))
        # B should stay >= 0, make sure 0 is min
        if (B < 0):
            B = 0

        i += 1
        
        
        
