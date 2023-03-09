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
import pickle  

# trace file
trace_file = "/tmp/trace.csv"

# inference results for incremental refiment and input generation
dinvs_file = "/tmp/dinvs.pkl"
pos_file = "/tmp/pos.pkl"

# leq_rhs = np.array()
# leq = np.array()
# eq_rhs = np.array()
# eq = np.array()

# import os
os.environ["INFERRED"] = "1"
inferred = 0

def init(seed):

    # disable all log
    logging.disable(logging.CRITICAL)

def deinit():
    pass

def write_to_file(X, Y, pos):

    f = open(trace_file, 'w')

    assert(len(X[0]) == len(pos))
    assert(len(pos) > 0)

    # inv
    # pos = [1, 30, 44, 55, 123...]
    # vtrace1; I q; I r; I a; I b; I x; I y;
    pos_vars = []
    inv = "vtrace1"
    for p in pos:
        inv += "; I x_{}".format(str(p))
        pos_vars.append("x_{}".format(str(p)))
    for i in range(0, len(Y[0])):
        inv += "; I y_{}".format(str(i))
        pos_vars.append("y_{}".format(str(i)))
    f.write(inv + "\n")

    file = open(pos_file, 'wb')
    pickle.dump(pos_vars, file)
    file.close()

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

def get_coeff(invs, pos_vars):

    eq_rhs = []
    eq = []
    for inv in invs:
        s = str(inv)
        expr = sympy.parse_expr(s)

        # sympy cannot parse ==
        if expr == False:
            l = s.split(" ")
            if len(l) == 3 and l[1] == "==":
                rhs = int(l[2])
                eq_rhs.append(rhs)

                colist = []
                for var in pos_vars:
                    if l[0] == sympy.symbols(var):
                        colist.append(1)
                    else:
                        colist.append(0)
                eq.append(colist)

            else:
                continue
        else:

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

    assert(len(X) > 0)

    # write file
    write_to_file(X, Y, pos)

    # file read
    inp = Path(trace_file)

    # run dig
    try:
        dig = alg.DigTraces.mk(inp, None)
        dinvs = dig.start(seed=round(time.time(), 2), maxdeg=None)
    except:
        pass
    file = open(dinvs_file, 'wb')
    pickle.dump(dinvs, file)
    file.close()

def mutate(buf, X, Y, pos):
    
    file = open(dinvs_file, 'rb')
    dinvs = pickle.load(file)
    file.close()

    file = open(pos_file, 'rb')
    pos_vars = pickle.load(file)
    file.close()

    if len(dinvs) == 0:
        return buf

    # do sampling stuff
    sample = []
    
    # if os.environ.get("INFERRED", "2") == "2":
    loc = list(dinvs.keys())[0]
    cinvs = dinvs[loc].cinvs
    leq_rhs, leq = get_coeff(cinvs.octs, pos_vars)
    eq_rhs, eq = get_coeff(cinvs.eqts, pos_vars)
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

    count = 1 # number of samples
    samples = []
    try:
        samples = walk_sample.sample(eq, eq_rhs, leq, leq_rhs, 1)
    except:
        pass

    # samples [x1, x2, x3, x4] 2 times:
    # [[1, 1, 1, 1], [2, 2, 2, 2]], each list is a set of byte values
    if len(samples) > 0:
        # constructing the mutated buff
        index = 0
        for loc in pos:
            if samples[0][index] < 0 or samples[0][index] > 256:
                buf[loc] = 0
            else:
                buf[loc] = int(samples[0][index])
            index += 1
    else:
        pass

    return buf

def fuzz(buf, add_buf, max_size, X, Y, pos):

    
    if os.environ.get("INFERRED", "2") == "2" and len(pos) > 0:
        runDig(X, Y, pos)

    mutated_out = mutate(buf, X, Y, pos)

    return mutated_out

    