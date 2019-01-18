import setuptools
from setuptools import setup

with open('README.md', 'r') as fh:
    long_description = fh.read()

setup(
    name='flask-ezmail',
    version='0.6.3',
    url='https://github.com/JeffVandrewJr/flask-ezmail',
    license='MIT',
    author='Jeff Vandrew Jr',
    author_email='jeffvandrew@protonmail.ch',
    description='Flask extension for sending email',
    long_description=long_description,
    long_description_content_type='text/markdown',
    install_requires=[
        'blinker'
    ],
    packages=setuptools.find_packages(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
