from setuptools import setup, find_packages

setup(
    name='Lan Nanny',
    version='0.0.1',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=['Flask']
)

# End File: lan-nanny/setup.py
