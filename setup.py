# coding=utf-8

# Copyright 2017 by Blue Yonder GmbH

from setuptools import setup

setup(
    name='azure-billing-exporter',
    description='Prometheus scraper for the Azure billing API',
    author='Manuel Bähr',
    author_email='manuel.baehr@blue-yonder.com',
    use_scm_version=True,
    packages=['azure_billing'],
    setup_requires=['wheel', 'setuptools_scm'],
    install_requires=['flask', 'requests', 'numpy', 'pandas'],
)
