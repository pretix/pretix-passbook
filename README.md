# pretix-passbook

[![Build Status](https://travis-ci.org/pretix/pretix-passbook.svg?branch=ci)](https://travis-ci.org/pretix/pretix-passbook)

This is a plugin for [pretix](https://github.com/pretix/pretix). It allows to provide tickets in the passbook format supported by Apple Wallet and a number of Android apps.

## Contributing

If you like to contribute to this project, you are very welcome to do so. If you have any
questions in the process, please do not hesitate to ask us.

Please note that we have a [Code of Conduct](https://docs.pretix.eu/en/latest/development/contribution/codeofconduct.html)
in place that applies to all project contributions, including issues, pull requests, etc.

### Development setup

1. Make sure that you have a working
   [pretix development setup](https://docs.pretix.eu/en/latest/development/setup.html).

2. Clone this repository, eg to `local/pretix-passbook`.

3. Activate the virtual environment you use for pretix development.

4. Execute ``python setup.py develop`` within this directory to register this application with pretix's plugin registry.

5. Execute ``make`` within this directory to compile translations.

6. Restart your local pretix server. You can now use the plugin from this repository for your events by enabling it in
   the 'plugins' tab in the settings.

## License

Copyright 2016 Tobias 'rixx' Kunze and Raphael Michel

Released under the terms of the Apache License 2.0
