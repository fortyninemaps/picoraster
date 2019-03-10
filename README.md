# picoraster

Lazy Python library for raster band manipulation.

## Example usage

```python
bands = []

for input in input_list:
    band = Raster(input) \
        .and_then(Resize(extents)) \
        .and_then(HistogramAdjust()) \
        .and_then(Reproject(crs))
    bands.append(end)

multiband = Merge(bands)

# Forces computation
array = multiband.render_to_array()

multiband.render_to_file("output.tif")
```

## Installation

Installing GDAL is the most challenging part. Installing directly from PyPI is unlikely to work. The best choices are one of the following:

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