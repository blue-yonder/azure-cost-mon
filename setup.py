# coding=utf-8

# Copyright 2017 by Blue Yonder GmbH

from setuptools import setup

setup(
    name='azure_costs_exporter',
    description='A Prometheus exporter for the Azure billing API',
    author='Manuel Bähr',
    author_email='manuel.baehr@blue-yonder.com',
    url='https://github.com/blue-yonder/azure-cost-mon',
    use_scm_version=True,
    packages=['azure_costs_exporter'],
    setup_requires=['wheel', 'setuptools_scm'],
    install_requires=['flask', 'requests', 'numpy', 'pandas', 'prometheus_client'],
    classifiers=['Development Status :: 4 - Beta',
                 'Intended Audience :: Developers',
                 'Intended Audience :: System Administrators',
                 'License :: OSI Approved :: MIT License',
                 'Operating System :: POSIX :: Linux',
                 'Operating System :: MacOS :: MacOS X',
                 'Programming Language :: Python',
                 'Topic :: System :: Monitoring']
)
