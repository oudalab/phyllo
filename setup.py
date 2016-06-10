from setuptools import setup

setup(
    name="phyllo",
    packages=["phyllo"],
    version="0.0.1",
    description="PHilologicallY Linguistic LegwOrk.",
    author="Christan Grant",
    author_email="cgrant@ou.edu",
    url="https://github.com/oudalab/phyllo",
    download_url="https://github.com/oudalab/phyllo",
    keywords=["latin", "search"],
    install_requires=[
        "cltk",
        "sqlite3"
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