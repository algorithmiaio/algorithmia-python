import os

from setuptools import setup

setup(
    name='algorithmia',
    version=os.environ.get('CLIENT_VERSION', '0.0.0'),
    description='Algorithmia Python Client',
    long_description='Algorithmia Python Client is a client library for accessing Algorithmia from python code. This library also gets bundled with any Python algorithms in Algorithmia.',
    url='http://github.com/algorithmiaio/algorithmia-python',
    license='MIT',
    author='Algorithmia',
    author_email='support@algorithmia.com',
    packages=['Algorithmia'],
    entry_points = {
    'console_scripts': ['algo = Algorithmia.__main__:main']
    },
    install_requires=[
        'requests',
        'six',
        'enum-compat',
        'toml',
        'argparse',
        'algorithmia-api-client==1.5.5',
        'algorithmia-adk>=1.0.2,<1.1'
    ],
    include_package_data=True,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
