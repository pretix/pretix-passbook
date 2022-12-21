pretix-passbook
===============

.. image:: https://img.shields.io/pypi/v/pretix-passbook.svg
   :target: https://pypi.python.org/pypi/pretix-passbook

.. image:: https://travis-ci.org/pretix/pretix-passbook.svg?branch=master
   :target: https://travis-ci.org/pretix/pretix-passbook

This is a plugin for `pretix`_. It allows to provide tickets in the passbook format supported by Apple Wallet and a
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

4. Execute ``python setup.py develop`` within this directory to register this application with pretix's plugin registry.

5. Execute ``make`` within this directory to compile translations.

6. Restart your local pretix server. You can now use the plugin from this repository for your events by enabling it in
   the 'plugins' tab in the settings.


Generating Passbook keys and configuring them in pretix
-------------------------------------------------------

You can generate a key and CSR using::

    export CERT_NAME=pass-pretix
    openssl genrsa -out $CERT_NAME.key 2048
    openssl pkey -in $CERT_NAME.key -traditional > $CERT_NAME.key.pem
    openssl req -new -key $CERT_NAME.key -out $CERT_NAME.csr

You can then request a certificate using that CSR in your `Apple developer account`_. You can then convert the downloaded certificate like this::

    openssl x509 -inform der -in $CERT_NAME.cer -out $CERT_NAME.pem
    
After generating the .pem file, upload it to pretix as passbook certificate.
Make sure you have uploaded the key generated before (pass-pretix.key) and added the passbook CA of apple.
Next add your Team ID in pretix and the passbook type id. This is your identifier, as example pass.pretix.example.
If you have configured your private rsa key with a password you can provide it in pretix.

Click on Save.
Enjoy!

License
-------

Copyright 2016 Tobias 'rixx' Kunze and Raphael Michel

Released under the terms of the Apache License 2.0


.. _Apple developer account: https://developer.apple.com/account/ios/certificate/
.. _pretix: https://github.com/pretix/pretix
.. _Code of Conduct: https://docs.pretix.eu/en/latest/development/contribution/codeofconduct.html
.. _pretix development setup: https://docs.pretix.eu/en/latest/development/setup.html
