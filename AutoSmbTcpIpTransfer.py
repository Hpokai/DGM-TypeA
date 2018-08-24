#!/usr/bin/env python3
#coding=utf-8

import os, sys, time
import base64
import subprocess

from smb.SMBConnection import SMBConnection
from ftplib import FTP

'''
Use a class to declare INFO of SPM and Central Server
'''
class CInfo:
    def __init__(self, ID, IP, Domain, Password, ServerName, ClientName, FolderName):
        self.ID = ID
        self.IP = IP
        self.Domain = Domain
        self.Password = Password
        self.ServerName = ServerName
        self.ClientName = ClientName
        self.FolderName = FolderName   
        
'''
Subfunctions
'''
global SingalMachine, CentralServer
global tcp_ip, smb_conn
global isDebug

def LoadSettings():
    global SingalMachine, CentralServer                                                                                     
    
    item=['IDvar','IPvar','Domainvar','Passwordvar','Servernamevar','Clientnamevar','Foldernamevar','IDvar1','IPvar1','Domainvar1','Passwordvar1','Servernamevar1','Clientnamevar1','Foldernamevar1']
    data = dict()
    
    file_in = open('/home/pi/Public/Program/FSDC.txt','r')
    i=0
    for line in file_in:
        data[item[i]] = base64.b64decode(line).decode('UTF-8')
        #print(data[item[i]])
        i+=1
        
    file_in.close()
    
    if isDebug == False:
        SingalMachine = CInfo(data['IDvar'],data['IPvar'],data['Domainvar'],data['Passwordvar'],data['Servernamevar'],data['Clientnamevar'],data['Foldernamevar'])
        CentralServer = CInfo(data['IDvar1'],data['IPvar1'],data['Domainvar1'],data['Passwordvar1'],data['Servernamevar1'],data['Clientnamevar1'],data['Foldernamevar1'])
    else:
        SingalMachine = CInfo("HsiehP1", "192.168.0.11", "corp.JABIL.ORG","kiNG628(@&", "CHA1MSM979", "pi", "CL")
        CentralServer = CInfo("dgm", "192.168.0.11", "","dgm", "", "", "/")

def GetRemoteFileSize(resp):
    size = resp.split(' ')
    return size[1]   

def isSameSize(local_file, remote_file):
    try:
        tcp_ip.sendcmd("TYPE I")
        resp = tcp_ip.sendcmd('SIZE /{}'.format(remote_file).encode('utf-8').decode('latin-1'))
        remote_file_size = GetRemoteFileSize(resp)
        #print('remote_file_size %s' %remote_file_size)
    except:
        remote_file_size = -1
    try:
        local_file_size = os.path.getsize(local_file)
        #print('local_file_size %s' %local_file_size)
    except:
        local_file_size = -1

    if int(remote_file_size) == int(local_file_size):
        return True
    else:
        return False

def UploadOneFile(local_file, remote_file):
    if not os.path.isfile(local_file):
        return
    
    if isSameSize(local_file, remote_file) == True:
        print('Ignore[equal size]: %s' %local_file)
    else:
        print('Sent: %s' %local_file)
        file_handler = open(local_file, 'rb')
        tcp_ip.storbinary('STOR /{}'.format(remote_file).encode('utf-8').decode('latin-1'), file_handler, 1024)
        file_handler.close()

def UploadManyFiles(local_dir='./', remote_dir = './'):
    if not os.path.isdir(local_dir):
        return
    
    local_files = os.listdir(local_dir)
    tcp_ip.cwd(remote_dir)
    
    for lf in local_files:
        src = os.path.join(local_dir, lf)
        if os.path.isdir(src) == True:
            try:
                tcp_ip.mkd(lf)
            except:
                print('目錄已存在 %s' %lf)
                UploadManyFiles(src, lf)
        else:
            UploadOneFile(src, lf)

def ConnectTcpIp():
    global CentralServer
    global tcp_ip

    tcp_ip = FTP()
    tcp_ip.set_pasv(True)
    try:
        print(CentralServer.IP)     
        tcp_ip.connect(CentralServer.IP, 21, timeout = 3000)
    except Exception:
        print('連接失敗')
        return False

    try:   
        tcp_ip.login(CentralServer.ID, CentralServer.Password)        
        print(tcp_ip.getwelcome())            
    except Exception:
        print('登入失敗')
        tcp_ip.quit()   #polite to leave
        return False

    try:
        #print('Send MAC to server')
        interface='eth0'
        mac = open('/sys/class/net/%s/address' %interface).read()
        mac_cmd = "LMAC " + mac[0:17]
        print(mac_cmd)
        tcp_ip.sendcmd(mac_cmd)
    except(Exception):
        print('Check MAC Failure.')
        tcp_ip.quit()   #polite to leave
        return False

    try:
        tcp_ip.cwd(CentralServer.FolderName)
    except(Exception):
        print('切換目錄失敗')
        tcp_ip.quit()   #polite to leave
        return False

    return True

def UploadFileToCentralServerByTcpIp():
    global tcp_ip
    
    UploadManyFiles('/home/pi/Public/Program/DGM_Data/','/')
    tcp_ip.sendcmd('PASV')
        
    print('====Upload Finished====')

def ConnectSMB():
    global smb_conn
    
    smb_conn = SMBConnection(SingalMachine.ID, SingalMachine.Password, SingalMachine.ClientName, SingalMachine.ServerName, SingalMachine.Domain, use_ntlm_v2 = True)
    isConnect = smb_conn.connect(SingalMachine.IP, 139)

    time.sleep(1)

    if isConnect == True:
        print('Connect succeeded!')
    else:
        print('Conncet failed!')

    return isConnect
    

def DownloadFileFromSingalMachineBySMB():
    global smb_conn
    
    list_path = smb_conn.listPath(SingalMachine.FolderName, "/")
    for lp in list_path:
        if lp.isDirectory == False:
            local_filename = '/home/pi/Public/Program/DGM_Data/'+lp.filename
            remote_filename = '/'+lp.filename
            #if file exist
            try:
                file_attr = smb_conn.getAttributes(SingalMachine.FolderName, remote_filename)
                file_obj = open(local_filename, 'wb')
                file_attributes, file_size = smb_conn.retrieveFile(SingalMachine.FolderName, remote_filename, file_obj)
                file_obj.close()
                print('Received file: {}'.format(lp.filename))
            except(Exception):
                print('File does not exist: {}'.format(remote_filename))
    
    print('====Download Finished====')
    
    

def ZipFiles():
    src_file_path = '/home/pi/Public/Program/DGM_Data'
    os.chdir(src_file_path)
    f = []
    for dirpath, dirnames, filenames in os.walk('./'):
        f.extend(filenames)
        
    print(">> Start compress files and wait\n--------------------")   
    rc = subprocess.call(['7z', 'a', '/home/pi/Public/Program/DGM_Data.zip', '-tzip', '-mx0', '-p1234']+f)
    print('--------------------\n>> Compress as "DGM_Data.zip"\n')


def RemoveLocalFiles():
    local_files = os.listdir('/home/pi/Public/Program/DGM_Data/')
    
    for lf in local_files:
        src = os.path.join('/home/pi/Public/Program/DGM_Data/', lf)
        os.remove(src)
    
if __name__ == "__main__":
    global isDebug
    isDebug = True
    isConnectSMB = isConnectTcpIp = False
    if isDebug == False:
        time.sleep(3)
    
    LoadSettings()
    while True:
        if isConnectSMB == False:
            print('>>>>>>Connect to SPM---------')
            isConnectSMB = ConnectSMB()
        if isConnectTcpIp == False:
            print('\n>>>>>>Connect to Server--------')
            isConnectTcpIp = ConnectTcpIp()

        while isConnectSMB == True & isConnectTcpIp == True:
            try:
                tStart = time.time()
                print('\n### Remove Local Files ####')        
                RemoveLocalFiles()
                time.sleep(1)
                print('\n*****Recieve Data*****')
                DownloadFileFromSingalMachineBySMB()
                time.sleep(1)
                print('*****Sent Data*****')
                UploadFileToCentralServerByTcpIp()            
                time.sleep(3)
                #break
                tEnd = time.time()
                print(tEnd-tStart)
            except Exception as e:
                print('\nServer is down!')
                break                
                
        if isConnectTcpIp == True:
            print('\n--------Disconnect to Server<<<<<<')
            try:
                tcp_ip.quit()
            except Exception as e:
                print(e)                
            isConnectTcpIp = False
        if isConnectSMB == True:
            print('\n--------Disconnect to SPM<<<<<<')
            try:
                smb_conn.close()
            except Exception as e:
                print(e)            
            isConnectSMB = False
                
        time.sleep(10)
        
