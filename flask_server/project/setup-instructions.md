We use a command line scrypt utility.

https://github.com/jkalbhenn/scrypt

reason for this is that the native python hashlib scrypt implementation only works with OpenSSl 1.1+, which is not installed on pythonanywhere (and that's hard to fix)

Setting up scrypt

tar -xvf scrypt-0.4.tar
./exe/compile scrypt
./exe/install scrypt

Then I positioned libraries and binaries as follows:

16:03 /usr/bin $ cd /home/diarmidmackenzie/.local/bin
16:03 ~/.local/bin $ cp ~/scrypt-0.4/scrypt/usr/bin/scrypt-kdf .
16:03 ~/.local/bin $ cd ~
16:03 ~ $ cp ~/scrypt-0.4/scrypt/usr/lib/libscrypt.so .



Finally I set the working directory for the Python Anywhere site to 

/home/diarmidmackenzie/

This allows libscrypt.so to be picked up from the working directory
(I tried LD_LIBRARY_PATH, but had trouble making the environment variable persist).








​	