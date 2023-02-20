#!/usr/bin/env python
# encoding: utf-8

import random
import os
import numpy as np
from io import BytesIO
from sklearn.multioutput import MultiOutputRegressor
from sklearn.svm import SVR

svr = SVR(epsilon=0.2)
mor = MultiOutputRegressor(svr)

def init(seed):
    """
    Called once when AFLFuzz starts up. Used to seed our RNG.

    @type seed: int
    @param seed: A 32-bit random value
    """
    random.seed(seed)


def deinit():
    pass

def bytearray_to_np(b):
    np_bytes = BytesIO(b)
    return np.load(np_bytes, allow_pickle=True)

def update_reg(X, Y):
    
    if (len(X) == 0):
        return

    X_new = numpy.array([numpy.array(y) for y in Y])
    Y_new = numpy.array([numpy.array(y) for y in Y])
    mor = mor.fit(X, Y)

def fuzz(buf, add_buf, max_size, X, Y, pos):

    update_reg(X, Y) 

    mutated_out = bytearray(100)
    return mutated_out