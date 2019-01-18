from setuptools import setup


setup(
    name='flask-ezmail',
    version='0.6.1'
    url='https://github.com/JeffVandrewJr/flask-ezmail',
    license='MIT',
    author='Jeff Vandrew Jr',
    author_email='jeffvandrew@protonmail.ch',
    description='Flask extension for sending email',
    install_requires=[
        'blinker'
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
