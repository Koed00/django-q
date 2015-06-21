import os

from setuptools import setup

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))
from distutils.core import setup, Command
# you can also import from setuptools

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
    version='0.1.0',
    author='Ilan Steemers',
    author_email='koed00@gmail.com',
    packages=['django_q'],
    url='https://github.com/koed00/django-q',
    license='MIT',
    description='A multiprocessing task queue for Django',
    long_description=README,
    include_package_data=True,
    install_requires=['django>=1.7', 'redis', 'coloredlogs', 'django-picklefield', 'jsonpickle'],
    test_suite='django_q.tests',
    cmdclass = {'test': PyTest},
    classifiers=[
        'Development Status :: 2 - PreAlpha',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)
