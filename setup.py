import os
from setuptools import setup, Command

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))


class PyTest(Command):
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        import subprocess
        import sys

        errno = subprocess.call([sys.executable, 'runtests.py'])
        raise SystemExit(errno)


setup(
    name='django-q',
    version='1.3.4',
    author='Ilan Steemers',
    author_email='koed00@gmail.com',
    keywords='django multiprocessing worker scheduler queue',
    packages=['django_q'],
    include_package_data=True,
    url='https://django-q.readthedocs.org',
    license='MIT',
    description='A multiprocessing distributed task queue for Django',
    long_description=README,
    install_requires=['django>=2.2', 'django-picklefield', 'blessed', 'arrow'],
    test_requires=['pytest', 'pytest-django', ],
    cmdclass={'test': PyTest},
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX',
        'Operating System :: MacOS',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: System :: Distributed Computing',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    entry_points={
        'djangoq.errorreporters': [
            'rollbar = django_q_rollbar:Rollbar',
            'sentry = django_q_sentry:Sentry',
        ]
    },
    extras_require={
        'rollbar': ["django-q-rollbar>=0.1"],
        'sentry': ["django-q-sentry>=0.1"],
    }
)
