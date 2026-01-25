#!/bin/bash
# Get wind or wave data based on the command line switch
# Define the valid options (e.g., 'a' and 'b')
# The leading colon ':' enables silent error reporting

# Loop through all arguments provided to the script
while [[ "$#" -gt 0 ]]; do
    case $1 in
        # gather wind data
        -z|--wind)
            echo "Getting wind data from OCR"
            python3 CaptureAndStore_WxExcRocks.py -z
            shift # Move to the next argument
            ;;
        -w|--wave)
            echo "Getting wave data from OCR"
            python3 CaptureAndStore_WxExcRocks.py -w
            shift # Move to the next argument
            ;;
        *)
            # Handle unknown options or stop parsing
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done