check_external_ip.py
====================

> Version 0.3 Updated 12/14/2017

This script is designed to be run from behind a network that utilizes a dynamic IP address for the external IP. I have several scripts and systems that require access to my devices behind my firewall and they utilize the external IP address to make these connections. Since the cable provider changes our IP address on a semi-regular basis, I decided to write a script that did everything that I needed it to do in our situation. This includes updating my noip.com account that I use for dynamic DNS services.

This script can be configured to run in three different modes: 
* Standalone - Script is configured and run on a single system.
* Primary - Script is setup as the Primary script in a Primary/Backup configuration.
* Backup - Script is configured as the backup and will not check it's IP so long as the Primary reports its success. Designed to be run on two different system and in the event the Primary system fails to report a success to the backup system, the backup system will run the check.

#### Standalone
When you run the script in Standalone mode, it will first check to see if you have internet access before doing anything else. If you do not have internet access, it will quit. If you do have internet access, it will grab your current external IP address utilizing ipgetter. Once it has your external IP address, it will check it against the IP address located in the configuration file. If it is different, it can send you a pushbullet and/or email notification, update an noip.com account and write your new IP address to your configuration file.  

#### Primary
When you run the script in Primary mode, it will first check to see if you have internet access before doing anything else. If you do not have internet access, it will quit. If you do have internet access, it will grab your current external IP address utilizing ipgetter. Once it has your external IP address, it will check it against the IP address located in the configuration file. If it is different, it can send you a pushbullet and/or email notification, update an noip.com account and write your new IP address to your configuration file. Once it has completed it's check, it will notify the backup system (utilizing ssh to touch a checkfile) that is has completed it's checks.

#### Backup
When you run the script in Backup mode it will check to see if the configured checkfile exists. This checkfile will only exist if the Primary has completed a sucessful check. If the checkfile exists, the script removes the checkfile and quits. If the checkfile does not exist, then the scripts assumes that the Primary failed (system crashed, etc) and it will revert it's operation to standalone mode until such time as the Primary comes back online.


### Prerequisites
This script should run on any system that can run python. I am running this on a Raspberry Pi3 utilizing Python 2.7.9. The only things that I added to my python install that I user are:

* [ipgetter](https://github.com/phoemur/ipgetter) - Python scrip that gets current external IP address. 

- Utilizes a list of websites that provide this service and randomaly grabs one to use. I had issues with a few of the websites and had to edit the script to get it to work correctly. In once case, one of the websites actually returned my "local" IP which caused some interesting problems until I figured out which one it was. The ipgetter script has a builtin test you can run to check all websites for accuracy and to help you clean up the list. The list of websites that I use are listed in (list_of_ip_websites).  

To install ipgetter simply type:
```
pip install ipgetter
```


* [pushbullet](https://github.com/randomchars/pushbullet.py) - Python script to interact with PushBullet

* In order to use the PushBullet API you need an API key that can be obtained
[here](https://www.pushbullet.com/account). This is user specific and is used instead of passwords.

To install pushbullet simply type:
```
pip install pushbullet.py
```

Everything else you need to run this script should be loaded with python, but as in all things - your milage may vary!

* SSH
In order for the scripts to operate in Primary/Backup roles, ssh is used to touch a checkfile on the backup system. As a result, you will need to configure ssh for a passwordless, key-based operation. You should be fully aware of any security risks associated with utilizing ssh in this manner and it is recommended that you do not use the root account when you operate in this manner.
[HERE](https://www.tecmint.com/ssh-passwordless-login-using-ssh-keygen-in-5-easy-steps/) is a great tutorial on setting up passwordless ssh sessions. If you plan to operate in Standalone mode, this is not necessary.

## Installing

By default, this script lives under my root directory:
```
/root/check_external_ip_work
```
However it should be able to run anywhere you would like it to run or that your user has permission to read and write since it uses python's ConfigParser. If you are planning on using the system in Primary/Backup roles you may want to create a specific user and directory outside of /root.

To install, simply download the tarball or git clone the repository. Once you have placed it to where you would like it, you need to make it executable:
``` chmod +x check_external_ip.py ```

You then need to modify the checkip_data configuration file:

```
[system_settings]
debug = True
pbapi = x.xxxxxxxxxxxxxxxxxxxxxxxx
current_external_ip = 0.0.0.0
alert_email = some_email@your_domain.com
check_url = www.google.com

[notifications]
alerting = True
noip = True
pb = True
email = True

[noip_settings]
hostname = yourdomain.ddns.net
username = your_login_name
password = your_login_password

[system_role]
role = backup
backup_host = scruffy
checkfile = /root/check_external_ip_work/primary_is_active
```


The setting should be pretty self explanatory:
* If you want to do **any** alerting, ```alerting``` needs to be set to ``` alerting = True``` 
* If you plan on using PushBullet you need to enter your PushBullet API in the ```pbapi``` field
* If you want to use email alerting you need to enter ```True``` in the email field: ```email = True```
You also need to enter the email address to which you want to receive alerts: ```alert_email = some_email@your_domain.com```. This is setup to use the local system ```mail``` command so your local system must be able to send email already via the builtin ```mail``` command. If it cannot, this will not work for you.
* If you want to use noip.com this requires either a free or paid account. Once your account is setup, change the settings under the ```noip_settings``` section to match your noip.com account.
* You need to set ```role``` to standalone, primary or backup (lower case) depending on your intended mode of operation.
* You need to set ```backup_host``` to the hostname or IP address of the backup server if this is the primary server. It is unused if this is the backup server.
* You need to set ```checkfile``` to the full path of the checkfile you intend to use. This MUST be the same on both the Primary and the Backup configurations.

If you do change the base directory where you are operating the script, you need to edit the main script and change that location in the config file function:

```
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
```
Change the pathname to the path where you are running your script.

## Running
### crontab
To run the script via crontab, issue the crontab command for your system ex:```crontab -e``` and edit your crontab file to reflect the time and directory where you have installed the script:
```
*/5 * * * * /usr/bin/python /root/check_external_ip_work/check_external_ip.py > /dev/null 2>&1
```

>NOTE: If you are running in Primary/Backup mode, then you want to make sure that your Primary server always runs first as this will create the checkfile on the backup system letting it know that it has already been successful. I would recommend getting the scripts setup the way you want them, test them both to make sure they work properly (test the backup first, it reverts to standalone mode if it does not see a checkfile) and once you verify that everything works, setup your crontab to have the scripts one minute apart. Once you have done this, manually run the script on the **primary** system and this will create the checkfile on the backup system.

> ### Primary Cron Entry:
>```1,6,11,16,21,26,31,36,41,46,51,56 * * * * /usr/bin/python /root/check_external_ip_work/check_external_ip.py > /dev/null 2>&1```

> ### Backup Cron Entry:
>```2,7,12,17,22,27,32,37,42,47,52,57 * * * * /usr/bin/python /root/check_external_ip_work/check_external_ip.py > /dev/null 2>&1```

### CLI
You can also call the script directly from the command line if you wish:
```
root scruffy: check_external_ip_work #  ./check_external_ip.py
Starting check_external_ip.py
We are the Primary System
Our external IP is:  62.21.67.222
Everything looks good!
Notifing Backup System of Success!
```
Add on the backup system:
```
root backup-scruffy: check_external_ip_work# ./check_external_ip.py
Starting check_external_ip.py
We are the Backup System
Primary Server is Active: Exiting
```


## Logging
By default the script logs to syslog ```/var/log/syslog```, but only when there is a change. If you have an IP address change, and depending on the configuration options you have selected, this is what your logfile entry should look like:

```
Dec 12 15:26:15 scruffy check_external_ip.py: WARNING: External IP Address Change Detected!
Dec 12 15:26:15 scruffy check_external_ip.py: Old External IP Address: 0.0.0.0
Dec 12 15:26:15 scruffy check_external_ip.py: New External IP Address: 64.233.97.222
Dec 12 15:26:16 scruffy check_external_ip.py: Alert Email Sent to: my_email_address@gmail.com
Dec 12 15:26:17 scruffy check_external_ip.py: PushBullet Alert Sent
Dec 12 15:26:17 scruffy check_external_ip.py: Updating:  www.noip.com account:
Dec 12 15:26:17 scruffy check_external_ip.py: >>> NEW IP: 64.233.97.222
Dec 12 15:26:17 scruffy check_external_ip.py: >>> No-IP Update Succeed: yes
```

## Authors

* **Richard J. Sears** - *richard@sears.net* - [The RS Technical Group, Inc.](http://github.com/rjsears)

## License

This project is licensed under the MIT License - see the MIT License for details

## Acknowledgments

* [Phoemur](https://github.com/phoemur) - ipgetter
* [Randomchars](https://github.com/randomchars) - pushbullet.py
* My amazing family that puts up with all of my coding projects!
