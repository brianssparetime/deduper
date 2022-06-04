#!/usr/bin/env python3 

import os, sys, re
import operator
import argparse
import hashlib
import operator

cand =  [
   'foobar',
   'long_prefix_with_stuff here',
   'long_prefix_with_stuff here 1',
   'long_prefix_with_stuff here 2',
   'long_prefix_with_stuff here 3',
   'zeds dead baby',
]




def most_common_long_prefix(fns):

    if len(fns) == 1:
        return fns[0]
    prefixes = {}
    for fn in fns:
        prefix = None
        for t in fn.split():
            new_prefix = ' '.join([prefix, t]) if prefix else t
            if new_prefix in prefixes:
                prefixes[new_prefix] += 1
            else:
                prefixes[new_prefix] = 1
            prefix = new_prefix

    mclp = [ key for key in prefixes.keys() if prefixes[key] == max(prefixes.values()) ] 
    mclp.sort(key=len, reverse=True)
    return mclp[0]


print("candidates:")
for x in cand:
    print(x)
print('=============')
print(most_common_long_prefix(cand))