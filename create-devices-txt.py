#!/usr/bin/env python3

import argparse
import osmosdr
import re


def argument_parser():
    parser = argparse.ArgumentParser(description="A script to detect SDR devices and generate a devices.txt file for challengectl.")
    parser.add_argument("-f", "--file", default="devices.txt", help="Output file")
    parser.add_argument("-p", "--printonly", action="store_true", help="Print results to screen, and do not write to file.")
    parser.add_argument("-b", "--disablebiastee", action="store_true", help="Disable bladeRF biastee (enabled by default).")
    parser.add_argument("-v", "--verbose", action="store_true")
    return parser

def main(options=None):
    if options is None:
        options = argument_parser().parse_args()

    args = options
    verbose = args.verbose
    printonly = args.printonly
    outputfile = args.file
    disablebiastee = args.disablebiastee


    # This list will hold the GrOsmoSDR device strings
    sdrstrings = []
    
    # Find devices through osmosdr
    devices = osmosdr.device.find()
    
    for device in devices:
        # Get strings for each device identified by osmosdr
        devicestring = device.to_string()
        # Split string so we can find the attributes that we want
        attributes = devicestring.split(',')
    
        # Find UHD / USRP devices
        if("uhd" in attributes):
            # uhd_find_devices returns non-USRP devices from soapy
            # Ignore any soapy entries
            if("type=soapy" in attributes):
                continue
            uhdtype = ""
            uhdserial = ""
            for item in attributes:
                # USRP type
                if(item.startswith("type=")):
                    uhdtype = item
                # USRP serial number
                elif(item.startswith("serial=")):
                    uhdserial = item
    
            # Skip device if either type or serial are empty
            if(uhdtype != "" and uhdserial != ""):
                # Generate UHD device string
                # Example: "uhd,type=b200,serial=<serialnumber>"
                uhdstring = "uhd,{},{}".format(uhdtype, uhdserial)
                if(verbose):
                    print(uhdstring)
                # Add UHD device string to the list
                sdrstrings.append(uhdstring)
            else:
                print("WARNING: UHD device skipped")
                print("uhdtype: {}".format(uhdtype))
                print("uhdserial: {}".format(uhdserial))
    
        # Find bladeRF devices
        elif("driver=bladerf" in attributes):
            for item in attributes:
                bladerfstring = "bladerf=<serial>,biastee=1"
                if(item.startswith("serial=")):
                    # Remove 'serial=' bladeRF serial number
                    bladerfserial = item[7:]
    
            # Skip device if serial is empty
            if(bladerfserial != ""):
                bladerfbiastee = "biastee=1"
                if(disablebiastee == True):
                    bladerfbiastee = "biastee=0"
                # Generate bladeRF device string
                # Example: "bladerf=<serialnumber>,biastee=1"
                bladerfstring = "bladerf={},{}".format(bladerfserial, bladerfbiastee)
                if(verbose):
                    print(bladerfstring)
                sdrstrings.append(bladerfstring)
            else:
                print("WARNING: bladeRF device skipped")
                print("bladerfserial: {}".format(bladerfserial))
    
        # Find HackRF devices
        elif("driver=hackrf" in attributes):
            for item in attributes:
                if(item.startswith("serial=")):
                    # Remove 'serial=' and leading zeros from HackRF serial number
                    hackrfserial = re.sub("^serial=0+(?!$)", "", item)
    
            # Skip device if serial is empty
            if(hackrfserial != ""):
                # Generate hackRF device string
                # Example: "hackrf=<serialnumber>"
                hackrfstring = "hackrf={}".format(hackrfserial)
                if(verbose):
                    print(hackrfstring)
                sdrstrings.append(hackrfstring)
            else:
                print("WARNING: HackRF device skipped")
                print("hackrfserial: {}".format(hackrfserial))
    
    # Generate strings for challengectl devices.txt file
    outputstrings = []
    index = 0
    for sdr in sdrstrings:
        sdrstring = "{},\"{}\"".format(index, sdr)
        outputstrings.append(sdrstring)
        index += 1

    # Print devices.txt strings to screen, and write to outputfile if printonly is not set.
    if(printonly == True):
        for string in outputstrings:
            print(string)
    else:
        with open(outputfile, 'w') as fh:
            for string in outputstrings:
                print(string)
                fh.write(string)
                fh.write('\n')


if __name__ == '__main__':
    main()
