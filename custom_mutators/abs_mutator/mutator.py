#!/usr/bin/env python
# encoding: utf-8


import random

import dig


def init(seed):
    pass

def fuzz_count(buf):
    return cnt

def fuzz(buf, add_buf, max_size):
    return mutated_out

def describe(max_description_length):
    return "description_of_current_mutation"

def post_process(buf):
    return out_buf

def init_trim(buf):
    return cnt

def trim():
    pass
    # return out_buf

def post_trim(success):
    pass

def havoc_mutation(buf, max_size):
    return buf

def havoc_mutation_probability():
    return probability # int in [0, 100]

def queue_get(filename):
    return True

def fuzz_send(buf):
    pass

def queue_new_entry(filename_new_queue, filename_orig_queue):
    return False

def introspection():
    pass

def deinit():  # optional for Python
    pass