"""Installer for pyDBCLI"""

try:
        from setuptools import setup, find_packages
except ImportError:
        from ez_setup import use_setuptools
        use_setuptools()
        from setuptools import setup, find_packages
setup(
    name='pyDBCLI',
    description='Python database CLI lib',
    version='0.1',
    author='Wes Mason',
    author_email='wes[at]1stvamp[dot]org',
    url='http://github.com/1stvamp/pyDBCLI',
    packages=find_packages(exclude=['ez_setup']),
    extras_require={
        'odbc': ['pyodbc>=2.0',],
    },
    license='Apache License 2.0'
)
