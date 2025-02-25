This is just the updated architecture of SiriServerCore without any Plugins, made to work with modern Google STT

If you want to configure your Mac to use SiriServer, you can edit the:

    ~/Library/Preferences/com.apple.assistant.plist

**iOS 6 Update**

I cannot guarantee that the version here will work with anything pre iOS 6.

There were some changes in iOS 6. To use the server with iOS 6 you must
disable Siri's Authentication mechanism. You can do this by adding (or via Cydia see below)

    <key>Authentication Disabled</key>
    <true/>
to

`/var/mobile/Library/Preferences/com.apple.assistant.plist`

The easiest way to do so is like this:
    
    ssh into your device
    cd /var/mobile/Library/Preferences

now edit the contents (with your favorite editor) and add (between `<dict></dict>` underneath `<keys>Account</keys>`):
    
    <key>Authentication Disabled</key>
    <true/>
 
You can also do it via iFile

What is this?
-------------
This is a very early version of a Siri Server updated to work in with modern google STT(not a proxy).

Apple's Siri is an voice controlled assistant on A5 and newer.

With jailbreaking you can install it on other iDevices.
However, Siri needs a server to communicate to do the speech processing.

This project tries to recreate the Apple Siri Server to use it with other iDevices.

It uses Google Speech-To-Text API.


Setup, Notes and Instructions
-----------------------------
*DISCLAIMER*

This project is very old and is only ment to work with python2 and or macos Mavericks or older

**Install audio libraries**

For the audio handling you need [libspeex](http://www.speex.org/) and [libflac](http://flac.sourceforge.net/)

On Linux simply install it via you packet manager e.g. (or see instructions and note for OS X):

	sudo apt-get install libspeex1 libflac8

On OS X download libspeex and libflac from the websites above (the sources, not the binaries)
and compile and install them, or simply follow the following steps:

	wget http://downloads.xiph.org/releases/speex/speex-1.2rc1.tar.gz
	tar -xf speex-1.2rc1.tar.gz
	cd speex-1.2rc1
	./configure
	make
	sudo make install
	cd ..
	
	wget http://sourceforge.net/projects/flac/files/flac-src/flac-1.2.1-src/flac-1.2.1.tar.gz/download -O flac-1.2.1.tar.gz
	tar -xf flac-1.2.1.tar.gz
	cd flac-1.2.1
	./configure --disable-asm-optimizations
	make
	sudo make install
Note: you can also install libspeex via MacPorts, but libflac is not available in 64bit through MacPorts, to make it build with 64bit support you need to supply `--disable-asm-optimizations` in configure of libflac to make it compile

**Python requirements**

As this project is coded with python you need a python interpreter (this is usually already installed).
I work with python 2.6.6 and 2.7.2 and both work.

You also need some python packages to make it work:

	[twisted](http://twistedmatrix.com/)
	
	Or pip2 install twisted
	
	[pyOpenSSL](https://launchpad.net/pyopenssl)

pyOpenSSL is also a requirement for twisted, so installing twisted will already force an installation of pyOpenSSL.

On a debian based system twisted can be installed via apt:

	sudo apt-get install python-twisted
	
If that dosent work then try any of the three:

	pip2 install twisted
	pip install twisted
	python2 -m pip install twisted

On OS X you can install it via easy_install (`sudo easy_install pyOpenSSL twisted`) or via MacPorts (`sudo port install py27-openssl py27-twisted`)


**Certificate Generation**

You also need to generate certificates for this server, they must be placed in the keys/ directory, there are dummy files to show you the correct names.

**Google STT Authentication**

You will need to aquire a google speech to text authentication file (pem or json) and edit listener.py environment variable to point to it, you will also need to install gcloud and log in via:

sudo apt-get install gcloud
gcloud auth login

**Installing API Keys**

To allow plugins to reuse API keys, there is an apiKeys.conf in the root directory of the server. (Note in this git there is only a dummy file -EXAMPLE)

The general format is as follows:

	apiName="PLUGIN-API-KEY"

The apiName is usually printed in error messages when you miss a certain API Key.

**Running the server**

Now you are ready to go, start the servers with (run each in a different terminal window):

	sudo python2 SiriServer.py --port 443
	sudo python2 listener.py

If you want to use another port use:

	python SiriServer.py --port [PORTNUM]
	
Note: for ports <= 1024 you need to run the server as root (e.g. via sudo)


Common Errors
-------------
If we had the mid 90s this section would glow and sparkle to get your attention.
There are some errors that might occur even though you did everything that was written above...

**The server just crashes after a SpeechPacket**

You are running Linux right? Probably debian?
There is probably already a libspeex on your machine which is optimized for SSE2 which does not work with python (reason???)
Check if there is a `/usr/lib/sse2/libspeex.so.1`.

Option A: delete it (there should also be a version in /usr/lib if you installed via apt, or in /usr/local/lib if you compiled by hand)

Option B: ToDo

**I cannot get a connection from device to server**

Do you access your server over the internet? You need to setup your firewall and NAT to allow traffic for tcp port 4443 directed to your server
Do you have a local firewall on the machine running the server? Also check if tcp port 4443 is allowed for incomming connections
You must also make sure to setup the corret server and port in the spire configuration:

	https://server.domain:PORT


**There is something with SSL in the error**

Have you installed the ca.pem file on your phone? Do you have more than one CA certificate installed for the same domain?

=> Try deleting all certificates on the device and install the one created by gen_certs

Can I somehow verify the correct certificate? YES!

start siriServer.py, then take your ca.pem you think belongs to your servers certificate and run:

	 echo | openssl s_client -connect [DOMAIN]:4443 2>&1 | sed -ne '/-BEGIN CERTIFICATE-/,/-END CERTIFICATE-/p' | openssl verify -CAfile keys/ca.pem 
Make sure to replace [DOMAIN] with the actual domain of the machine running siriServer.py (e.g. an IP address)
If your ca.pem matches your server certificate you should see `stdin: OK` as output!

OK, what else?
We can also setup a small test server using openssl to check if SSL is working (and to check if the iPhone correctly validates the server certificate):

	openssl s_server -cert keys/server.crt -key keys/server.key -accept 4443 -state
When you run this (SiriServer should NOT run) it opens a basis server on port 4443 using your servers certificate.

Now you can connect with your iPhone as if you would use Siri (of course Siri won't work, we are just testing the SSL layer)
It should output something like this, note the Ace http request near the end:

	 Using default temp DH parameters
	 Using default temp ECDH parameters  
	 ACCEPT
	 SSL_accept:before/accept initialization
	 SSL_accept:SSLv3 read client hello A
	 SSL_accept:SSLv3 write server hello A
	 SSL_accept:SSLv3 write certificate A
	 SSL_accept:SSLv3 write server done A
	 SSL_accept:SSLv3 flush data
	 SSL_accept:SSLv3 read client key exchange A
	 SSL_accept:SSLv3 read finished A
	 SSL_accept:SSLv3 write change cipher spec A
	 SSL_accept:SSLv3 write finished A
	 SSL_accept:SSLv3 flush data
	 -----BEGIN SSL SESSION PARAMETERS-----
	 MIGKAgEBAgIDAQQCAC8EIJ3DOw2nTgOAjdCNMqiFi+OmYU1fszwfH3jDk4q1P/mq
	 BDB7vM4nKFiGjLHpExNf4F1HZQ7ekRPaG/2X9EI/mqtpeWPp8vU1a/Em5JWomauK
	 jDShBgIETyr5oaIEAgIBLKQGBAQBAAAAphMEEWVob2VybmNoZW4uYXRoLmN4
	 -----END SSL SESSION PARAMETERS-----
 	 Shared ciphers:ECDHE-ECDSA-AES256-SHA:ECDHE-ECDSA-AES128-SHA:ECDHE-ECDSA-RC4-SHA:ECDHE-      ECDSA-DES-CBC3-SHA:ECDHE-RSA-AES256-SHA:ECDHE-RSA-AES128-SHA:ECDHE-RSA-RC4-SHA:ECDHE-RSA-DES-CBC3-SHA:ECDH-ECDSA-AES128-SHA:ECDH-ECDSA-AES256-SHA:ECDH-ECDSA-RC4-SHA:ECDH-ECDSA-DES-CBC3-SHA:ECDH-RSA-AES128-SHA:ECDH-RSA-AES256-SHA:ECDH-RSA-RC4-SHA:ECDH-RSA-DES-CBC3-   SHA:AES128-SHA:RC4-SHA:RC4-MD5:AES256-SHA:DES-CBC3-SHA:DHE-RSA-AES128-SHA:DHE-RSA-AES256-  SHA:EDH-RSA-DES-CBC3-SHA
	 CIPHER is AES128-SHA
	 Secure Renegotiation IS supported
	 ACE /ace HTTP/1.0
	 Host: DOMAIN REMOVED
	 User-Agent: Assistant(iPhone/iPhone3,1; iPhone OS/5.0.1/9A405) Ace/1.0
	 Content-Length: 2000000000


Licensing
---------
This is free software. You can reuse it under the terms of the [Creative Commons Attribution-NonCommercial-ShareAlike 3.0](http://creativecommons.org/licenses/by-nc-sa/3.0/) license. So you can do what ever you want with it. But you are not allowed to sell it. Or use it commercially to make profit.
If you like to do more than the license allows (e.g. run a commercial server and charge people for the use of it), please contact me and ask for a special commercial license. 

Disclaimer
----------
Apple owns all the rights on Siri. I do not give any warranties or guaranteed support for this software. Use it as it is.
