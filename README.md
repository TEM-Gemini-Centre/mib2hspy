# mib2hspy

This python package supplies a notebook and a gui tool to convert .mib data files to other data file types such as .hspy and .blo.

## Installation and requirements
This module requires, in particular, pyxem (works with 0.13.3), PyQt5, tabulate, and pathlib.

You can install this package by creating a new environment and run `setup.py` like this:

```shell script
conda create -n mib2hspy python=3.9 pyxem=0.13.3 tabulate pathlib -c conda-forge
conda activate mib2hspy
cd <path-to-mib2hspy setup.py>
pip install --editable .
```

## Usage
Run the GUI by opening a conda shell, activate the appropriate environment and running the the gui through python:
```shell script
conda activate mib2hspy
python -c "from mib2hspy import run_gui; run_gui()"
```