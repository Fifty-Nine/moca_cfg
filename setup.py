from setuptools import setup, find_packages
from textwrap import dedent

setup(
    name='moca_cfg',
    version='1.0',
    description=dedent("""Python wrapper for configuring Broadcom 6802-based
                          MoCA adapters."""),
    author_email='tim.prince@gmail.com',
    packages=find_packages(),
    install_requires=[
        'tftpy',
        'requests'
    ],
    tests_require=[
        'pytest'
    ]
)
