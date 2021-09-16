#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 21 12:23:10 2021

optional arguments are; 
    --no-bias      Will not bias the images
    --no-ccdt      Will not show the real-time temperature of the CCD
@author: Jonathan St-Antoine, jonathan@astro.umontreal.ca
"""
def help():
    print('\n\t::: cred_script.py help menu :::')
    print('\t--no-bias      Will not bias the images')
    print('\t--no-ccdt      Will not show the real-time temperature of the CCD')
    print('\t--test         Will test connection to the CRED.')
from cred import CRED
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
def check_connection():
    from pycromanager import Bridge
    from version import colored
    try:
        bridge = Bridge()
        bridge.get_core()
        
        print("Camera (CRED)\t[%s]"%(colored('Connected')))
        bridge.close()
    except :
        print("Camera (CRED)\t[%s]"%(colored('Not Connected',c='red')))
        print('Exiting...')
        exit(0)
if '--test' in argv:
    check_connection()
    exit(0)     
    
#test connection    
check_connection()


cfg = cfg_file()
number_image = int(cfg['IMGNUM'])
target_temperature = float(cfg['DETTEMP'])
timeout_trigger = int(cfg['TIMEOUT']) #timeout before capture
nd_filter = float(cfg['NDF'])#ND filter value
comments = cfg['COMMENTS']

exp_time = 35#Starting exposure time in ms. The exposure time will be asked eveytime time

#:::::::::::::::::::::::::::::::::::::::::

with CRED() as cred:
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
    
    cred.WDIR = join(cred.WDIR,datetime.now().strftime("%Y%m%d%H%M%S%f")[:-3])
    if not isdir(cred.WDIR):
        mkdir(cred.WDIR)
    #Initial setup
    cred.set_exp_time(exp_time)
    old_exp = exp_time
    
    if '--no-ccdt' not in argv:
        cred.set_sensor_temperature(target_temperature)
    if '--no-bias' not in argv:
        cred.bias()
    
    #::::::::::::::::::::::::::::::::::::::::::
    #::  Set some variable for the headers   ::
    #::::::::::::::::::::::::::::::::::::::::::
        
    cred.set_operator(operator)
    cred.set_wavelenght(wavelength)
    cred.set_programme_name(programme)
    cred.set_puissance(puissance)#power of the source in mW
    cred.set_nd(nd_filter)#ND filter value
    
    ii=0
    while(1):
        print("Position number #%d"%(ii+1))
        ii+=1
        tmp_cmt = ""
        usr = input("Move the focuser to a position. Press any key to continue. -1 to quit, -2 to add a comment ")
        if '-1' in usr:
            break
        if '-2' in usr:
            tmp_cmt = input('Enter your comment: ')
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
    

    

from analyse_cred import analyse

an = analyse(cred.WDIR)
an.clean()
an.redux()