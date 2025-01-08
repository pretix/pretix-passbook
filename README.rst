pretix-passbook
===============

.. image:: https://img.shields.io/pypi/v/pretix-passbook.svg
   :target: https://pypi.python.org/pypi/pretix-passbook

.. image:: https://travis-ci.org/pretix/pretix-passbook.svg?branch=master
   :target: https://travis-ci.org/pretix/pretix-passbook

This is a plugin for `pretix`_. It allows to provide tickets in the pkpass format supported by Apple Wallet and a
number of Android apps.

Contributing
------------

If you like to contribute to this project, you are very welcome to do so. If you have any
questions in the process, please do not hesitate to ask us.

Please note that we have a `Code of Conduct`_ in place that applies to all project contributions, including issues,
pull requests, etc.

Development setup
^^^^^^^^^^^^^^^^^

1. Make sure that you have a working `pretix development setup`_.

2. Clone this repository, eg to ``local/pretix-passbook``.

3. Activate the virtual environment you use for pretix development.

4. Execute ``pip install -e .`` within this directory to register this application with pretix's plugin registry.

5. Execute ``make`` within this directory to compile translations.

6. Restart your local pretix server. You can now use the plugin from this repository for your events by enabling it in
   the 'plugins' tab in the settings.


Obtaining *Pass Type ID certificates* and configuring them in pretix
------------------------------------------------------------------

1. To obtain a *Pass Type ID certificate* you need to generate an *RSA private key* and a certificate signing request (CSR) using::

    export CERT_NAME=pass-pretix
    openssl genpkey -out $CERT_NAME.key -algorithm RSA -pkeyopt rsa_keygen_bits:2048
    openssl req -new -key $CERT_NAME.key -out $CERT_NAME.csr

2. Request a *Pass Type ID certificate* using the CSR (``pass-pretix.csr``) in your `Apple developer account`_ and download the certificate (as ``pass-pretix.cer``)

3. Convert the downloaded certificate to PEM format::

    openssl x509 -inform der -in $CERT_NAME.cer -out $CERT_NAME.pem
    
4. Setup your *Pass Type ID certificate* in pretix within global settings
    - Add your Team ID  
      (The Team ID can be found under "Organizational Unit" when opening the certificate, e.g. with Keychain on MacOS or you can find it in your `Apple developer account`_)
    - Add the Pass Type ID  
      (The Pass Type ID is your identifier, for example ``pass.pretix.example``)
    - Upload the *Pass Type ID certificate* (``pass-pretix.pem``)
    - Add the right *Apple Intermediate Certificate* for your certificate 
      (You can download the current certificate from Apple at https://www.apple.com/certificateauthority/AppleWWDRCAG4.cer)
    - Paste the *RSA private key* (``pass-pretix.key``) into the secret key field
    - If you have configured your *RSA private key* with a password, it is necessary to provide it in pretix
    - Click on `Save`

Enjoy!

License
-------

Copyright 2016 Tobias 'rixx' Kunze and Raphael Michel

Released under the terms of the Apache License 2.0


.. _Apple developer account: https://developer.apple.com/account/ios/certificate/
.. _pretix: https://github.com/pretix/pretix
.. _Code of Conduct: https://docs.pretix.eu/en/latest/development/contribution/codeofconduct.html
.. _pretix development setup: https://docs.pretix.eu/en/latest/development/setup.html

