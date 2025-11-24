# coding=utf-8
import re
from pathlib import Path

from setuptools import find_packages, setup

root_path = Path(__file__).parent

VERSION = re.match(r'__version__ = ["\']((\d+\.?){3})', root_path.joinpath('pyniryo/version.py').read_text())[1]
README = root_path.joinpath('README.rst').read_text()
REQUIRES = root_path.joinpath('requirements.txt').read_text().splitlines()
DOC_REQUIRES = root_path.joinpath('docs/requirements.txt').read_text().splitlines()
TESTS_REQUIRES = root_path.joinpath('tests/requirements.txt').read_text().splitlines()
SCRIPTS_REQUIRES = root_path.joinpath('scripts/requirements.txt').read_text().splitlines()

kwargs = {
    'name':
    'pyniryo',
    'version':
    VERSION,
    'description':
    'Package to control Niryo Robot "Ned" through TCP',
    'long_description':
    README,
    'author':
    'Niryo',
    'author_email':
    'r.lux@niryo.com',
    'maintainer':
    'Niryo',
    'maintainer_email':
    'admin.it@niryo.com',
    'include_package_data':
    True,
    'url':
    'https://github.com/NiryoRobotics/pyniryo',
    'license':
    'GNU 3.0',
    'classifiers': [
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'Topic :: Scientific/Engineering :: Image Recognition',
        'Topic :: Scientific/Engineering :: Human Machine Interfaces',
    ],
    'packages':
    find_packages(exclude=('tests', 'tests.*')),
    'install_requires':
    REQUIRES,
    'tests_require':
    TESTS_REQUIRES,
    'extras_require': {
        'docs': DOC_REQUIRES,
        'tests': TESTS_REQUIRES,
        'scripts': SCRIPTS_REQUIRES,
        'dev': DOC_REQUIRES + TESTS_REQUIRES + SCRIPTS_REQUIRES,
    }
}

setup(**kwargs)
