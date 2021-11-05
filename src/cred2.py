#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov  5 11:49:45 2021

@author: noboru
"""
#TODO implement Gain function
#TODO in version.py, make sure we have seaborn as well for live graph
import FliSdk_V2 as FliSdk
from time import sleep
from os.path import join
from astropy.io import fits
from os import system
from datetime import datetime
from astropy.time import Time

xlim = 1#for animation
xlim_step = 1#for animation

class cred2():
    def __init__(self):
        self.cameraModel = ""
        self.context = FliSdk.Init()
        self.detectCameras()
        self.status = ""
        self.diag = ""
        self.fps = 0.0
        self.comments = [];
        self.wavelength = 0
        self.puissance = 0
        self.focus = 0
        self.nd = 0
        self.programme_name = ''
        self.operator = ''
        self.fmt = "%Y-%m-%dT%H:%M:%S"
        #will change
        self.WDIR = 'C:/Users/NIRPS/Documents/CRED-DATA'
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
    def set_focus(self,pos):
        self.focus = pos
    def set_sensor_temperature_live_wait(self,t):
        #set pelletier target in deg. C
        self.set_sensor_temperature(t)
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
        return self.read_temp()['sensor']
    def read_temp(self):
        '''
        Read temperatures. 

        Returns
        -------
        temps : dict
            dictionary containing; MB, FB, PW, sensor, peltier, heatsink

        '''
        _temps = FliSdk.FliCredTwo.GetAllTemp(self.context)
        temps = {}
        temps['MB'] = _temps[1]
        temps['FE'] = _temps[2]
        temps['PW'] = _temps[3]
        temps['sensor'] = _temps[4]
        temps['peltier'] = _temps[5]
        temps['heatsink'] = _temps[6]
        return temps
    def get_status(self):
        status = {}
        definition = {'EXPTIME':'Exposure time (ms)','BIAS': 'Bias status 1->done, 0-> not done',
                      'FOCUS':'focus position in um (manually set)','DATE': 'date of creation','CAMERA': 'camera modele',
                      'FPS':'Frame per second', 
                      'CCDTSP': 'Set point of the FPA',
                      'MJDATE':'MJD','WAVEL':'Approx. wavelength in nanometer',
                      'CCDT':'temperature of the sensor',
                      'peltier': 'temperature at the Peltier stage',
                      'hsink': 'temperature at the heatsink'}
        status['EXPTIME'] = self.get_exp_time()
        status['BIAS'] = self.get_bias_status()
        status['FOCUS'] = self.focus
        status['WAVEL'] = self.wavelength
        status['DATE'] = datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] #datetime.now().strftime(fmt)
        status['CAMERA'] = self.cameraModel
        status['FPS'] = self.get_fps()
        status['CCDTSP'] = self.get_ccd_set_point()
        #status['BINNING'] = int(self.core.get_property('FliSdk','Binning'))
        status['MJDATE'] = Time.now().mjd
        temps = self.read_temp()
        status['CCDT'] = temps['sensor']
        status['peltier'] = temps['peltier']
        status['hsink'] = temps['heatsink']
    
        return status,definition

    def shutdown(self):
        '''
        We cannot power up the camera via software after this function is called. 

        Returns
        -------
        None.

        '''
        FliSdk.FliCred.ShutDown(self.context)
        FliSdk.Stop(self.context)
        FliSdk.Exit(self.context)
        exit(0)
        return
    def get_ccd_set_point(self):
        _,sp = FliSdk.FliCredTwo.GetTempSnakeSetPoint(self.context)
        return sp
    def set_sensor_temperature(self,sp):
        FliSdk.FliCredTwo.SetTempSnakeSetPoint(self.context, sp)
        return
    def detectCameras(self):
        FliSdk.DetectGrabbers(self.context)
        listOfCameras = FliSdk.DetectCameras(self.context)
        
        if len(listOfCameras) == 0:
            print("No camera detected. Exiting")
            exit(0)

        FliSdk.SetCamera(self.context, listOfCameras[0])
        FliSdk.Update(self.context)
        #set some stuff maybe...
        self.cameraModel = FliSdk.GetCameraModel(self.context)
        res,self.status,self.diag = FliSdk.FliCred.GetStatusDetailed(self.context)

        res,self.fps = FliSdk.FliSerialCamera.GetFps(self.context)
        #    self.ReadParameters()
        #    self.timer.start(10)
    def disconnect(self):
        FliSdk.Stop(self.context)
        FliSdk.Exit(self.context) 
    def set_exp_time(self,time_ms):
        sec = time_ms/1000.
        fps = 1/sec
        FliSdk.FliSerialCamera.SetFps(self.context,fps)
        FliSdk.FliCredTwo.SetTint(self.context, sec)
        return 
    def get_exp_time(self):
        #return exposure time in ms
        res, tint = FliSdk.FliCredTwo.GetTint(self.context)
        return tint*1000.0
    def get_fps(self):
        #return exposure time in ms
        _,fps = FliSdk.FliSerialCamera.GetFps(self.context)
        return fps
    def bias(self):
        if (not FliSdk.FliCred.BuildBias(self.context)):
            print("Failed to acquire bias.")
        FliSdk.FliSerialCamera.EnableBias(self.context, True)
        return 
    def disable_bias(self):
        FliSdk.FliSerialCamera.EnableBias(self.context, False)
        return
    def get_bias_status(self):
        _,state = FliSdk.FliCred.GetBiasState(self.context)
        return state
    def show_tmp_image(self):
        data = self.single_capture()
        hdu = fits.PrimaryHDU(data=data)
        hdu.writeto(join(self.WDIR,'tmp.fits'),overwrite=True)
        system("C:\SAOImageDS9\ds9.exe -zscale %s"%join(self.WDIR,'tmp.fits'))
    def single_capture(self):
        '''
        return the RAW data.

        Returns
        -------
        TYPE
            return the RAW data in numpy 2d array

        '''
        FliSdk.EnableGrabN(self.context, 1)
        FliSdk.Start(self.context)
        sleep(0.1)
        i=1
        while (not FliSdk.IsGrabNFinished(self.context)):
            sleep(0.1)
            print("waiting for data")
            if (i*100>2000):
                print("timeout reached 2s")
                break
            i+=1
        FliSdk.Stop(self.context)
        return FliSdk.GetRawImageAsNumpyArray(self.context,-1)
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()
        print("Camera closed!")
    def acquire_single_image(self,fname,overwrite=False,user_cmt=""):
        
        if '/' not in fname:
            fname=join(self.WDIR,fname)
        pixels = self.single_capture()
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