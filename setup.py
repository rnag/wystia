#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = ['requests',
                'requests-toolbelt',
                'urllib3']

test_requirements = ['pytest>=6']

setup(
    author='Ritvik Nag',
    author_email='rv.kvetch@gmail.com',
    python_requires='>=3.7',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10'
    ],
    description='A Python wrapper library for the Wistia API',
    install_requires=requirements,
    license='MIT license',
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords=['wistia', 'wistia api', 'wistia data api', 'wistia upload api', 'wystia'],
    name='wystia',
    packages=find_packages(include=['wystia', 'wystia.*']),
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/rnag/wystia',
    version='0.1.0',
    zip_safe=False,
)
