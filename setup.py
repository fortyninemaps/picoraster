import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="picoraster",
    version="0.0.1",
    author="Nat Wilson",
    author_email="natw@fortyninemaps.com",
    description="Lazy raster band processing",
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=["numpy>=1.1", "GDAL>=2.0"],
    python_requires=">3.3",
    package_dir={'picoraster': 'src'},
    packages=['picoraster'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: GIS",
    ],
)