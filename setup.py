'''
pytz setup script
'''
import os
import re

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

me = 'Aman Bothra'
memail = 'amanbothra1777@gmail.com'

packages = ['ab_drf', 'ab_drf.mixins']
package_dir = {'ab_drf': 'src/ab_drf'}
install_requires = open('requirements.txt', 'r').readlines()

setup(
    name='ab_drf',
    version='0.1',
    zip_safe=True,
    description='A few extensions to DRF.',
    author=me,
    author_email=memail,
    maintainer=me,
    maintainer_email=memail,
    install_requires=install_requires,
    url='https://github.com/AmanBothra/ab_utils',
    license=open('LICENSE', 'r').read(),
    keywords=['djangorestframework', 'drf'],
    packages=packages,
    package_dir=package_dir,
    platforms=['Independant'],
    classifiers=[
        'Development Status :: 1 - beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)