#!/usr/bin/env python
# encoding: utf-8

import sympy
import random
from diglib.helpers.miscs import Miscs
import os
from diglib import alg
import time
from pathlib import Path
import logging
from diglib.helpers.z3utils import Z3
import walk_sample
import numpy as np

# trace file
trace_file = "/tmp/trace.csv"

# inference results for incremental refiment and input generation
dinvs = {}

# samples [x1, x2, x3, x4] 2 times:
# [[1, 1, 1, 1], [2, 2, 2, 2]]
samples = []

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

def get_coeff(invs):

    eq_rhs = []
    eq = []
    for inv in invs:
        s = str(inv)
        expr = sympy.parse_expr(s)
        rhs = expr.rhs
        if rhs.is_integer:
            eq_rhs.append(int(expr.rhs))
        else:
            continue

        colist = []
        coes = expr.lhs.as_coefficients_dict()
        for var in pos_vars:
            sym = sympy.symbols(var)
            if sym in coes:
                colist.append(int(coes[sym]))
            else:
                colist.append(0)
        eq.append(colist)

    return eq_rhs, eq

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

def mutate(buf, X, Y, pos):
    
    # do sampling stuff
    sample = []
    
    loc = list(dinvs.keys())[0]
    cinvs = dinvs[loc].cinvs
    leq_rhs, leq = get_coeff(cinvs.octs)
    eq_rhs, eq = get_coeff(cinvs.eqts)
    if len(eq) == 0:
        eq_rhs.append(0)
        eq.append([0] * len(pos_vars))
    if len(leq) == 0:
        leq_rhs.append(0)
        leq.append([0] * len(pos_vars))
    leq_rhs = np.array(leq_rhs)
    leq = np.array(leq)
    eq_rhs = np.array(eq_rhs)
    eq = np.array(eq)
    samples = walk_sample.sample(eq, eq_rhs, leq, leq_rhs)
    
    if len(samples) > 0:
        # constructing the mutated buff
        index = 0
        for loc in pos:
            buf[loc] = samples[0][index]
            index += 1
        
    else:
        pass


    return buf

def fuzz(buf, add_buf, max_size, X, Y, pos):

    if len(dinvs) == 0:
        runDig(X, Y, pos)

    mutated_out = mutate(buf, X, Y, pos)

    return mutated_out

    