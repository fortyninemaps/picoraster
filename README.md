# picoraster

Small Python library for processing large raster images.

Currently a work in progress.

## Example usage

```python
source = AWSLandsat8Source("LC08_L1TP_139045_20170304_20170316_01_T1", band="8")

# Lazily create a band and build a description of processing steps
band = Band(source) \
    .and_then(Resize(extents)) \
    .and_then(HistogramAdjust()) \
    .and_then(Reproject(crs))

# Forces computation
array = band.render_to_array()

band.render_to_file("output.tif")
```

## Installation

Installing GDAL is the most challenging part. Installing directly from PyPI is historically unlikely to work.

First, install numpy:
`pip install numpy`

Then, choose one of the following:

- install with a system package manager
    - Ubuntu: `sudo apt install libgdal-dev`
    - MacOS: `brew install gdal`
- install from conda-forge: `conda install -c conda-forge gdal`
- [compile manually](http://trac.osgeo.org/gdal/wiki/BuildHints)

Afterwards, the correct Python bindings can be installed with
```bash
pip install GDAL==$(gdal-config --version) --global-option=build_ext --global-option="-I/usr/include/gdal" 
```

Finally,
`pip install picoraster`

## Running tests

`python -m src.tests`