
from setuptools import setup, find_packages

setup(
    name="phyllo",
    version="0.1",
    description="PHilologicallY Linguistic LegwOrk.",
    author="Jordan Nguyen, Christan Grant",
    author_email="Jordan.Nguyen-1@ou.edu, cgrant@ou.edu",
    url="https://github.com/oudalab/phyllo",
    download_url="https://github.com/oudalab/phyllo",
    license='GPLv3',
    #packages=["phyllo", "phyllo.extractors"],
    packages=find_packages(exclude=('tests', 'docs')),
    keywords=["latin", "search"],
    install_requires=[
        "cltk",
        "beautifulsoup4",
        "html5lib"
    ],
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Topic :: Text Processing :: Linguistic",
    ],
    long_description="""\
TBD...
"""
)
