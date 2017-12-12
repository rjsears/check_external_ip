check_external_ip.py
====================

This script is designed to be run from behind a network that utilizes a dynamic IP address for the external IP. I have several scripts and systems that require access to my devices behind my firewall and they utilize the external IP address to make these connections. Since the cable provider changes our IP address on a semi-regular basis, I decided to write a script that did everything that I needed it to do in our situation. This includes updating my noip.com account that I use for dynamic DNS services.

When you run the script, it will first check to see if you have internet access before doing anything else. If you do not have internet access, it will quit. If you do have internet access, it will grab your current external IP address utilizing ipgetter. Once it has your external IP address, it will check it against the IP address located in the configuration file. If it is different, it can send you a pushbullet and/or email notification, update an noip.com account and write your new IP address to your configuration file.  


## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

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


### Installing

By default, this script lives under my root directory:
```
/root/check_external_ip_work
```
However it should be able to run anywhere you would like it to run or that your user has permission to read and write since it uses python's ConfigParser.

To install, simply download the tarball or git clone the repository. Once you have placed it to where you would like it, you need to modify the checkip_data configuration file:

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
```


The setting should be pretty self explanatory:
* If you plan on using PushBullet you need to enter your PushBullet API in the ```pbapi``` field


If you plan on using PushBullet then you need to 


Say what the step will be

```
Give the example
```

And repeat

```
until finished
```

End with an example of getting some data out of the system or using it for a little demo

## Running the tests

Explain how to run the automated tests for this system

### Break down into end to end tests

Explain what these tests test and why

```
Give an example
```

### And coding style tests

Explain what these tests test and why

```
Give an example
```

## Deployment

Add additional notes about how to deploy this on a live system

## Built With

* [Dropwizard](http://www.dropwizard.io/1.0.2/docs/) - The web framework used
* [Maven](https://maven.apache.org/) - Dependency Management
* [ROME](https://rometools.github.io/rome/) - Used to generate RSS Feeds

## Contributing

Please read [CONTRIBUTING.md](https://gist.github.com/PurpleBooth/b24679402957c63ec426) for details on our code of conduct, and the process for submitting pull requests to us.

## Versioning

We use [SemVer](http://semver.org/) for versioning. For the versions available, see the [tags on this repository](https://github.com/your/project/tags). 

## Authors

* **Billie Thompson** - *Initial work* - [PurpleBooth](https://github.com/PurpleBooth)

See also the list of [contributors](https://github.com/your/project/contributors) who participated in this project.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* Hat tip to anyone who's code was used
* Inspiration
* etc
