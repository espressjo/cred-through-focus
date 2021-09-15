#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep 15 09:21:43 2021

@author: noboru
"""
from os import getcwd
from os.path import join,isfile
import re

class cfg_file():
    def __init__(self):
        root_path = getcwd()
        self.cfg = {}
        self.dict = ['IMGNUM','DETTEMP','TIMEOUT','NDF']
        if 'src' in root_path:
            root_path = root_path.replace('src','')
        self.set_default()
        if not isfile(join(root_path,'cred.cfg')):
            print('No config file found.\nSetting values to default.')
        else:
            with open(join(root_path,'cred.cfg'),'r') as f:
                      self.extract_info(f)
    def __getitem__(self,key):
        return self.cfg[key]
    def extract(self,line):
        new_line = ""
        for c in line:
            if c=="#":
                break

            new_line+=c
        
        new_line=new_line.replace('\t',' ')
        
        new_line = re.sub(' +', ' ', new_line)
        
        kw = new_line.split(' ')[0]
        
        arg = new_line.replace(kw,'').strip()
        kw = [c.capitalize() for c in kw]
        kw = "".join(kw)
        return kw,arg
        
    def set_default(self):
        self.cfg['IMGNUM'] = '25' 
        self.cfg['DETTEMP'] = '-15'
        self.cfg['TIMEOUT'] = '5'
        self.cfg['NDF'] = '0'
        self.cfg['COMMENTS'] = [];
        self.cfg['WDIR'] = "C:/Users/Hexagon/Desktop/"
    def extract_info(self,f):
        for line in f.readlines():
            
            kw,arg = self.extract(line)
            
            if kw in self.dict:
                self.cfg[kw] = arg
            elif 'COMMENT' in kw:
                self.cfg['COMMENTS'].append(arg)
    def __str__(self):
        txt = ''
        for h in self.cfg:
            if h!='COMMENTS':
                txt+=h+' '+self.cfg[h]+'\n'
            else:
                txt+=h+'\n'
                for c in self.cfg[h]:
                    txt+='\t'+c+'\n'
        return txt
if '__main__' in __name__:
    cfg = cfg_file()
    print(cfg['COMMENTS'])
    
    