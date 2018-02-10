#!/usr/bin/env python
from setuptools import setup, find_packages

setup(
    name='synamic',
    version='0.2.dev',
    description='Synamic',
    author='Md. Sabuj Sarker',
    author_email='md.sabuj.sarker@gmail.com',
    url='https://github.com/SabujXi/Synamic',
    packages=find_packages('src', exclude=('synamic',)),
    package_dir={'': 'src'},
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'synamic = synamic.entry_points.synamic_shell:main'
        ]
    },
    data_files=[('', ['README.md', 'LICENSE'])]
)

# print(find_packages('src', exclude=('synamic',)))
