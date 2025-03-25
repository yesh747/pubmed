from setuptools import setup, find_packages

setup(
    name='pubmedquery',
    version='0.1.5',
    author='Yeshwant Chillakuru',
    description='A Python package to download data from PubMed',
    packages=find_packages(),  # Automatically discovers all packages with `__init__.py`
    install_requires=[
        'numpy',
        'pandas',
        'requests'
    ],
    python_requires='>=3.8',
)