from setuptools import setup

setup(
    name='iarp_utils',
    version='0.6.8',
    description='A personal collection of common python utilities used in various projects',
    url='https://bitbucket.org/iarp/iarp-python-utils/',
    author='IARP',
    author_email='iarp.opensource@gmail.com',
    license='MIT',
    packages=['iarp_utils'],
    install_requires=[],
    extras_require={
        'browser': ['selenium', 'requests'],
        'SQLServer': ['pyodbc'],
        'MySQL': ['mysql-connector-python'],
        'tools': ['psutil'],
    },
    zip_safe=False
)
