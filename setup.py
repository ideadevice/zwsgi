# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

import zwsgi


install_reqs = [
    'pyzmq==14.6.0',
]

setup(
    name='calm',
    version='0.1.0',
    url='https://github.com/ideadevice/zwsgi',
    author='ID Engg.',
    install_requires=install_reqs,
    description='zeromq wsgi bridge',
    packages=find_packages(),
    include_package_data=True,
    platforms='linux',
    zip_safe=False,
)
