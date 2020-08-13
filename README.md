# BlenderOpenData
Python tool to extract data from Blender Benchmark Open Data JSON files (https://opendata.blender.org/)

Benchmark data can be downloaded from:
* https://opendata.blender.org/raw-data/
* https://opendata.blender.org/snapshots/

The option _--latest_ automatically downloads the latest data from https://opendata.blender.org/snapshots/opendata-latest.zip

## Usage

    Extract statistics from Blender Benchmark Opendata: Scene render times per OS or devices
    
    Usage: blender-opendata.py [-d render_device] [-o os] [-v] [--list-os|--list-devices] <json_file>|--latest
    
    Examples:
        blender-opendata.py -o Linux-64bit -d "AMD Ryzen 5 3600 6-Core Processor" file.json
        blender-opendata.py -v -d "GeForce GTX 950" -d "GeForce GTX 1650 SUPER" --latest
        blender-opendata.py -o Linux-64bit --list-devices file.json
    
    OS:
        Linux-64bit
        Windows-64bit
    
    Devices:
        GeForce GTX 950
        GeForce GTX 1650 SUPER
        AMD Ryzen 5 1600 Six-Core Processor
        AMD Ryzen 5 3600 6-Core Processor
        AMD Ryzen 7 3700X 8-Core Processor


