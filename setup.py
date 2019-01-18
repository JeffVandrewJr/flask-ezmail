import setuptools
from setuptools import setup


setup(
    name='flask-ezmail',
    version='0.6.2',
    url='https://github.com/JeffVandrewJr/flask-ezmail',
    license='MIT',
    author='Jeff Vandrew Jr',
    author_email='jeffvandrew@protonmail.ch',
    description='Flask extension for sending email',
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
