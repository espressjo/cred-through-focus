#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 21 12:23:10 2021

optional arguments are; 
    --no-bias      Will not bias the images
    --no-ccdt      Will not show the real-time temperature of the CCD
    --check-version
@author: Jonathan St-Antoine, jonathan@astro.umontreal.ca
"""
def help():
    print('\n\t::: cred_script.py help menu :::')
    print('\t--no-bias      Will not bias the images')
    print('\t--no-ccdt      Will not show the real-time temperature of the CCD')
    print('\t--check-version         Will test connection to the CRED.')
    print('\t--test-cam\t will test the camera connection')
from cred2 import cred2
from os.path import join,isdir
from datetime import datetime
from os import mkdir
from time import sleep
from config_file_cred import cfg_file
from sys import argv
#::::::::::::::::::::::::::::::::::::::::::
#::::          Editable stuff         :::::
#::::::::::::::::::::::::::::::::::::::::::

if '--help' in argv:
    help()
    exit(0)    
if '--check-version' in argv:
    import version
    exit(0)
if '--test-cam' in argv:
    with cred2() as cred:
        if cred.cam_detected:
            print("%s detected"%cred.cameraModel)
        else:
            print("Not detected")
    exit(0)
gain = "high"#conversion gain.
cfg = cfg_file()
number_image = int(cfg['IMGNUM'])
gain = str(cfg["GAIN"])
target_temperature = float(cfg['DETTEMP'])
timeout_trigger = int(cfg['TIMEOUT']) #timeout before capture
nd_filter = float(cfg['NDF'])#ND filter value


exp_time = 35#Starting exposure time in ms. The exposure time will be asked eveytime time

#:::::::::::::::::::::::::::::::::::::::::
img2csv_path = ''
with cred2() as cred:
    #set some variables
    
    
    operator = input("Name of the person using this script?\n\t")
    for i in range(3):
        wavelength = input("Wavelength of the laser?\n\t")
        try:
            wavelength = float(wavelength)
            break
        except :
            print("Wavelength must be float or int value.")
    
    for i in range(3):
        puissance = input("Power of the laser (mW)?\n\t")
        try:
            puissance = float(puissance)
            break
        except :
            print("Power must be float or int value.")
    programme = input("Name of the program?\n\t")
    if 'WDIR' in cfg and isdir(cfg['WDIR']):
        cred.WDIR = join(cfg['WDIR'],datetime.now().strftime("%Y%m%d%H%M%S%f")[:-3])
    else:
        cred.WDIR = join(cred.WDIR,datetime.now().strftime("%Y%m%d%H%M%S%f")[:-3])
    img2csv_path = cred.WDIR
    if not isdir(cred.WDIR):
        mkdir(cred.WDIR)
    #Initial setup
    cred.set_exp_time(exp_time)
    old_exp = exp_time
    
    if '--no-ccdt' not in argv:
        cred.set_sensor_temperature_live_wait(target_temperature)
    else:
        cred.set_sensor_temperature(target_temperature)
    #set conversion gain
    cred.set_gain(gain)
    if '--no-bias' not in argv:
        cred.bias()
    
    #::::::::::::::::::::::::::::::::::::::::::
    #::  Set some variable for the headers   ::
    #::::::::::::::::::::::::::::::::::::::::::
        
    cred.set_operator(operator)
    cred.set_wavelenght(wavelength)
    cred.set_programme_name(programme)
    cred.set_puissance(puissance)#power of the source in mW
    cred.set_nd_filter(nd_filter)#ND filter value
    for cmt in cfg['COMMENTS']:
        cred.set_comments(cmt)
    ii=0
    analyse = True
    print("From this point you can type in a command;\n\tanalyse\tWill start the analysis\n\tabort\tWill close this script without analysing the data\n\tcomment\tWill let a user enter a comment in the FITS header.")
    while(1):
        print("Position number #%d"%(ii+1))
        ii+=1
        tmp_cmt = ""
        usr = input("Move the focuser to a position. Press any key to continue. or [analyse,abort,comment]")
        if 'analyse' in usr:
            analyse = True
            break
        if 'comment' in usr:
            tmp_cmt = input('Enter your comment: ')
        if 'abort' in usr:
            analyse = False
            break
        pos = float(input("Position in (um)? "))
        cred.set_focus(pos)
        exp = float(input("Exposure time (ms)? "))
        if exp!=old_exp:
            cred.set_exp_time(exp)
            cred.bias()
            old_exp = exp
        for i in range(timeout_trigger):
            print("%d/%d"%(i+1,timeout_trigger))
            sleep(1)
        for i in range(number_image):
            print("Image %d/%d"%(i+1,number_image))
            fname = datetime.now().strftime('%Y%m%d%H%M%S%f')[:-3]
            if tmp_cmt!="":
                cred.acquire_single_image("%s.fits"%fname,user_cmt=tmp_cmt)
            else:
                cred.acquire_single_image("%s.fits"%fname)
    

    
if analyse:
    from analyse_cred import analyse
    
    an = analyse(img2csv_path)
    an.clean()
    an.redux()
    if img2csv_path!='':
        from img2csv import create_log
        create_log(img2csv_path)