# OCRWeather

This is a tool designed to collect wind and wave information from a publicly available and displayed weather buoy. It is located within 2 nm of our sailing club and all I seek to do is to proved realtime and some historical data (24hrs). Once upon a time the buoys were funded (and still are) by NOAA and the NWS but run by the University of Ct, Bridgeport. For a while, the NWS carried and cataloged the data from these buoys and an app I wrote for display at our club relied on this public database. At some point NERACOOS buoys were updated and the NWS, though listing these resources, no longer adds to their database. I suspect that these devices have to go through a vetting period and it will be a while as the reliability and accuracy of these buoys are checked.

In the meantime we would like to use this information. While the software that presents graphical data can produce short term datasets it doesn't seem to be working. The PHP requests crash everytime someone tries to capture this information. So what can we do? Capture the data ourselves by using OCR tools to extract the measurements. An interesting problem.

## Approach

 > Every ~15min grab the wind.png image, identify small regions where data we want is located in the image and store the values indexed by the timestamp.
```python
NaN = float('nan')
windSources = {
    'WindSpeedAvg [kts]': {'bounds':( 21, 307,  63, 327), 'value': NaN,}, #kts
    'WindSpeedGst [kts]': {'bounds':(116, 307, 158, 327), 'value': NaN }, #kts
    'WindSpeedAvg [mph]': {'bounds':( 21, 334,  63, 351), 'value': NaN }, #mph
    'WindSpeedGst [mph]': {'bounds':(116, 334, 158, 351), 'value': NaN }, #mph
    'WindSpeedAvg [m/s]': {'bounds':(21, 358, 63, 375),   'value': NaN }, #m/s
    'WindSpeedGst [m/s]': {'bounds':(116, 358, 158, 375), 'value': NaN }, #m/s
    'WindDir [°]':        {'bounds':(230, 320, 287, 339), 'value': NaN }, #deg True
    'AirTemp [°F]':       {'bounds':(410, 169, 471, 188), 'value': NaN }, #degFarenheit
    'AirTemp [°C]':       {'bounds':(409, 221, 471, 238), 'value': NaN }, #degCentegrade
    'BaromPres [mmHg]':   {'bounds':(391, 415, 449, 434), 'value': NaN }, #barm in mmHg
    'BaromPres [mB]':     {'bounds':(467, 415, 537, 434), 'value': NaN }, #barm in mBar
    'DewPoint [°F]':      {'bounds':(505, 322, 552, 341), 'value': NaN }, #dewpoint degFarenheit
    'DewPoint [°C]':      {'bounds':(563, 322, 605, 341), 'value': NaN }, #dewPoint degCentegrade
    'RelHum [%]':         {'bounds':(391, 323, 448, 341), 'value': NaN }, #rel. humidity
    'WindTimestamp':      {'bounds':(100,  64, 294,  78), 'value': NaN }, #dateString for reading
    'WindSpeedM24 [kt]':  {'bounds':(112, 412, 150, 435), 'value': NaN }, #kts max in last 24hrs
    'WindDirM24 [°]':     {'bounds':(271, 412, 300, 433), 'value': NaN }, #deg True in last 24hrs
    'WindTimeM24':        {'bounds':(114, 433, 299, 454), 'value': NaN }, #dateString of 24Hr Max
}
WindDataDF = pd.DataFrame(columns=[windSources.keys()])
```

 > Every ~30min grab the wave.png image, the regions are already defined for the pieces of the 
```python
waveSources = {
    'WaveHgtSig [ft]':    {'bounds':( 68, 329, 112, 346), 'value': NaN,}, #ft
    'WaveHgtMax [ft]':    {'bounds':(168, 329, 212, 346), 'value': NaN }, #ft
    'WaveHgtSig [m]':     {'bounds':( 68, 353, 112, 371), 'value': NaN,}, #m
    'WaveHgtMax [m]':     {'bounds':(168, 353, 212, 371), 'value': NaN }, #m
    'WaveDir [°]':        {'bounds':(292, 322, 347, 340), 'value': NaN }, #degT
    'WavPerAvg [s]':      {'bounds':(479, 193, 539, 211), 'value': NaN }, #sec
    'WavPerDom [s]':      {'bounds':(479, 251, 539, 269), 'value': NaN }, #sec
    'WaveTimestamp':      {'bounds':(100,  64, 294,  78), 'value': NaN }, #dateString for reading
    'WaveHgt24 [ft]':     {'bounds':(169, 413, 207, 433), 'value': NaN }, #kts max in last 24hrs
    'WaveDirM24 [°]':     {'bounds':(327, 412, 354, 433), 'value': NaN }, #deg True in last 24hrs
    'WavePerAvgM24 [s]':  {'bounds':(169, 442, 207, 433), 'value': NaN }, #deg True in last 24hrs
    'WaveperDomM24 [s]':  {'bounds':(542, 442, 574, 433), 'value': NaN }, #deg True in last 24hrs
    'WaveTimeM24':        {'bounds':(169, 433, 363, 455), 'value': NaN }, #dateString of 24Hr Max  
}
WaveDataDF = pd.DataFrame(columns=[waveSources.keys()])
```

## Some of the tools we need

`tesseract` is a tool that can pull data from an image. It is portable and can be installed on a RasperianOS driven device. (Our weather kiosk) we can store the data in a 36hr ring buffer.  This results in ~100 calls per day which is far from any deep burden on the servers delivering the data.

## Platform

This will be deployed on a Raspberry Pi 3B running a stripped down RaspberrianOS. It runs a custom built kiosk like device that currently pulls publicly available NWS data for displaying current marined conditions close to our club.

## Storage Strategy

### Phase 1

- Marked by lack of datastorage files.
- 2 Seperate datastorage files: wind and waves

Deal with the initial case.  Set up the `DF` and write it out.

### Phase 2

- Marked by existance of datafiles.
- Read datafiles

Gather data, populate the `DF` and write it out.
