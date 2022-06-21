from setuptools import setup, find_packages

setup(
    name='xd_pytools',
    version='1.0.0',
    description='A collections of helpful decorators for general use',
    author='Ryan Lague',
    author_email='ryan@xdmind.com',
    packages=find_packages(),
    install_requires=[
        'pandas'
    ]
)
