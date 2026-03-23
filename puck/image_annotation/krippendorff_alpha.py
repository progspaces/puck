#! /usr/bin/env python
# -*- coding: utf-8
'''
Python implementation of Krippendorff's alpha -- inter-rater reliability

(c)2011-17 Thomas Grill (http://grrrr.org)

Python version >= 2.4 required
'''
import math
import numpy as np
import json

def nominal_metric(a, b):
    # print(a)
    # print(b)
    return a != b

def dist1_metric(a,b):
    # use when you're comparing just every single point individually
    # print(a)
    # print(b)
    return math.dist(a,b)

def dist2_metric(a,b):
    #use when you're comparing groups of points
    a0,a1,a2,a3 = a
    b0,b1,b2,b3 = b
    return sum([math.dist(a0,b0),math.dist(a1,b1),math.dist(a2,b2),math.dist(a3,b3)])


def interval_metric(a, b):
    # print("metric")
    return (a-b)**2


def ratio_metric(a, b):
    return ((a-b)/(a+b))**2


def krippendorff_alpha(data, metric=interval_metric, force_vecmath=False, convert_items=float, missing_items=None):
    '''
    Calculate Krippendorff's alpha (inter-rater reliability):
    
    data is in the format
    [
        {unit1:value, unit2:value, ...},  # coder 1
        {unit1:value, unit3:value, ...},   # coder 2
        ...                            # more coders
    ]
    or 
    it is a sequence of (masked) sequences (list, numpy.array, numpy.ma.array, e.g.) with rows corresponding to coders and columns to items
    
    metric: function calculating the pairwise distance
    force_vecmath: force vector math for custom metrics (numpy required)
    convert_items: function for the type conversion of items (default: float)
    missing_items: indicator for missing items (default: None)
    '''
    
    # number of coders
    m = 3
    
    # set of constants identifying missing values
    if missing_items is None:
        maskitems = []
    else:
        maskitems = list(missing_items)
    if np is not None:
        maskitems.append(np.ma.masked_singleton)
    
    # convert input data to a dict of items
    units = {}
    for d in data:
        try:
            # try if d behaves as a dict
            diter = d.items()
            # print("AHHH")
            # print(diter)
        except AttributeError:
            # sequence assumed for d
            # print(d)
            diter = enumerate(d)
            # print(diter)
            
        for it, g in diter:
            # it is the Index
            # g is the value
            if g not in maskitems:
                try:
                    its = units[it]
                except KeyError:
                    its = []
                    units[it] = its
                its.append(convert_items(g))


    units = dict((it, d) for it, d in units.items() if len(d) > 1)  # units with pairable values
    # print("UNITS")
    # print(units)
    # units = data
    n = sum(len(pv) for pv in units.values())  # number of pairable values
    
    if n == 0:
        raise ValueError("No items to compare.")
    
    np_metric = (np is not None) and ((metric in (interval_metric, nominal_metric, dist1_metric, ratio_metric)) or force_vecmath)
    
    Do = 0.
    for grades in units.values():
        if np_metric:
            gr = np.asarray(grades)
            # print("grades")
            # print(gr)
            Du = sum(np.sum(metric(gr, gri)) for gri in gr)
        else:
            Du = sum(metric(gi, gj) for gi in grades for gj in grades)
        Do += Du/float(len(grades)-1)
    Do /= float(n)

    if Do == 0:
        return 1.

    De = 0.
    for g1 in units.values():
        if np_metric:
            d1 = np.asarray(g1)
            for g2 in units.values():
                De += sum(np.sum(metric(d1, gj)) for gj in g2)
        else:
            for g2 in units.values():
                De += sum(metric(gi, gj) for gi in g1 for gj in g2)
    De /= float(n*(n-1))

    return 1.-Do/De if (Do and De) else 1.


data = (
    "*    *    *    *    *    3    4    1    2    1    1    3    3    *    3", # coder A
    "1    *    2    1    3    3    4    3    *    *    *    *    *    *    *", # coder B
    "*    *    2    1    3    4    4    *    2    1    1    3    3    *    4", # coder C
)

missing = '*' # indicator for missing values
array = [d.split() for d in data]  # convert to 2D list of string items
# print(array)
# print("interval metric: %.3f" % krippendorff_alpha(array, interval_metric, missing_items=missing))

