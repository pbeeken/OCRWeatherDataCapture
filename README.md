# OCRWeather

This is a tool designed to collect wind and wave information from a publicly available and displayed weather buoy. It is located within 2 nm of our sailing club and all I seek to do is to proved realtime and some historical data (24hrs). Once upon a time the buoys were funded (and still are) by NOAA and the NWS but run by the University of Ct, Bridgeport. For a while, the NWS carried and cataloged the data from these buoys and an app I wrote for display at our club relied on this public database. At some point NERACOOS buoys were updated and the NWS, though listing these resources, no longer adds to their database. I suspect that these devices have to go through a vetting period and it will be a while as the reliability and accuracy of these buoys are checked.

In the meantime we would like to use this information. While the software that presents graphical data can produce short term datasets it doesn't seem to be working. The PHP requests crash everytime someone tries to capture this information. So what can we do? Capture the data ourselves by using OCR tools to extract the measurements. An interesting problem.

## Approach

 > Every ~15min grab the wind.png image, identify small regions where data we want is located in the image and store the values indexed by the timestamp.
```python
NaN = float('nan')
windSources = {
    'Timestamp':          {'bounds':(100,  64, 294,  78), 'value': NaN }, #dateString for reading  SHOULD BE FIRST
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
    'WindSpeedM24 [kt]':  {'bounds':(112, 412, 150, 435), 'value': NaN }, #kts max in last 24hrs
    'WindDirM24 [°]':     {'bounds':(271, 412, 300, 433), 'value': NaN }, #deg True in last 24hrs
    'WindTimeM24':        {'bounds':(114, 433, 299, 454), 'value': NaN }, #dateString of 24Hr Max
}
WindDataDF = pd.DataFrame(columns=[windSources.keys()])
```

 > Every ~30min grab the wave.png image, the regions are already defined for the pieces of the 
```python
waveSources = {
    'Timestamp':          {'bounds':(100,  64, 294,  78), 'value': NaN }, #dateString for reading  SHOULD BE FIRST
    'WaveHgtSig [ft]':    {'bounds':( 68, 329, 112, 346), 'value': NaN,}, #ft
    'WaveHgtMax [ft]':    {'bounds':(168, 329, 212, 346), 'value': NaN }, #ft
    'WaveHgtSig [m]':     {'bounds':( 68, 353, 112, 371), 'value': NaN,}, #m
    'WaveHgtMax [m]':     {'bounds':(168, 353, 212, 371), 'value': NaN }, #m
    'WaveDir [°]':        {'bounds':(292, 322, 347, 340), 'value': NaN }, #degT
    'WavPerAvg [s]':      {'bounds':(479, 193, 539, 211), 'value': NaN }, #sec
    'WavPerDom [s]':      {'bounds':(479, 251, 539, 269), 'value': NaN }, #sec
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

### Phase 3

- setup RaspPi and update libraries
- test execution on the pi (fix any machine dependancies)
- build cron job parameters.  
  > To fire an event at regular intervals it can be done with a /10 
  > (for minute intervals in an hour i.e. 10,20,30...). To start and a
  > point other than :00 then use this 7-59/15 which would trigger at 
  > 7 min past the hour > at :07, :22, :37, :52

  > Some systems don't support the /delta so you can specify the time **RASP-Pi DOES**
  > in a comma separated list: 07,22,37,52 in the minute slot.
```
# Actual Cron records
# restart a few minutes can "blow it's nose."
10 15 * * *           /bin/bash /home/pi/WeatherKiosk/bin/restartMachine.sh
# Capture new wind and wave data
4-59/15 * * * *       /bin/bash /home/pi/collectWeatherData.sh -z  # Wind
8-59/20 * * * *       /bin/bash /home/pi/collectWeatherData.sh -w  # Waves
```

### Phase 4
  - Replace the wind graphic with one generated from the captured data. 
    > Consider reducing the size of the tide graph (decrease it's overall height by 25%)

    > Create a new wind/wave chart and maybe a cool graphic with a compass rose indicating
    > the magnitude of the wind direction and strength superimposed on the same for the wave
    > direction and strength.

    > Consider marking the source in the data recording and include central LIS as well as
    > as backup capture western LIS  [EXC, WLI, CLI] and switch between based on failure tree:
    > default: EXC : if fail: WLI : if fail: CLI : giveup. or return to Sands Point (different graphic)

### Phase 5
   > Odd Bug.  Every 6 hours or so the OCR glitches when reading wind data. So far I haven't seen this
   > with the wave data. I wonder if it is the graphic itself that is being posted incorrectly?  One way 
   > to debug this is to save the .png file right after it is downloaded. Th pi doesn't have the reserve
   > storage so I'll pull it to here from the pi.
   > I use the systemd service to run a script, `capturePNG.sh`, to grab the file a few minutes after it
   > is downloaded to a local folder: `/home/pbeeken/Documents/Jupyter/OCRWeatherImage/pngDebug` 

#### How to do this

- create `capturePNG.sh`, `pull-remote-png.service`, and `pull-remote-png.timer`
- out the `.service` and `.timer` files into `/etc/systemd/system/`
- Enable and Start... Run these commands to activate your new schedule: 

>> Reload systemd to recognize the new files:
`sudo systemctl daemon-reload`
>> Enable the timer so it starts on boot:
`sudo systemctl enable pull-remote-file.timer`
>> Start the timer immediately:
`sudo systemctl start pull-remote-file.timer`
>> How to Check It's Working

- List all active timers: Use `systemctl list-timers` to see when your script is scheduled to run next.
- Check logs: Use `journalctl -u pull-remote-file.service` to see the exact output and any errors from your script.
- **Found it.**  The issue is with the graphic. <font color="red">🅝</font> is posted for all values but gusts. The screen was captured almost right away. Now if I am wondering if I could detect this would a second attempt at a download fix the problem?  The rising/falling area shows the string "Error" vs "Rising" or "Falling"
- For now we will filter out all the NaN from the pandas array when graphing.  

---

## Develop the graphic panel

