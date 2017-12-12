#!/usr/bin/python

from __future__ import print_function

__author__ = 'Richard J. Sears'
VERSION = "0.3 (2017-12-12)"

# richard@sears.net

# check_external_ip.py
# script to automate checking external ip address on my network
# and alert me via Pushbullet and email if it changes. 
# I also user noip.com and this script will automatically
# update noip.com on the fly.

## USAGE
# Make the necessary changes to the "checkip_data" file. This is the config
# file that we read and write date to for this script.

# Call the script directly or from cron:
## */5 * * * * /usr/bin/python /root/check_external_ip_work/check_external_ip.py > /dev/null 2>&1

# Manage Imports
import ipgetter
from pushbullet import Pushbullet
import subprocess
import ConfigParser
import httplib
import syslog
import requests

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
    myip = ipgetter.myip()
    if DEBUG:
        print(myip)
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
    internet_active = check_internet()
    if internet_active:
        check_ip()
    else:
        if DEBUG:
            print("Not detecting Internet access, quitting!")
        quit()


if __name__ == '__main__':
    main()
