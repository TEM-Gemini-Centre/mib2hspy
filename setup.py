from setuptools import setup, find_packages

setup(
    name='mib2hspy',
    version='0.1.1',
    license='mit',
    author='Emil Christiansen',
    author_email='emil.christiansen@ntnu.no',
    description="Converting .mib data to hspy supported formats",
    long_description=open('README.md').read(),
    classifiers=[
        "Programming Language :: Python :: 3.8",
        "Intended Audience :: Science/Research",
        "License :: MIT",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Physics",
    ],
    packages=find_packages(),
    install_requires=[
        "PyQt5",
        "hyperspy",
        "pyxem",
        "numpy",
        "matplotlib",
        "pathlib",
        "tabulate",
        "datetime",
        "pandas",
        "openpyxl",
    ],
    package_data={
        "": ["LICENSE", "README.md"],
        "": ["*.py"],
        "": ["*.ipynb"],
    },
)