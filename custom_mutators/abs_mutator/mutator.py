#!/usr/bin/env python
# encoding: utf-8

import random
import os
import numpy as np
from sklearn.linear_model import LinearRegression

def init(seed):
    """
    Called once when AFLFuzz starts up. Used to seed our RNG.

    @type seed: int
    @param seed: A 32-bit random value
    """
    random.seed(seed)


def deinit():
    pass


def fuzz(buf, add_buf, max_size):

    x_new = x = np.array([6, 16, 26, 36, 46, 56]).reshape((-1, 1))
    y = np.array([4, 23, 10, 12, 22, 35])
    y_new = np.array([4, 11, 55, 44, 123, 33])

    reg = LinearRegression().fit(x, y)

    # Calculate the corresponding values of the other input variables
    x_new_other = (y_new - reg.intercept_)
    for i, coef in enumerate(reg.coef_):
        x_new_other /= coef
        x_new[:, i] = x_new_other

    mutated_out = x_new.tobytes()

    return mutated_out