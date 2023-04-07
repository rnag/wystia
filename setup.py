"""The setup script."""
import pathlib

from setuptools import setup


here = pathlib.Path(__file__).parent

package_name = 'wystia'

packages = [
    package_name,
    f'{package_name}.utils',
    f'{package_name}.utils.parse'
]

requires = [
    'requests',
    'requests-toolbelt',
    'urllib3',  # should already be installed via requests
    'dataclass-wizard>=0.21.0,<1.0',
    'cached-property~=1.5.2; python_version == "3.7"'
]

test_requirements = [
    'pytest>=6',
    'pytest-mock~=3.6.1'
]

readme = (here / 'README.rst').read_text()
history = (here / 'HISTORY.rst').read_text()

setup(
    name='wystia',
    version='1.2.0',
    description='A Python wrapper library for the Wistia API',
    long_description=readme + '\n\n' + history,
    author='Ritvik Nag',
    author_email='rv.kvetch@gmail.com',
    url='https://github.com/rnag/wystia',
    packages=packages,
    include_package_data=True,
    python_requires='>=3.7',
    install_requires=requires,
    license='MIT',
    keywords=['wistia', 'wistia api', 'wystia',
              'wistia data api', 'wistia upload api'],
    classifiers=[
        # Ref: https://pypi.org/classifiers/
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python'
    ],
    test_suite='tests',
    tests_require=test_requirements,
    zip_safe=False
)
