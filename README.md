# mib2hspy
mib2hspy is a python package for converting .mib files into .hspy formats. It also provides tools for converting single frame .mib images to various image formats.

## Installation
Download this folder to some location on your local machine and unzip it. The installation details will depend on your python distribution, and this guide will show how to do it using an anaconda or miniconda distribution.

### Create environment
First, create a new python environment and install some of the required packages manually. This is best done in a conda console/terminal.

Create new environment with python 3.8 and activate it
````shell script
conda create -n mib2hpsy python=3.8
conda activate mib2hpsy
```` 

Then install some of the required packages.
```shell script
conda install hyperspy=1.5.2 -c conda-forge
conda install pyxem=0.12 -c conda-forge
```

Finally, install mib2hspy along with some minor required packages that require no specific version. This is easiest to do by navigating to the folder that contains mib2hspys `setup.py` and running:
```shell script
pip install --editable .
```
This will make mib2hspy available to your python environment, and make it possible to edit the files in the package as well.

To use the GUI parts of mib2hspy, your python environment will need PyQt5, which might or might not be simple to install (it might already be installed). From experience, issues arising from PyQt5 incompatibilities are best solved on a case-to-case basis, and this guide will not cover these issues. 

## Usage
You can use the separate tools in mib2hspy in any way you want, but most of the tools are made to work in a provided GUI. There are two main GUI tools, one for converting .mib stacks and one for converting .mib frames. The first GUI is run by calling `mib2hspy.run_gui()`, while the latter is run by calling `mib2hspy.run_converter_gui()`. You can run these GUIs from the command line like this:
```shell script
conda activate mib2hspy
python -c "from mib2hspy import run_gui; run_gui()"
```
for the .mib stack converter, or like this
```shell script
conda activate mib2hspy
python -c "from mib2hspy import run_converter_gui; run_converter_gui()"
```
for the .mib frame converter.

Alternatively, you can create a .bat file (windows) with these commands:
```shell script
#!/usr/bin/env bash
echo "Starting mib2hspy .mib stack converter gui"
call "C:\Users\<your-user-name>\Miniconda3\Scripts\activate.bat" mib2hspy & python -c "from mib2hspy import run_gui; run_gui()"
pause
```
or like this:
```shell script
#!/usr/bin/env bash
echo "Starting mib2hspy .mib frame converter gui"
call "C:\Users\<your-user-name>\Miniconda3\Scripts\activate.bat" mib2hspy & python -c "from mib2hspy import run_converter_gui; run_converter_gui()"
pause
```

The GUIs can then be run by clicking the respective .bat files.

### Calibrations
The GUIs support calibration of the data. The stack converter is more flexible, and allows for both manual calibration and calibration through calibration files. The frame converter so far only uses calibration files to calibrate the data. In addition, the frame converter uses a specific calibration file provided by this repository, while the stack converter can be set up to use calibration files located in other directories. In any event, the calibration files require a very specific header format and should appear like this:

|   Label	|   Nominal Cameralength (cm)   |   Cameralength (cm)	|   Date	|   Scale (1/Å)	|   Acceleration Voltage (V)	|   Mag mode	|   Camera	|   Microscope	|   Scale (1/nm)	   |    Scale (mrad)	|   Scale (deg)	|   Nominal Magnification ()	|   Magnification ()	   |    Scale (nm)	|   Scale (µm)	|   Mode    |
|----|----|----|----|----|----|----|----|----|----|----|----|----|----|----|----|----|
|   DIFF    |   8   |   16.20   |   2020-11-23  |   0.0135  |   20000   |   SAEDP   |   Merlin  |   2100F   |   0.00135 |   0.339450146	|   0.019449061	|   |   |   |   |   |
|   IMG    |      |      |   2020-11-20  |    |   20000   |   SAMAG   |   US1000 1  |   2100F   |     |     |       | 8000    |   9416.52 |       |   0.001486748 |   TEM |
|   IMG    |      |      |   2020-11-20  |    |   20000   |   MAG1   |   US1000 1  |   2100F   |     |     |       | 8000    |   11041 |       |   0.001268 |   TEM |
 
These tables can be made either using python (pandas is a good package for this) or in spreadsheet programs such as Excel. They should be stored e.g. as a .xlsx file, but other data formats might also work.

Calibration is performed by looking up if there are rows in the table that matches required fields. For diffraction data, `mib2hspy` will look for any rows which has a matching `Nominal Cameralength (cm)`, `Acceleration Voltage (V)`, `Camera`, and `Microscope`, and extract the corresponding scale in the row. In the future, if more than one row is found to match the metadata fields, it will select the most recent calibration after the acquisition date. For now, it selects the first match (depends on how the calibrations are ordered in the table). 

## Issues
There are some annoying issues with the GUIs which will take time to solve. For instance, if Exceptions are raised, the GUIs will exit and you must start over again. The GUIs are therefore not exceptionally user friendly if you use them in "unexpected" ways. 
