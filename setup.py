from setuptools import setup

setup(
    name='iarp_utils',
    version='0.6.2',
    description='A personal collection of common python utilities used in various projects',
    url='https://bitbucket.org/iarp/python-framework',
    author='IARP',
    author_email='iarp.opensource@gmail.com',
    license='MIT',
    packages=['iarp_utils'],
    install_requires=[
        'psutil',
    ],
    extras_require={
        'browser': ['selenium', 'requests'],
        'SQLServer': ['pyodbc'],
        'MySQL': ['mysql-connector-python'],
    },
    zip_safe=False
)
