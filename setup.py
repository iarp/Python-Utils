from setuptools import setup, find_packages

setup(
    name='iarp_utils',
    version='2.0.1',
    description='A personal collection of common python utilities used in various projects',
    url='https://bitbucket.org/iarp/iarp-python-utils/',
    author='IARP',
    author_email='iarp.opensource@gmail.com',
    license='MIT',
    packages=find_packages(exclude=["example"]),
    include_package_data=True,
    install_requires=[],
    extras_require={
        'browser': ['selenium', 'requests'],
        'SQLServer': ['pyodbc'],
        'MySQL': ['mysql-connector-python'],
        'tools': ['psutil'],
        'images': ['pillow'],
    },
    zip_safe=False
)
