# OCRWeather

This is a tool designed to collect wind and wave information from a publicly available and displayed weather buoy. It is located within 2 nm of our sailing club and all I seek to do is to proved realtime and some historical data (24hrs). Once upon a time the buoys were funded (and still are) by NOAA and the NWS but run by the University of Ct, Bridgeport. For a while, the NWS carried and cataloged the data from these buoys and an app I wrote for display at our club relied on this public database. At some point NERACOOS buoys were updated and the NWS, though listing these resources, no longer adds to their database. I suspect that these devices have to go through a vetting period and it will be a while as the reliability and accuracy of these buoys are checked.

In the meantime we would like to use this information. While the software that presents graphical data can produce short term datasets it doesn't seem to be working. The PHP requests crash everytime someone tries to capture this information. So what can we do? Capture the data ourselves by using OCR tools to extract the measurements. An interesting problem.

## Approach
Every ~15min grab the .png image, identify small regions where data we want is located in the image and store the values indexed by the timestamp.

## Some of the tools we need
`tesseract` is a tool that can pull data from an image. It is portable and can be installed on a RasperianOS driven device. (Our weather kiosk) we can store the data in a 36hr ring buffer.  This results in ~100 calls per day which is far from any deep burden on the servers delivering the data.  

## Platform
This will be deployed on a Raspberry Pi 3B running a stripped down RaspberrianOS. It runs a custom built kiosk like device that currently pulls publicly available NWS data for displaying current marined conditions close to our club.
