
from setuptools import setup, find_packages

setup(
    name='phyllo',
    version='0.01',
    author='Jordan Nguyen',
    authour_email='Jordan.Nguyen-1@ou.edu',
    packages=find_packages(exclude=('tests', 'docs'))
)
