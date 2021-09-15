#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep 15 11:44:58 2021

@author: noboru
"""
from packaging import version

req_version = {
    'natsort': '7.1.1',
    'astropy':'4.2',
    'numpy':'1.20.1',
    'pycromanager':'0.13.2',
    'matplotlib':'3.3.4',
    're':'2.2.1',
    'scipy':'1.6.1',
    'tqdm':'4.51.0'}

def colored(txt,c='green'):
    if c=='red':
        return '\x1b[0;30;41m%s\x1b[0m'%txt
    else:
        return '\x1b[0;30;42m%s\x1b[0m'%txt
import natsort
import astropy
import pycromanager
import numpy
import matplotlib
import re
import scipy
import tqdm
# print(natsort.__version__)
# print(astropy.__version__)
# print(numpy.__version__)
# print(pycromanager.__version__)
# print(matplotlib.__version__)

module = {'tqdm':tqdm,'scipy':scipy,'natsort':natsort,'astropy':astropy,'numpy':numpy,'pycromanager':pycromanager,'matplotlib':matplotlib,'re':re}


print("\t\t :::: Checking version :::\n")
for h in module:
    if version.parse(module[h].__version__) >= version.parse(req_version[h]):
        print("%s:\t%s\t[%s]"%(h,module[h].__version__,colored('OK')))
    else:
        print("%s:\t%s\t[%s]\t(%s required)"%(h,module[h].__version__,colored('NOK',c='red'),req_version[h]))
