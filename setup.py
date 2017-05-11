# coding=utf-8

# Copyright 2017 by Blue Yonder GmbH

from setuptools import setup

setup(
    name='azure-cost-mon',
    description='Prometheus scraper for the Azure billing API',
    author='Manuel Bähr',
    author_email='manuel.baehr@blue-yonder.com',
    url='https://github.com/blue-yonder/azure-cost-mon',
    use_scm_version=True,
    packages=['azure_billing'],
    setup_requires=['wheel', 'setuptools_scm'],
    install_requires=['flask', 'requests', 'numpy', 'pandas'],
    classifiers=['Development Status :: 4 - Beta',
                 'Intended Audience :: Developers',
                 'Intended Audience :: System Administrators',
                 'License :: OSI Approved :: MIT License',
                 'Operating System :: POSIX :: Linux',
                 'Operating System :: MacOS :: MacOS X',
                 'Programming Language :: Python',
                 'Topic :: System :: Monitoring']
)
