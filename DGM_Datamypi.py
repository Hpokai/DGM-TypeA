#!/usr/bin/python
#--------------------------------------
#
#                mypi.py
#  Functions to display Pi properties
#
#  If called directly outputs :
#  - Revision number
#  - Serial number
#  - Mac address
#  - IP address
#  - CPU temperature
#  - GPU temperature
#
# Author : Matt Hawkins
# Date   : 12/03/2016
#
# http://www.raspberrypi-spy.co.uk/
#
#--------------------------------------

import platform
import subprocess
import os

# Define functions

def getMAC(interface='eth0'):
  # Return the MAC address of interface
  try:
    line = open('/sys/class/net/%s/address' %interface).read()
  except:
    line = "None"
  return line[0:17]

def getSerial():
  # Extract serial from cpuinfo file
  mycpuserial = "Error"
  try:
    f = open('/proc/cpuinfo','r')
    for line in f:
      if line[0:6]=='Serial':
        mycpuserial = line[10:26]
    f.close()
  except:
    mycpuserial = "Error"

  return mycpuserial

def getRevision():
  # Extract board revision from cpuinfo file
  myrevision = "Error"
  try:
    f = open('/proc/cpuinfo','r')
    for line in f:
      if line[0:8]=='Revision':
        myrevision = line[11:-1]
    f.close()
  except:
    myrevision = "Error"

  return myrevision

def getIP(interface='eth0'):
  # Read ifconfig.txt and extract IP address
  try:
    filename = 'ifconfig_' + interface + '.txt'
    os.system('ifconfig ' + interface + ' > /home/pi/' + filename)
    f = open('/home/pi/' + filename, 'r')
    line = f.readline() # skip 1st line
    line = f.readline() # read 2nd line
    line = line.strip()
    f.close()

    if line.startswith('inet addr:'):
      a,b,c = line.partition('inet addr:')
      a,b,c = c.partition(' ')
    else:
      a = 'None'

    return a

  except:
    return 'Error'

def getCPUtemp():
  # Extract CPU temp
  try:
    temp = subprocess.check_output(['vcgencmd','measure_temp'])
    temp = temp[5:-3]
  except:
    temp = '0.0'
  temp = '{0:.2f}'.format(float(temp))
  return str(temp)

def getGPUtemp():
  # Extract GPU temp
  try:
    temp = subprocess.check_output(['cat','/sys/class/thermal/thermal_zone0/temp'])
    temp = float(temp)/1000
  except:
    temp = 0.0
  temp = '{0:.2f}'.format(temp)
  return temp

def getRAM():
  # free -m
  output = subprocess.check_output(['free','-m'])
  lines = output.splitlines()
  line  = lines[1]
  ram = line.split()
  return (str(ram[1]),str(ram[2]),str(ram[3]))

def getDisk():
  # df -h
  output = subprocess.check_output(['df','-h'])
  lines = output.splitlines()
  line  = lines[1]
  disk  = line.split()
  return disk

def getCPUspeed():
  # Get CPU frequency
  try:
    output = subprocess.check_output(['vcgencmd','get_config','arm_freq'])
    lines = output.splitlines()
    line  = lines[0]
    freq = line.split('=')
    freq = freq[1]
  except:
    freq = '0'
  return freq

def getUptime():
  # uptime
  # tupple uptime, 5 min load average
  return 0

def getPython():
  # Get current Python version
  # returns string
  pythonv = platform.python_version()
  return pythonv

def getSPI():
  # Check if SPI bus is enabled
  # by checking for spi_bcm2### modules
  # returns a string
  spi = "False"
  try:
    c=subprocess.Popen("lsmod",stdout=subprocess.PIPE)
    gr=subprocess.Popen(["grep" ,"spi_bcm2"],stdin=c.stdout,stdout=subprocess.PIPE)
    output = gr.communicate()[0]
    if output[:8]=='spi_bcm2':
      spi = "True"
  except:
    pass
  return spi

def getI2C():
  # Check if I2C bus is enabled
  # by checking for i2c_bcm2### modules
  # returns a string
  i2c = "False"
  try:
    c=subprocess.Popen("lsmod",stdout=subprocess.PIPE)
    gr=subprocess.Popen(["grep" ,"i2c_bcm2"],stdin=c.stdout,stdout=subprocess.PIPE)
    output = gr.communicate()[0]
    if output[:8]=='i2c_bcm2':
      i2c = "True"
  except:
    pass
  return i2c

def getBT():
  # Check if Bluetooth module is enabled
  # returns a string
  bt = "False"
  try:
    c=subprocess.Popen("lsmod",stdout=subprocess.PIPE)
    gr=subprocess.Popen(["grep" ,"bluetooth"],stdin=c.stdout,stdout=subprocess.PIPE)
    output = gr.communicate()[0]
    if output[:9]=='bluetooth':
      bt = "True"
  except:
    pass
  return bt

if __name__ == '__main__':

  myRAM = getRAM()
  myDisk = getDisk()

  # Script has been called directly
  print("----------------------------------------")
  print("System               : " + platform.platform())
  print("Revision Number      : " + getRevision())
  print("Serial Number        : " + getSerial())
  print("Python version       : " + platform.python_version())
  print("----------------------------------------")
  print("i2c enabled          : " + getI2C())
  print("SPI enabled          : " + getSPI())
  print("Bluetooth enabled    : " + getBT())
  print("----------------------------------------")
  print("Ethernet MAC Address : " + getMAC('eth0'))
  print("Ethernet IP Address  : " + getIP('eth0'))
  print("Wireless MAC Address : " + getMAC('wlan0'))
  print("Wireless IP Address  : " + getIP('wlan0'))
  print("----------------------------------------")
  print("CPU Clock            : " + getCPUspeed() + "MHz")
  print("CPU Temperature      : " + getCPUtemp() + "\xb0" +"C")
  print("GPU Temperature      : " + getGPUtemp() + "\xb0" +"C")
  print("RAM (Available)      : " + myRAM[0] + "MB (" + myRAM[2] + "MB)")
  print("Disk (Available)     : " + myDisk[1] + " (" + myDisk[3] + ")")
  print("----------------------------------------")