#!/usr/bin/env python
# encoding: utf-8

import random
import os
from diglib import alg
import time
from pathlib import Path
import logging

# trace file
trace_file = "/tmp/trace.csv"

# inference results for incremental refiment and input generation
dinvs = {}

def init(seed):

    # disable all log
    logging.disable(logging.CRITICAL)

def deinit():
    pass

def write_to_file(X, Y, pos):

    f = open(trace_file, 'w')

    assert(len(X[0]) == len(pos))

    # inv
    # pos = [1, 30, 44, 55, 123...]
    # vtrace1; I q; I r; I a; I b; I x; I y;
    inv = "vtrace1"
    for p in pos:
        inv += "; I x_{}".format(str(p))
    for i in range(0, len(Y[0])):
        inv += "; I y_{}".format(str(i))
    f.write(inv + "\n")

    # vtrace
    # X = [[2, 3, 4, 5, 6...], [2, 3, 4, 5, 6...], [2, 3, 4, 5, 6...]]
    # Y = [[2, 3, 4...], [2, 3, 4...], [2, 3, 4...]]
    # vtrace1; 0; 282; 8; 64; 282; 8
    trace_num = len(X)
    for i in range(0, trace_num):

        trace = "vtrace1"
        
        x_i = X[i]
        y_i = Y[i]

        for x in x_i:
            trace += "; {}".format(x)
        for y in y_i:
            trace += "; {}".format(y)

        f.write(trace + "\n")

    f.close()

def runDig(X, Y, pos):

    if len(X) == 0:
        return

    # write file
    write_to_file(X, Y, pos)

    # file read
    inp = Path(trace_file)

    # run dig
    dig = alg.DigTraces.mk(inp, None)
    dinvs = dig.start(seed=round(time.time(), 2), maxdeg=None)

    print(dinvs)

def mutate(buf, X, Y, pos):
    
    # do sampling stuff
    
    
    # constructing the mutated buff
    index = 0
    for loc in pos:
        buf[loc] = X[index]
        index += 1
    

    return buf

def fuzz(buf, add_buf, max_size, X, Y, pos):

    runDig()

    mutated_out = mutate(buf)

    return mutated_out

    