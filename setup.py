import os
from setuptools import setup, find_packages


try:
    with open(os.path.join(os.path.dirname(__file__), 'README.rst'), encoding='utf-8') as f:
        long_description = f.read()
except:
    long_description = ''


setup(
    name='pretix-passbook',
    version='1.0.0',
    description='Passbook tickets for pretix',
    long_description=long_description,
    url='https://github.com/pretix/pretix-passbook',
    author='Tobias Kunze',
    author_email='rixx@cutebit.de',

    install_requires=['wallet-py3k'],
    packages=find_packages(exclude=['tests', 'tests.*']),
    include_package_data=True,
    entry_points="""
[pretix.plugin]
passbook=pretix_passbook:PretixPluginMeta
""",
)
