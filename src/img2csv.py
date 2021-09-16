#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 28 14:36:29 2021
Optional arguments are; 
    --list    Will list all the image folders in working directory defined in cfg file.
    --dir     run the analysis in specific directory located in working dir. (e.g., --dir=20210921105411 )
    --path    run the analysis in specific directory (e.g., --path=C:\\Users\\Hexagon\\20210921105411 )
@author: espressjo
"""
from astropy.io import fits
from os import listdir,getcwd
from os.path import join
from natsort import natsorted
from config_file_cred import cfg_file


def help():
    print('\t::: img2csv.py :::')
    print('')
    print('\t--list\tWill list all the image folders in working directory defined in cfg file.')
    print('\t--dir\trun the script in specific directory located in working dir. (e.g., --dir=20210921105411 )')
    print('\t--path\trun the script in specific directory (e.g., --path=C:\\Users\\Hexagon\\20210921105411 )')
    
def create_log(p):
    ls = [f for f in listdir(p) if '.fits' in f]
    ls = natsorted(ls)
    with open(join(p,'log.csv'),'w') as fi:
        fi.write("Filename,Date,Source,Bias,Flat,FPS,Exposure,Conversion gain,HDR mode,wavelength,Puissance laser,Relay,Comments\n")
        for f in ls:
            H = fits.getheader(join(p,f))
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
            line+="%s,"%H['ORELAY']
            line+="\n"
            fi.write(line)
    print("log.csv saved here: %s"%p)
if '__main__' in __name__:
    from sys import argv
    if '--help' in argv:
        help()
        exit(0)
    cfg = cfg_file()
    if '--list' in argv:
        ls = [d for d in listdir(cfg['WDIR']) if d.isnumeric()]
        ls = natsorted(ls)
        for d in ls:
            print(d)
        exit(0)
    for arg in argv:
        if '--dir' in arg:
            p = join(cfg['WDIR'],arg.replace('--dir=',''))
        if '--path' in arg:
            p = arg.replace('--path=','')
    create_log(p)
    
        
    

        
        
        
        
        