import os
from distutils.command.build import build

from django.core import management
from setuptools import setup, find_packages


try:
    with open(os.path.join(os.path.dirname(__file__), 'README.rst'), encoding='utf-8') as f:
        long_description = f.read()
except:
    long_description = ''


class CustomBuild(build):
    def run(self):
        management.call_command('compilemessages', verbosity=1)
        build.run(self)


cmdclass = {
    'build': CustomBuild
}


setup(
    name='pretix-passbook',
    version='1.10.0',
    description='Passbook tickets for pretix',
    long_description=long_description,
    url='https://github.com/pretix/pretix-passbook',
    author='Tobias Kunze',
    author_email='rixx@cutebit.de',
    license='Apache License 2.0',

    install_requires=['wallet-py3k', 'googlemaps'],
    packages=find_packages(exclude=['tests', 'tests.*']),
    include_package_data=True,
    cmdclass=cmdclass,
    entry_points="""
[pretix.plugin]
passbook=pretix_passbook:PretixPluginMeta
""",
)
