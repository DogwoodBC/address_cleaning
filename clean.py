import csv
import requests
import xml.etree.ElementTree as ET
import xmltodict
import argparse
from pprint import pprint

parser = argparse.ArgumentParser(description='Clean addresses using geocoder.ca service.')
parser.add_argument('-f', metavar='N', type=str, help='a name for the file to clean up.  Must be a csv.')
parser.add_argument('-o', metavar='N', type=str, help='a name for the output file.  Must be a csv.')

args = parser.parse_args()

# This will throw error with no input -f since we're not committing this file
file_name = args.f if args.f else "dogwood_sample_address_data.csv"
write_file_name = args.o if args.o else "output.csv"

print("Opening " + file_name)
print("Outputting to " + write_file_name)

with open(file_name) as csvfile:
    addresses = csv.DictReader(csvfile)
    with open(write_file_name, 'w') as csvfile2:
        prefix = "Matched "
        fieldnames = ['Primary Street', 'Primary City', 'Primary Province/State', 'Primary Postal Code/Zip', 'Contact ID',
        prefix + ' confidence',
        prefix + 'No.',
        prefix + 'Address',
        prefix + 'City',
        prefix + 'Postal Code',
        prefix + 'Long',
        prefix + 'Lat']
        writer = csv.DictWriter(csvfile2, fieldnames=fieldnames, extrasaction="raise")
        writer.writeheader()
        for row in addresses:
            # print(row)

            street = row['Primary Street']
            province = row['Primary Province/State']
            city = row['Primary City']
            query = "addresst=" + street + "&prov=" + province
            if(len(city) > 0):
                query += "&city=" + city
            url =  "http://geocoder.ca/?" + query + "&geoit=XML"
            r = requests.get(url)

            #parse
            root = ET.fromstring(r.text)
            error = root.findall("./error")
            if(error):
                print(error[0][0].text)
            else:
                info = xmltodict.parse(r.text)
                if(float(info['geodata']['standard']['confidence']) > 0.7):
                    row[prefix + 'No.'] = info['geodata']['standard']['stnumber']
                    row[prefix + 'Address'] = info['geodata']['standard']['staddress']
                    row[prefix + 'City'] = info['geodata']['standard']['city']
                    row[prefix + 'Postal Code'] = info['geodata']['postal']
                    row[prefix + 'Long'] = info['geodata']['longt']
                    row[prefix + 'Lat'] = info['geodata']['latt']
                    row[prefix + ' confidence'] = info['geodata']['standard']['confidence']

            writer.writerow(row)
