#!/usr/bin/env python

from setuptools import setup

version = "0.1"

REQUIREMENTS = [
    "requests>=2.3.0",
    "fire"
]

setup(
  name="blinktrade-cli",
  version=version,
  author="Rodrigo Souza",
  packages = [
    "blinktrade-cli"
    ],
  entry_points = { 'console_scripts':
                     [
                       'veloxbot blinktrade-cli.blinktrade-cli:main'
                     ]
  },
  install_requires=REQUIREMENTS,
  author_email='contact@blinktrade.com',
  url='https://github.com/blinktrade/blinktrade-cli',
  description='BlinkTrade client'
)
