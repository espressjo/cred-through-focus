#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 28 14:36:29 2021

@author: espressjo
"""
from astropy.io import fits
from os import listdir,getcwd
from os.path import join
from natsort import natsorted
ls = [f for f in listdir(getcwd()) if '.fits' in f]
ls = natsorted(ls)
with open(join(getcwd(),'log.csv'),'w') as f:
    f.write("Filename,Date,Source,Bias,Flat,FPS,Exposure,Conversion gain,HDR mode,wavelength,Puissance laser,Relay\n")
    for f in ls:
        H = fits.getheader()
        line =""
        line+=f.replace('.fits','')+','
        line+=H['DATE']+','
        line+="Thorlabs accordable,"
        if H['BIAS']==1:
            line+="yes,"
        else:
            line+="no,"
        line+="no"
        line+="%.1f,"%H['FPS']
        line+="%.3f,"%H['EXPTIME']
        line+="%s,"%H['GAIN']
        line+="%s,"%H['HDR']
        line+="%.1f,"%H['WAVEL']
        line+="%.3f,"%H['SOURCEP']
        line+="%s\n"%H['ORELAY']
        f.write(line)
        
        
        
        
        