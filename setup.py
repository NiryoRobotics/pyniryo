# coding=utf-8

from io import open
import sys
from setuptools import find_packages, setup

version = '1.1.1'

with open('README.rst', 'r', encoding='utf-8') as f:
    readme = f.read()

with open('requirements.txt', 'r') as f:
    REQUIRES = [str(line.replace("\n", "")) for line in f.readlines()]

kwargs = {
    'name': 'pyniryo',
    'version': version,
    'description': 'Package to control Niryo Robot "Ned" through TCP',
    'long_description': readme,
    'author': 'Niryo',
    'author_email': 'r.lux@niryo.com',
    'maintainer': 'Niryo',
    'maintainer_email': 'admin.it@niryo.com',
    'install_requires': REQUIRES,
    'include_package_data': True,
    'url': 'https://github.com/NiryoRobotics/pyniryo',
    'license': 'GNU 3.0',
    'classifiers': [
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Image Recognition",
        "Topic :: Scientific/Engineering :: Human Machine Interfaces",
    ],
    'tests_require': ['coverage', 'pytest'],
    'packages': find_packages(exclude=('tests', 'tests.*')),

}

setup(**kwargs)
