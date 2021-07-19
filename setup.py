from os import path

from setuptools import setup

from version import version_info

classifiers = [
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Telecommunications Industry',
    'Operating System :: MacOS :: MacOS X',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3.9',
    'Topic :: Communications :: Email :: Post-Office :: IMAP'
]


def read(name):
    """https://pythonhosted.org/an_example_pypi_project/setuptools.html#setting-up-setup-py - reference."""
    return open(path.join(path.dirname(__file__), name)).read()


setup(
    name='gmail-connector',
    version='.'.join(str(c) for c in version_info),
    description='Python module to, send SMS, emails and read unread emails.',
    long_description=read('README.md') + '\n\n' + read('CHANGELOG'),
    url='https://github.com/thevickypedia/gmail-connector',
    author='Vignesh Sivanandha Rao',
    author_email='svignesh1793@gmail.com',
    License='MIT',
    classifiers=classifiers,
    keywords='gmail, smtp, imap, tls',
    packages=['.gmailconnector'],
    install_requires=['']
)
