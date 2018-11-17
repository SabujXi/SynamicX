#!/usr/bin/env python
from setuptools import setup, find_packages

with open('README.rst', 'r', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='synamic',
    version='0.5.2.dev5',
    description='Synamic',
    author='Md. Sabuj Sarker',
    author_email='md.sabuj.sarker@gmail.com',
    url='https://github.com/SabujXi/Synamic',
    packages=find_packages('src'),
    # packages=find_packages('src', exclude=('synamic',)),
    package_dir={'': 'src'},
    entry_points={
        'console_scripts': [
            'synamic = synamic.entry_points.synamic_shell:main'
        ]
    },
    data_files=[('', ['README.rst', 'LICENSE'])],
    package_data={
        '': ['*.model', '*.syd', '*.txt', '*.rst', '*.md', '*.markdown'],
    },
    install_requires=[
        'Jinja2>=2.10',
        'MarkupSafe>=1.0',
        'mistune>=0.8.3',
        'Pillow>=5.2.0',
        'sly>=0.3',
        'aiohttp>=3.4.4',
    ],
    python_requires='>=3.6',
    long_description=long_description
)

# print(find_packages('src', exclude=('synamic',)))
