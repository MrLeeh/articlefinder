#!/usr/local/bin/python
from setuptools import setup

setup(
    name='articlefinder',
    version='0.0.1',
    packages=['articlefinder',
              'articlefinder.shops',
              'articlefinder.shops.bike',
              'articlefinder.shops.electro',
              'articlefinder.core',
	          'articlefinder.gui'],
    url='https://github.com/MrLeeh/articlefinder.git',
    license='GPL',
    author='Stefan Lehmann',
    author_email='Stefan.St.Lehmann@gmail.com',
    description='Helper package for finding articles at a number of suppliers.',
    requires=["beautifulsoup4", "tabulate"],
    scripts=['scripts/run_articlefinder.pyw']
)
