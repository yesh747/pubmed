from setuptools import setup, find_packages

setup(
    name='pubmedquery',
    version='0.1.12',
    author='Yeshwant Chillakuru',
    description='A Python package to download data from PubMed',
    long_description='Please refer to the GitHub page for more information / documentation',
    packages=find_packages(),  # Automatically discovers all packages with `__init__.py`
    install_requires=[
        'numpy',
        'pandas',
        'requests'
    ],
    python_requires='>=3.8',
)