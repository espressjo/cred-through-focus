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
    'pycromanager':'0.13.1',
    'matplotlib':'3.3.4',
    're':'2.2.1',
    'scipy':'1.6.1',
    'tqdm':'4.51.0',
    'seaborn': '0.11.1'}

def colored(txt,c='green'):
    if c=='red':
        return '\x1b[0;30;41m%s\x1b[0m'%txt
    else:
        return '\x1b[0;30;42m%s\x1b[0m'%txt

print("\t\t :::: Checking version :::\n")
module = {}
try:
    import natsort
    module['natsort'] = natsort
except:
    del req_version['natsort']
    print("%s:\tNot installed\t[%s]"%('natsort',colored('NOK',c='red')))
try:
    import seaborn
    module['seaborn'] = seaborn
except:
    del req_version['seaborn']
    print("%s:\tNot installed\t[%s]"%('seaborn',colored('NOK',c='red')))
try:
    import astropy
    module['astropy'] = astropy
except:
    del req_version['astropy']
    print("%s:\tNot installed\t[%s]"%('astropy',colored('NOK',c='red')))
try:
    import pycromanager
    module['pycromanager'] = pycromanager
except:
    del req_version['pycromanager']
    print("%s:\tNot installed\t[%s]"%('pycromanager',colored('NOK',c='red')))
try:
    import numpy
    module['numpy'] = numpy
except:
    del req_version['numpy']
    print("%s:\tNot installed\t[%s]"%('numpy',colored('NOK',c='red')))
try:
    import matplotlib
    module['matplotlib'] = matplotlib
except:
    del req_version['matplotlib']
    print("%s:\tNot installed\t[%s]"%('matplotlib',colored('NOK',c='red')))
try:
    import re
    module['re'] = re
except:
    del req_version['re']
    print("%s:\tNot installed\t[%s]"%('re',colored('NOK',c='red')))
try:
    import scipy
    module['scipy'] = scipy
except:
    del req_version['scipy']
    print("%s:\tNot installed\t[%s]"%('scipy',colored('NOK',c='red')))
try:
    import tqdm
    module['tqdm'] = tqdm
except:
    del req_version['tqdm']
    print("%s:\tNot installed\t[%s]"%('tqdm',colored('NOK',c='red')))


for h in req_version:

    if version.parse(module[h].__version__) >= version.parse(req_version[h]):
        print("%s:\t%s\t[%s]"%(h,module[h].__version__,colored('OK')))
    else:
        print("%s:\t%s\t[%s]\t(%s required)"%(h,module[h].__version__,colored('NOK',c='red'),req_version[h]))
