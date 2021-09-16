#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep 15 17:13:05 2021

@author: noboru
"""
from time import sleep
class test:
    def __init__(self):
        self.a = 101011
        
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        print("closing")
if '__main__' in __name__:
    with test() as tt:
     
        
        