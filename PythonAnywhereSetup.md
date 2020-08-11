# Set up of a Flask Server with the Safe Paths Tools on Python Anywhere

### What is this article?

For PathCheck GPS testing, we have a selection of useful tools that are hosted on a free pythonanywhere account - various URLs under (see "Testing" below for specific URLs)

https://pathcheck.pythonanywhere.com

This document explains how to set these tools up on a new PythonAnywhere account, should you wish to do so.

It assumes access to GitHub, but does not assume that you have access to an existing PythonAnywhere account.



## Steps to Set Up the Flask Tools Server

### Create an Account

Create a free Python Anywhere account at www.pythonanywhere.com

You'll need an e-mail account, and you should verify your email address.

Note that free Python Anywhere accounts are automatically expired if you don't log in for 3 months.

### Basic Web App config

Under Web, "Add a new Web App"

Choose Flask / Python 3.8, and use default app path.

This will create a directory "mysite", with a child file "flask_app.py"



### Code from GitHub

From GitHub, take the following files and put them into the mysite directory:

https://github.com/diarmidmackenzie/safepathstools/tree/master/flask_server/project

Files to copy:

```
Into the "mysite" folder
__init__.py
views.py
scrypthash.py
generatelocation.py
jsonutils.py (from json_analysis folder)
geohashutils.py (from algorithm_test folder)

In a "mysite\templates" sub-folder
upload.html

In a "static" folder (not under mysite)
dygraph.js (from json_analysis folder)
```

Delete the flask_app.py that had been created automatically.

### Virtual Environment & Python Dependencies

Under Consoles, Start a new bash console

```
mkvirtualenv virtualenv1 --python=python3.8
pip install python-geohash
pip install flask
pip install scrypt
pip install base91
```



### Web App Set up

Under Web / Code / WSGI configuration file, edit the final line to match the line below, and save.

```
from mysite import app as application  # noqa
```

Under Web / Virtualenv, point to the Virtual Environment you set up above:

```
 /home/<user name>/.virtualenvs/virtualenv1
```

Under Static files:

```
map /static/  to /home/<user name>/static/

```

### Scrypt Binary

Python scrypt doesn't currently work on https://pythonanywhere.com because it uses an old version of TLS libraries.

So instead we put in place a scrypt executable as follows:

Download the tarball from:

https://github.com/jkalbhenn/scrypt/tarball/master

Upload this tar.gz file to /home/<user name>/

Unpack the tar file:

```
tar -xvf jkalb*.tar.gz
```

Build the code:

```
cd jkalb*
./exe/compile scrypt && ./exe/install scrypt
```

Put the binaries into suitable locations:

```
cd ~
cp jkalb*/scrypt/usr/lib/libscrypt.so .

cd .local/bin
cp ../../jkalb*/scrypt/usr/bin/scrypt-kdf .
```

Test:

```
cd ~
scrypt-kdf testpassword testsalt 4096 8 1 256
```

This should return an encrypted key and not generate any errors...


### Testing

With all of the above set up, test all of the following URLs (replace "pathcheck" with your user name)

http://pathcheck.pythonanywhere.com/location-data?longitude=1&latitude=2&points=3

http://pathcheck.pythonanywhere.com/infection-data?longitude=1&latitude=2

http://pathcheck.pythonanywhere.com/infection-data?longitude=1&latitude=2&hash=12 (takes a bit longer)

http://pathcheck.pythonanywhere.com/yaml?longitude=1&latitude=2&hds=3

http://pathcheck.pythonanywhere.com/upload (and upload a JSON location data file as output by the mobile app)


Don't worry about rendering of "notification" as "¬ification" - this is not a problem, "view source" in your browser to see the problem vanish!



### Troubleshooting

If things don't work - e.g. you hit an error page instead of getting the data you expect, best starting place is the "Error log" on the Web tab.

Together with these instructions, hopefully the most recent error message will help you to figure out what is not set up correctly.


### 

