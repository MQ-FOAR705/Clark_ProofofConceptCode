#https://github.com/pypa/sampleproject/blob/master/setup.py
from setuptools import setup, find_packages

setup(
    name="discogs_api_poc",
    version="0.0.1dev1",
    description='Proof of Concept  for FOAR705 2019',
    author="Matthew Clark",
    author_email='matthew.clark3@hdr.mq.edu.au',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha'
        'Intended Audience :: Education'
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)'
        'Natural Language :: English'
        'Operating System :: OS Independent'
        'Programming Language :: Python :: 2.7'
    ],
    install_requires=[
        'oauth',
        'oauth2',
        'numpy',
        ],
    packages=[
        'foar705_clark_poc'
        ],
    python_requires='>=2.7',
)
