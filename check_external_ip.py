#!/usr/bin/python

from __future__ import print_function

__author__ = 'Richard J. Sears'
VERSION = "0.5 (2020-06-02)"

# richard@sears.net

# check_external_ip.py
# script to automate checking external ip address on my network
# and alert me via Pushbullet and email if it changes. 
# I also user noip.com and this script will automatically
# update noip.com on the fly.

## USAGE
## For complete instructions please see:
## https://github.com/rjsears/check_external_ip/blob/master/README.md

## Version 0.5 Updates
## Added check for DOCSTRING return from ipify indicating error in 
## getting external IP address. Exit when found.

## Version 0.4 Updates
## Removed ipgetter and now utilize https://ipify.org 

## Version 0.3 Updates
## Added ability to run a primary and a backup script on different servers.


# Manage Imports
from pushbullet import Pushbullet
import subprocess
import ConfigParser
import httplib
import syslog
import requests
import os
import sys

#Housekeeping
config = ConfigParser.ConfigParser()
log = syslog.syslog

# Setup to read and write to our data file:
def read_data(file, section, status):
    pathname = '/root/check_external_ip/' + file
    config.read(pathname)
    current_status = config.get(section, status)
    return current_status

def update_data(file, section, status, value):
    pathname = '/root/check_external_ip/' + file
    config.read(pathname)
    cfgfile = open(pathname, 'w')
    config.set(section, status, value)
    config.write(cfgfile)
    cfgfile.close()

# What file do we check for if we are the backup?
def check_primary():
    checkfile = read_data("checkip_data", "system_role", "checkfile") 
    if os.path.isfile('%s' % checkfile):
        primary_server = "Active"
    else:
        primary_server = "Fail"
    return primary_server


# We use Push Bullet to send out all of our alerts
def send_push(title, message):
        pbAPI = read_data("checkip_data", "system_settings", "pbAPI")
        pb = Pushbullet(pbAPI)
        push = pb.push_note(title, message)


# Setup to send email via the builtin linux mail command. Your local system should be configured already to send mail.
def send_email(recipient, subject, body):
      process = subprocess.Popen(['mail', '-s', subject, recipient],stdin=subprocess.PIPE)
      process.communicate(body)


# Are we in DEBUG mode?
def check_debug():
    DEBUG = read_data("checkip_data", "system_settings", "debug")
    if DEBUG == "True":
        return True
    else:
        return False

# Are we using noip.com?
def check_noip():
    NOIP = read_data("checkip_data", "notifications", "noip")
    if NOIP == "True":
        return True
    else:
        return False

# Are we using PushBullet?
def check_pushbullet():
    PUSHBULLET = read_data("checkip_data", "notifications", "pb")
    if PUSHBULLET == "True":
        return True
    else:
        return False

# Are we using EMail?
def check_email():
    EMAIL = read_data("checkip_data", "notifications", "email")
    if EMAIL == "True":
        return True
    else:
        return False

# Do we want to do any alerting at all?
def check_alerting():
    ALERTING = read_data("checkip_data", "notifications", "alerting")
    if ALERTING == "True":
        return True
    else:
        return False


# Do we have internet access?
def check_internet():
    check_url = read_data("checkip_data", "system_settings", "check_url")
    conn = httplib.HTTPConnection(check_url, timeout=3)
    try:
        conn.request("HEAD", "/")
        conn.close()
        return True
    except:
        conn.close()
        return False

# Here is where we check our current external IP address.
def check_ip():
    DEBUG = check_debug()
    NOIP = check_noip()
    ALERTING = check_alerting()
    current_external_ip = read_data("checkip_data", "system_settings", "current_external_ip")
    global myip
    myip = requests.get('https://api.ipify.org').text
    if myip.find('DOCSTRING') != -1:
        sys.exit()
    if DEBUG:
        print("Our external IP is: ", myip)
    if myip != current_external_ip:
        log('WARNING: External IP Address Change Detected!')
        log('Old External IP Address: {oldip}'.format(oldip=current_external_ip))
        log('New External IP Address: {ip}'.format(ip=myip))
        if DEBUG:
            print("WARNING. Your External IP Address has changed!")
        if ALERTING:    
            send_ip_warning()
        if NOIP:
            update_noip()
        update_data("checkip_data", "system_settings", "current_external_ip", myip)
    else:
        if DEBUG:
            print("Everything looks good!")

# Here is where we send PB and EMail warnings if our IP address has changed.
def send_ip_warning():
    global myip
    EMAIL = check_email()
    PUSHBULLET = check_pushbullet()
    if EMAIL:
        alert_email = read_data("checkip_data", "system_settings", "alert_email")
        send_email(alert_email, 'External IP Change', 'Your New IP is %s' %myip) 
        log('Alert Email Sent to: {email_addr}'.format(email_addr=alert_email))
    if PUSHBULLET:
        send_push("Your External IP has Changed","Your new IP is %s" % myip)
        log('PushBullet Alert Sent')

# Here is where we update noip.com if we are using this service
def update_noip():
    global myip
    HOSTNAME = read_data("checkip_data", "noip_settings", "hostname")
    USERNAME = read_data("checkip_data", "noip_settings", "username")
    PASSWORD = read_data("checkip_data", "noip_settings", "password")
    _url_ = "https://dynupdate.no-ip.com/nic/update?hostname={hostname}&myip={ip}"
    _url_called_ = _url_.format(hostname=HOSTNAME, ip=myip)
    r = requests.get(_url_called_, auth=(USERNAME, PASSWORD))
    print (r.status_code)  # if 200 this means the page was reached
    print (r.content)  # should be the response from noip.com
    if r.status_code == 200:
        success = 'yes'
    else:
        success = 'no'
    log('Updating:  www.noip.com account:')
    log('>>> NEW IP: {ip}'.format(ip=myip))
    log('>>> No-IP Update Succeed: {success}'.format(success=success))


def main():
    DEBUG = check_debug()
    if DEBUG:
        print("Starting check_external_ip.py")
    system_role = read_data("checkip_data", "system_role", "role")
    if system_role == "standalone":
        pass
    elif system_role == "primary":
        if DEBUG:
            print("We are the Primary System")
    else:
        if DEBUG:
            print("We are the Backup System")
        primary_server_active = check_primary()
        if primary_server_active == "Active":
	    checkfile = read_data("checkip_data", "system_role", "checkfile")
            if DEBUG:
                print("Primary Server is Active: Exiting")
            os.remove('%s' % checkfile)
            quit()
    internet_active = check_internet()
    if internet_active:
        check_ip()
	if system_role == "primary":
            backup_host = read_data("checkip_data", "system_role", "backup_host") 
            if DEBUG:
                print("Notifing Backup System of Success!")
	    try:
		checkfile = read_data("checkip_data", "system_role", "checkfile")
                subprocess.check_output(['ssh', backup_host, 'touch %s' % checkfile])
            except subprocess.CalledProcessError as e:
                print (e.output) 
    else:
        if DEBUG:
            print("Not detecting Internet access, quitting!")
            log('ERROR: No Internet Access Detected: Exiting!')
        quit()


if __name__ == '__main__':
    main()
