#!/usr/bin/env python

from setuptools import setup

setup(
    name='python-netflix',
    version='0.3.0',
    install_requires=[
        'requests>=2.1.0',
        'requests-oauthlib>=0.4.0',
        'pytest'
    ],
    author='Mike Helmick',
    author_email='mikehelmick@me.com',
    license='MIT License',
    url='https://github.com/michaelhelmick/python-netflix/',
    keywords='python netflix oauth api',
    description='A Python Library to interface with Netflix REST API & OAuth',
    long_description=open('README.rst').read(),
    download_url="https://github.com/michaelhelmick/python-netflix/zipball/master",
    py_modules=["netflix"],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Communications :: Chat',
        'Topic :: Internet'
    ]
)
