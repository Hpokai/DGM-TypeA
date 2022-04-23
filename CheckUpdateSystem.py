#!/usr/bin/env python3
#coding=utf-8

import os, sys, time, shutil
import subprocess
import zipfile

class CUpdate:
    def __init__(self, file_path):
        self.file_path = file_path
        os.chdir(self.file_path)
        
    def SetCurrentPath(self, file_path):
        self.current_path = file_path
        os.chdir(self.file_path)
        
    def isFileExist(self, file_name):
        return os.path.isfile(file_name)


if __name__ == "__main__":    
    file_name = '__dgm_update__.zip'
    file_path = '/home/pi/Public/Program/Update/'
    up = CUpdate(file_path)
    print(os.getcwd())

    isFinish = False

    while False == isFinish:
        tStart = time.time()
        ##########################################
        if True == up.isFileExist(file_name):
            print('true')
            
            zf = zipfile.ZipFile(file_name)
            zf.setpassword(b'00709789')
            for name in zf.namelist():
                zf.extract(name, file_path)
                print(name)
            zf.close()
            os.remove(file_name)
            shutil.move('CheckUpdateSystem.py','/home/pi/Public/Program/CheckUpdateSystem.py')
            print('ok')

        ###########################################
        tEnd = time.time()
        print('<per loop> {0}\n'.format(tEnd-tStart))

        time.sleep(5)
