# -*- coding: utf-8 -*-
"""
Created on Wed Jul 21 12:23:10 2021

This script axcept 2 arguments

    --show-img    Will take an display an image
    --exp         Sets the exposure time of the CRED

e.g., python cred.py --show-img --exp=50 

@author: Jonathan St-Antoine, jonathan@astro.umontreal.ca
"""
from pycromanager import Bridge
from astropy.io import fits
from datetime import datetime
from os.path import join
import numpy as np
from astropy.time import Time

from config_file_cred import cfg_file

fmt = "%Y-%m-%dT%H:%M:%S"
xlim = 1#for animation
xlim_step = 1#for animation
class CRED():
    def __init__(self):
        self.bridge = Bridge()
        self.core =  self.bridge.get_core()
        self.bias_status = 0
        self.focus=0
        cfg = cfg_file()
        self.WDIR = cfg['WDIR']
        self.programme_name=""
        self.operator = ""
        self.puissance = 0
        self.nd = 0
        self.wavelength = 0
        self.comments = [];
    def set_comments(self,comments):
        self.comments.append(comments)
    def set_wavelenght(self,w):
        self.wavelength = w
    def set_puissance(self,p):
        self.puissance = p #in mW
    def set_nd_filter(self,nd):
        self.nd = nd #in ND
    def set_programme_name(self,name):
        self.programme_name = name
    def set_operator(self,name):
        self.operator = name
    def get_status(self):
        status = {}
        definition = {'EXPTIME':'Exposure time (ms)','BIAS': 'Bias status 1->done, 0-> not done',
                      'FOCUS':'focus position in um (manually set)','DATE': 'date of creation','CAMERA': 'camera modele',
                      'FPS':'Frame per second','CCDT':'temperature of the FPA', 
                      'CCDTSP': 'Set point of the FPA','BINNING':'Binning of the sensor',
                      'MJDATE':'MJD','WAVEL':'Approx. wavelength in nanometer'}
        status['EXPTIME'] = self.get_exp_time()
        status['BIAS'] = self.bias_status
        status['FOCUS'] = self.focus
        status['WAVEL'] = self.wavelength
        status['DATE'] = datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] #datetime.now().strftime(fmt)
        status['CAMERA'] = self.core.get_property('FliSdk','Cameras')
        status['FPS'] = float(self.core.get_property('FliSdk','FPS'))
        status['CCDT'] = self.get_temp()
        status['CCDTSP'] = float(self.core.get_property('FliSdk','Set sensor temp'))
        status['BINNING'] = int(self.core.get_property('FliSdk','Binning'))
        status['MJDATE'] = Time.now().mjd
        
        return status,definition
    def get_exp_time(self):
        #return exposure time in ms
        return float(self.core.get_exposure())
    def set_sensor_temperature(self,t):
        #set pelletier target in deg. C
        self.core.set_property('FliSdk','Set sensor temp',t)
    def set_sensor_temperature(self,t):
        #set pelletier target in deg. C
        self.core.set_property('FliSdk','Set sensor temp',t)
        from matplotlib import pyplot as plt
        import matplotlib.animation as ani
        import seaborn as sns
        
        sns.set_theme()
        fig = plt.figure()
        plt.xlabel('time (minutes)')
        plt.ylabel('Temperature CCD')
        plt.ylim([-18,28])
        plt.xlim([0,1])
        plt.title("Target temperature %.1f$^\circ C$\nCurrent temperature N/A"%t)
        t_o = t
        t = [];
        time = [];
        
        def chartfunc(i=int):
            
            global xlim
            global xlim_step
            t.append(self.get_temp())
            time.append(i/60.)
            if xlim<=i/60.:
                xlim +=xlim_step
                plt.xlim([0,xlim])
            plt.plot(time,t,'-',color='b',label="%.1f$^\circ C$"%t[-1])
            plt.title("Target temperature %.1f$^\circ C$\nCurrent temperature %.1f$^\circ C$"%(t_o,t[-1]))
        animator = ani.FuncAnimation(fig, chartfunc, interval = 1000)
        
        plt.show()
    def get_temp(self):
        #return ccd temp (deg. C)
        return float(self.core.get_property_from_cache('FliSdk','Sensor Temp'))
    def show_tmp_image(self):
        from os import system
        self.acquire_single_image('C:/Users/Hexagon/Desktop/tmp.fits',overwrite=True)
        system("C:\SAOImageDS9\ds9.exe -zscale C:/Users/Hexagon/Desktop/tmp.fits")
    def acquire_single_image(self,fname,overwrite=False,user_cmt=""):
        self.core.snap_image()
        if '/' not in fname:
            fname=join(self.WDIR,fname)
        tagged_image = self.core.get_tagged_image()
        pixels = np.reshape(tagged_image.pix,newshape=[tagged_image.tags['Height'], tagged_image.tags['Width']])
        hdu = fits.PrimaryHDU(data=pixels)
        status,defi = self.get_status()
        for h in status:
            hdu.header[h] = (status[h],defi[h])
        #add more information
        hdu.header['ORELAY'] = ('10x','objectif zoom')
        hdu.header['HDR'] = ('off','HDR')
        #hdu.header['WAVEL'] = (1547,'Wavelength in nanometer')
        hdu.header['GAIN'] = ('low','Gain setting')
        if self.programme_name!="":
            hdu.header['PROGRAM'] = (self.programme_name,'programe name')
        if self.operator!="":
            hdu.header['OPE'] = (self.operator,'Operator')
        if self.puissance!=0:
            hdu.header['SOURCEP'] = (self.puissance,'Source power in mW')
        hdu.header['NDFILTER'] = (self.nd,'ND filter placed at the front-end')
        for cmt in self.comments:
            hdu.header['COMMENT'] = str(cmt)
        if user_cmt!="":
            hdu.header['COMMENT'] = user_cmt.strip()
        #'C:/Users/Hexagon/Desktop/test.fits'
        hdu.writeto(fname,overwrite=overwrite)
    def disconnect(self):
        self.bridge.close()
    def set_focus(self,pos):
        self.focus = pos
    def bias(self):
        self.core.set_property('FliSdk','Build bias',1)
        if int(self.core.get_property('FliSdk','Build bias'))!=0:
            print("error in bias")
        else:
           self.core.set_property('FliSdk','Apply bias',1)
           self.core.set_property('FliSdk','Apply bias',0)
        self.bias_status=1
    def set_exp_time(self,t):
        #in ms
        max_t = float(self.core.get_property('FliSdk','MaximumExposureMs'))
        if t<max_t:
            self.core.set_exposure(t)
        else:
            FPS = 1000.0/t
            if FPS<=1:
                FPS=int(FPS)
            self.core.set_property('FliSdk','FPS',FPS)
            t = float(self.core.get_property('FliSdk','MaximumExposureMs'))
            self.core.set_exposure(int(t))
        t= self.core.get_exposure()
        print("Exposure time is set to %fms"%t)
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()
        print("Camera closed!")
if '__main__' in __name__:
    from sys import argv
    if '--help' in argv:
        print('\t::: cred.py :::')
        print('')
        print('\t--help\thelp menu')
        print('\t--show-img\tTake an image and display in DS9. All parameters can be adjust with imageJ')
        exit(0)
    if '--show-img' in argv:

        with CRED() as cred:
            print(cred.get_temp())
            for arg in argv:
                if '--exp' in arg:
                    exp = float(arg.replace('--exp=','').strip())
                    cred.set_exp_time(exp)
            cred.show_tmp_image()
            

