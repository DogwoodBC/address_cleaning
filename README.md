# Geocoding and Address Cleaning Script

### Instructions for use
- Make sure you have python version 3.4 or greater installed
- run `pip install -r requirements.txt`
- get google geocoder API keys here https://developers.google.com/maps/documentation/geocoding/start.  Scroll down to *Activate the API and get an API key*.
- add your API key as environment variable called `GOOGLEMAPS_KEY` by running `export GOOGLEMAPS_KEY=yourapikeyhere`
- to clean addresses, run `python clean.py -f name_of_input_file_here -o name_of_output_file_here`
- the google geocoder is not run by default to prevent accidently surpassing API daily quotas.  To include it in the search, use the flag `g` as in `python clean.py -g True`
- you can also run `python clean --help` to display options.


All added columns are prefixed with the name of the geocoder service.  This geocoder only queries BC addresses.
