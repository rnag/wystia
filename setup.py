#!/usr/bin/env python

"""The setup script."""

from setuptools import setup


with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

packages = [
    'wystia',
    'wystia.utils',
    'wystia.utils.parse'
]

requires = [
    'requests',
    'requests-toolbelt',
    'urllib3',
    'dataclasses; python_version == "3.6"',
    'backports-datetime-fromisoformat~=1.0.0; python_version < "3.7"'
]

test_requirements = [
    'pytest>=6',
    'pytest-mock~=3.6.1'
]

setup(
    name='wystia',
    version='0.3.0',
    description='A Python wrapper library for the Wistia API',
    long_description=readme + '\n\n' + history,
    author='Ritvik Nag',
    author_email='rv.kvetch@gmail.com',
    url='https://github.com/rnag/wystia',
    packages=packages,
    include_package_data=True,
    python_requires='>=3.5',
    install_requires=requires,
    license='MIT',
    keywords=['wistia', 'wistia api', 'wystia',
              'wistia data api', 'wistia upload api'],
    zip_safe=False,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3 :: Only'
    ],
    test_suite='tests',
    tests_require=test_requirements,
)
