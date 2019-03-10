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