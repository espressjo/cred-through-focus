import numpy as np
from astropy.io import fits
import matplotlib.pyplot as plt
from scipy.ndimage import median_filter
from astropy.table import Table
from os.path import basename,join,isdir
from os import listdir,mkdir
from scipy.optimize import curve_fit
from matplotlib.backends.backend_pdf import PdfPages

'''
Created on Wed Jul 21 12:23:10 2021

Optional arguments are; 
    --list    Will list all the image folders in working directory defined in cfg file.
    --dir     run the analysis in specific directory located in working dir. (e.g., --dir=20210921105411 )
    --path    run the analysis in specific directory (e.g., --path=C:\\Users\\Hexagon\\20210921105411 )
    
@author: Jonathan St-Antoine, jonathan@astro.umontreal.ca
'''
def help():
    print('\t::: analyse_cred.py :::')
    print('')
    print('\t--list\tWill list all the image folders in working directory defined in cfg file.')
    print('\t--dir\trun the analysis in specific directory located in working dir. (e.g., --dir=20210921105411 )')
    print('\t--path\trun the analysis in specific directory (e.g., --path=C:\\Users\\Hexagon\\20210921105411 )')
class analyse():
    def __init__(self,wdir):
        self.wdir = wdir
        # axe de dispersion = X
        self.scale = 9.3 # scale of CRED detector
        # width of the comparison LSF in km/s
        self.width_comparison = 3.0 # km/s
        self.out_csv_file = 'table_defocus.csv'
        self.rawfiles = [join(self.wdir,f) for f in listdir(wdir) if 'fits' in f]# raw files, will be processed and dumped in the 'cleaned' directory
        if isdir(join(self.wdir,'clean')):
            self.cleaned_file = [f for f in listdir(join(self.wdir,'clean'))]
        else:
            self.cleaned_file = [];
        
    def clean(self):
        for f in self.rawfiles:
            if basename(f) in self.cleaned_file and fits.getheader(join(join(self.wdir,'clean'),basename(f)))['CORR']==True:
                print("%s already cleaned."%basename(f))
                continue
            im = np.array(fits.getdata(f),dtype=float)#im = np.array(im,dtype = float)
            h = fits.getheader(f)
            for ite in range(2):
                im2 = np.array(im)
                im2[im>np.nanpercentile(im,95)] = np.nan

                for j in range(im.shape[0]):
                    im[j] -= np.nanmedian(im2[j])

                im2 = np.array(im)
                im2[im>np.nanpercentile(im,95)] = np.nan

                for j in range(im.shape[1]):
                    im[:,j] -= np.nanmedian(im2[:,j])
    
            # fraction of points above threshold that is 10x 80th perncentinue
            effective_radius = np.sqrt(np.nansum(im>(np.nanpercentile(im,80)*10))) /self.scale
    
            if effective_radius<2: # PSF is too sharp or no PSF is present
                h['BGND'] = True
            else:
                h['BGND'] = False
            med = median_filter(im,[3,3])
            err = im-med
            err/=np.nanmedian(np.abs(err))
            bad = np.abs(err)>20
            im[bad] = err[bad]
            h['CORR'] = True,'Corrected'
            h['BATCH'] = basename(self.wdir), 'Batch name'
            if not isdir(join(self.wdir,'clean')):
                mkdir(join(self.wdir,'clean'))
            fits.writeto(join(join(self.wdir,'clean'),basename(f)),im,h,overwrite = True)  

    def redux(self):
        # compute the theoretical line profile
        dv = np.arange(fits.getheader(self.rawfiles[0])['NAXIS1'],dtype=float)/self.scale
        dv-=np.mean(dv)
        # get the width of the line
        ew = self.width_comparison/(np.sqrt(np.log(2)*2)*2)
        # create the theoretical line
        demo_line = np.exp(-0.5*(dv/ew)**2)
        # normalize the line to an integral of one
        demo_line/=np.nansum(demo_line)
        # get RV content of theoretical line
        demo_rv_content = np.nansum(np.gradient(demo_line)**2  )

        files = [join(join(self.wdir,'clean'),f) for f in listdir(join(self.wdir,'clean')) if 'fits' in f]
        fi = [f for f in listdir(join(self.wdir,'clean')) if 'fits' in f]
        # create empty table
        tbl = Table()

        tbl['file'] = fi
        tbl['MJDATE'] = 0.0
        tbl['FOCUS'] = 0.0
        tbl['RV_CONTENT'] = 0.0
        tbl['WIDTH_p25'] = 0.0
        tbl['WIDTH_p50'] = 0.0
        tbl['BGND'] = True
        tbl['BATCH'] = np.zeros(len(files),dtype ='<U99')
        tbl['COMPARISON_WIDTH_KMS'] = self.width_comparison
        
        for i in range(len(files)):
            # reading file
            im,h = fits.getdata(files[i],header = True)
        
            # axis = 0 -> LSF seen by spectro spectro
            profil = np.nanmean(im,axis=1)
            # find position of trace in spatial dimension
            mask_lsf = profil>(0.1*np.nanmax(profil))
            lsf = np.nanmean(im,axis=0)
        
            # convolve the LSF with a smoothing kernel
            lsf2 = np.convolve(lsf, np.ones(9))
            lsf2 /=np.nansum(lsf2)
        
            # get width of LSF at two thresholds
            width_25 = np.nansum(lsf2>0.25*np.max(lsf2))/self.scale
            width_50 = np.nansum(lsf2 > 0.5 * np.max(lsf2)) / self.scale
        
            # get RV content
            rv_content = np.nansum(np.gradient(lsf2)**2)/demo_rv_content
        
            # fill the table
            tbl['BGND'][i] = h['BGND']
            tbl['MJDATE'][i] = h['MJDATE']
            tbl['FOCUS'][i] = h['FOCUS']
            tbl['BATCH'][i] = h['BATCH']
            tbl['WIDTH_p25'][i] = width_25
            tbl['WIDTH_p50'][i] = width_50
            tbl['RV_CONTENT'][i] = rv_content


        # write down table
        tbl = tbl[np.argsort(tbl['MJDATE'])]
        print('We write : {}'.format(self.out_csv_file))
        tbl.write(self.out_csv_file, overwrite = True)
        print('\n\t\tdone...\n')
        
        tbl = tbl[tbl['BGND'] == False]
        
        BATCH = np.unique(tbl['BATCH'])
        with PdfPages(join(self.wdir,'results.pdf')) as pdf:
            for i in range(len(BATCH)):
                outname = BATCH[i]+'.pdf'
                tbl2 = tbl[tbl['BATCH'] == BATCH[i]]
                plt.close()
                fig, ax = plt.subplots(nrows = 2, ncols = 1, sharex = True, figsize = [16,8])
                ax[0].plot(np.array(tbl2['FOCUS']),np.array(tbl2['WIDTH_p25']),'g.',alpha = 0.5,label = 'Width 25% peak')
                ax[0].plot(tbl2['FOCUS'],tbl2['WIDTH_p50'],'r.',alpha = 0.5,label = 'Width 50% peak')
                ax[0].set(xlabel = 'Focus [µm]', ylabel = 'Width [H4RG pix]',title = BATCH[i])
                ax[0].legend()
                ax[1].plot(tbl2['FOCUS'],tbl2['RV_CONTENT'],'g.' ,alpha = 0.5)
                ax[1].set(xlabel = 'Focus [µm]', ylabel = 'RV content\n{0:.1} km/s Gaussian'.format(tbl2['COMPARISON_WIDTH_KMS'][0]))
    
                ord = np.argsort(tbl2['FOCUS'])
                ufocus= np.array(np.unique(tbl2['FOCUS']))
                med_rv =np.zeros_like(ufocus, dtype = float)
                for i in range(len(ufocus)):
                    g = tbl2['FOCUS'] == ufocus[i]
                    med_rv[i] = np.nanmedian(tbl2['RV_CONTENT'][g])
    
                # ,amp,ew,x0,zp,slope):
                p0 = [np.max(med_rv), 200, ufocus[np.argmax(med_rv)], np.nanmedian(med_rv)]
                def funky_gauss(x,amp,ew,x0,zp):
                    return np.exp(-.5*(x-x0)**2/ew**2)*amp+zp
                try:
                    fit, cov = curve_fit(funky_gauss, ufocus, med_rv, p0=p0)
        
                    residual = np.nanstd(tbl2['RV_CONTENT']-funky_gauss(tbl2['FOCUS'][ord],*fit))
        
                    index = np.arange(np.min(tbl2['FOCUS']),np.max(tbl2['FOCUS']))
                    rv_content_model = funky_gauss(index,*fit)
                    best = ((np.max(rv_content_model)-rv_content_model)*4) <residual
        
                    err =  np.sqrt(cov[2,2])
                    ax[1].plot(index,funky_gauss(index,*fit),'r-',alpha=0.2)
        
                    best_focus = index[np.argmax(rv_content_model)]
        
                    print(best_focus, err)
        
                    best = rv_content_model > (np.max(rv_content_model)*0.9 )
                    width = np.sum( best)
        
                    ax[1].plot(index[best],funky_gauss(index,*fit)[best],'r-',linewidth = 4,alpha=0.9)
        
                    ax[1].errorbar(best_focus,np.nanmax(rv_content_model),xerr = err,fmt = 'k-o',label = '${0:.0f}\pm{1:.0f} [\pm{2:.0f}]$'.format(best_focus,err,width/2))
        
                    ax[1].plot(fit[2],best_focus,'r-')
        
                    ord = np.argsort(tbl2['FOCUS'])
                    index=  np.arange(np.min(tbl2['FOCUS']),np.max(tbl2['FOCUS']),.1)
                    ax[1].set(xlabel = 'Focus [µm]', ylabel = 'RV content\n{0:.1} km/s Gaussian'.format(tbl2['COMPARISON_WIDTH_KMS'][0]),
                              ylim = [0,np.nanmax(tbl2['RV_CONTENT'])*1.1])
                except:
                    print('err')
                ax[1].legend()
                plt.savefig(join(self.wdir,outname))
                print('Saving {}'.format(outname))
                plt.show()
                pdf.savefig(fig)
        
                plt.show()
    def ls(self):
        from os import listdir
        ls = [d for d in listdir(self.wdir) if d.isnumeric()]
        from natsort import natsorted
        ls = natsorted(ls)
        return ls
if '__main__' in __name__:
    from sys import argv
    from config_file_cred import cfg_file
    if '--help' in argv:
        help()
        exit(0)
    cfg = cfg_file()
    if '--list' in argv:
        wdir = cfg['WDIR']
        an = analyse(wdir)
        ls = an.ls()
        for d in ls:
            print(d)
        exit(0)
    for arg in argv:
        if '--path' in arg:
            wdir = arg.replace('--path=','')
        if '--dir' in arg:
            wdir = join(cfg['WDIR'],arg.replace('--dir=',''))

    #wdir = '/home/noboru/tmpcred/20210722155404326'
    an = analyse(wdir)
    an.clean()
    an.redux()