import os

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
    return open(os.path.join(os.path.dirname(__file__), name)).read()


setup(
    name='gmail-connector',
    version='.'.join(str(c) for c in version_info),
    description='Python module to, send SMS, emails and read unread emails.',
    long_description=read('README.md') + '\n\n' + read('CHANGELOG'),
    long_description_content_type='text/markdown',
    url='https://github.com/thevickypedia/gmail-connector',
    author='Vignesh Sivanandha Rao',
    author_email='svignesh1793@gmail.com',
    License='MIT',
    classifiers=classifiers,
    keywords='gmail, smtp, imap, tls',
    packages=['.gmailconnector'],
    python_requires=">=3.8",
    install_requires=['python-dotenv>=0.19.2', 'pytz>=2021.1'],
    project_urls={
        'Docs': 'https://thevickypedia.github.io/gmail-connector',
        'Bug Tracker': 'https://github.com/thevickypedia/gmail-connector/issues'
    },
)
