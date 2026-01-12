"""
General imports needed.
"""
# foundational libraries
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import pytz  # may need to migrate to ZoneInfo
import requests

# OCR tools
import pytesseract
# Bridge to cli tool. Need to install tesseract CLI engine in the OS

# Managing images
from PIL import Image

# Data management
import numpy as np
import pandas as pd


### Global Structures and Configurations
# Timezone configuration OLD SCHOOL
UTC = pytz.utc
# EST = pytz.timezone('US/Eastern')
# Timezone configuration NEW SCHOOL
# UTC = ZoneInfo.utc
EST = ZoneInfo('US/Eastern')

"""
    Quick review: NERACOOS weather buoys are managed by the Univ. of Ct. Bridgeport. They have invested, 
    heavily in a package (software and hardware) that provides real-time data on wind, waves and water 
    quality for LI Sound. We are most interested in two buoys which are close by to our harbor:
    Execution Rocks [exrx] and Western LI Sound [wlis]. The devices with their software can deliver csv lists
    of their systems but it would appear that the servers that present the data are not set up for this or
    not properly installed.  Since trying to access this infomation doesn't resolve to a permissions error
    or a no-authorized response but just a blunt php crash I am assuming the later.

    Our only option is to read the data from the .png graphical screens that are presented on their
    website. Fortunately this is pretty straightforward. In addition the data is only updated every 15 minutes
    for the Wind information and 20min for wave information.  Pulling data once every 10min seems like an
    easy lift.
"""

# Global defintion of no data.
NaN = float('nan')

# image URIs for Wind information
execrocksWind_url = "https://clydebank.dms.uconn.edu/exrx_wxSens2.png"  # Execution rocks
westernLIWind_url = "https://clydebank.dms.uconn.edu/wlis_wxSens1.png"  # Western Long Island

# dictionary of locations within the image of the data we want.
windSources = {
    'Timestamp':          {'bounds':(100,  64, 294,  78), 'value': NaN }, #dateString for reading
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

# image URIs for Wave information
westernLIWaves_url = "https://clydebank.dms.uconn.edu/wlis_wavs.png" 
execrocksWaves_url = "https://clydebank.dms.uconn.edu/exrx_wavs.png"

# dictionary of locations within the image of the data we want.
waveSources = {
    'Timestamp':         {'bounds':(100,  64, 294,  78), 'value': NaN },  #dateString for reading
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


class BuoyDataCapture:
    """
    Class to capture data from NERACOOS weather buoys. NERACOOS (long acronym: https://neracoos.org/), capture data from
    floating environmental stations up and down the coast. Mostly, it standardardizes the data storage and engineering of
    these stations. The data can be made available via an API but for the last 18 mos. it has only been available through
    a graphical display. As a consequence, this class uses OCR to read data from images and store the results in this object.
    This class works for both wind and wave data sections.  They have similar layouts. The water chemistry and bathymetry panels
    are quite different and might need a different class but we have what we need for our use case.
    :param sourceImageURL: URL of the image to fetch.
    :param dataExtraction: Dictionary defining regions to extract and store results.
    """

    # Source for image to decode
    sourceURL = ""
    # Placeholder for results
    dataParts = {}
    # temporary holder for downloaded image (maybe keep in memory?)
    filename  = "image.png"
    # Tesseract works best when limiting the characters to look for.
    ocrLimits = { # 0 decode for numbers
        'numberlike': r'--psm 6 -c tessedit_char_whitelist=-0123456789.',
                  # 1 decode for date
        'datelike':   r'--psm 6 -c tessedit_char_whitelist=-0123456789,:\ APMSunMonTueWedThuFriSatJanFebMarAprMayJunJulAugSepOctNovDecESTGMT',
    }

    def __init__(self, sourceImageURL, dataExtraction):
        """
        Initialize the class
        :param sourceImageURL: Where we get the original image. The last part of the path will be a valid .png file name.
        :param dataExtraction: The structure (see above) that delineates the bounds we are trying to capture along with a place to store the result.
        """
        self.sourceURL = sourceImageURL
        self.dataParts = dataExtraction
        self.filename = sourceImageURL.split("/")[-1]
        self.df = pd.DataFrame(keys=self.dataParts.keys())
        self.df.index.name = 'Timestamp'

    def fetch_image(self, filename=None):
        """
        retrieve the png and store to a file
        :param filename:  An optional name for the capture.
        """
        # 1. Retrieve the image  n.b. add a "?###" random number to sidestep local caching
        response = requests.get(self.sourceURL + f"?{np.random.randint(1000)}")

        # 2. Change the stored filename
        if filename != None:
            self.filename = filename
        
        # Check if the request was successful (HTTP 200)
        if response.status_code == 200:
            # 3. Store to disk for a second step, the image is not large, maybe keep in memory?
            with open(self.filename, "wb") as f:
                f.write(response.content)
            # return filename  # Return path to the stored file
        else:
            raise Exception(f"Failed to retrieve image. Status code: {response.status_code}")
    
    def _preprocess_for_ocr(self, croppedImage):
        """
        Improve the image for the OCR process. Mostly used in internally.
        :param croppedImage: an image object retrieved from the cropping process.
        :return: adapted image for OCR step
        """
        # 1. Convert to Grayscale ('L' mode in Pillow)
        gray_crop = croppedImage.convert('L')
        
        # 2. Resize: Tesseract needs clear, large characters. 
        # Upscaling by 2x or 3x often fixes issues with small regions.
        w, h = gray_crop.size
        upscaledImage = gray_crop.resize((w * 2, h * 2), Image.Resampling.LANCZOS)
        
        # 3. Optional: Invert if text is light on a dark background
        # Tesseract expects dark text on a light background.
        # upscaled = ImageOps.invert(upscaled) 
        return upscaledImage
    
    def ocr_numerals_only(self, image_crop, ocrCharacterLimit):
        """
        Processes a cropped image to extract only numbers and decimal points.
        :param image_crop: A single cropped image.
        :param ocrCharacterLimit: A set of characters to use when trying to decode the image
        :return: The value for the image.
        """
        # Configuration breakdown:
        # --psm 6: Assume a single uniform block of text (good for small crops)
        # tessedit_char_whitelist: Restrict characters to digits and dot
        
        # Perform OCR
        # text = pytesseract.image_to_string(image_crop, config=self.ocrLimits['numberLike'])
        # # Clean up whitespace/newlines
        # return float(text.strip())
        return self._ocr_values(image_crop, self.ocrLimits['numberlike'])

    def ocr_dates_only(self, image_crop):
        """
        Processes image crops to extract only numbers and decimal points.
        :param image_crops: List of PIL Image objects (from previous step).
        :return: List of extracted numeric strings.
        """
        print("\tDBG: DATES ONLY")
        # Configuration breakdown:
        # --psm 6: Assume a single uniform block of text (good for small crops)
        # tessedit_char_whitelist: Restrict characters to digits and dot
        
        # Perform OCR
        # text = pytesseract.image_to_string(image_crop, config=self.ocrLimits['dateLike'])
        # Clean up whitespace/newlines
        # return text.strip()
        return self._ocr_values(image_crop, self.ocrLimits['datelike'])

    def _ocr_values(self, image_crop, ocrCharacterLimit):
        """
        Processes a cropped image to extract only numbers and decimal points.
        :param image_crop: A single cropped image.
        :param ocrCharacterLimit: A set of characters to use when trying to decode the image
        :return: The value for the image.
        """
        # Perform OCR
        text = pytesseract.image_to_string(image_crop, config=ocrCharacterLimit)
        # Clean up whitespace/newlines
        return text.strip()        
        
    def extract_regions(self):
        """
        Extracts multiple rectangular regions from a PNG.  Again, we store the result 
        on disk but maybe we can get away with keeping in memory?
        :param image_path: Path to the retrieved PNG file.
        :param regions: List of 4-tuples (left, upper, right, lower) coordinates.
        :return: List of cropped Image objects.
        """
        # extracted_images = []
        
        with Image.open(self.filename) as img:
            # Standardize for OCR: convert to RGB and remove transparency
            img = img.convert("RGB") 

            for key, item in self.dataParts.items():
                print(f"\tWRK: {key}: {item['bounds']} {key.find("Time")}")
                croppedImage = self._preprocess_for_ocr(img.crop(item['bounds']))

                if key.find("Time")>-1:
                    # Decoding the date can be tricky. Though the buoys are connected via cell their clocks can be wildly off.
                    data = self._ocr_values(croppedImage, self.ocrLimits['datelike']) + f", {datetime.now().year}"
                    print(f"\t\tDBG: time string [raw]: {repr(data)}")
                    try:
                        data = datetime.strptime(data, "%I:%M:%S %p %Z, %a %b %d, %Y")  # even though it captures the EST it is naive
                    except:
                        data = datetime.strptime(data, "%I:%M:%S %p %Z, %b %d, %Y")  # even though it captures the EST it is naive

                    tz = pytz.timezone('US/Eastern')
                    data = data.replace(tzinfo=tz)
                    item['value'] = data
                    #ATTN: When testing this on Jan 02, 2026 the buoy's clock was 2hrs fast. This may be corrected later.
                    if datetime.now(pytz.timezone('US/Eastern')) < data:
                        # The buoy reports the wrong time every now and again probably 2 hours off. 1/7/26 Seems to have been fixed.
                        print("\t\tDBG: Fixed time")
                        data = data - timedelta(hours=2)
                    else:
                        print("\t\tDBG: Time is OK")
                        data = data
                else:
                    try:
                        data = self._ocr_values(croppedImage, self.ocrLimits['numberlike'])
                        data = float(data)
                    except:
                        data = np.nan
                item['value'] = data

    def getDict(self):
        dataDict = {}
        for k in self.dataParts:
            dataDict[k] = self[k]
        return dataDict
    
    def __getitem__(self, key):
        return self.get(key)
    
    def get(self, key):
        return self.dataParts[key]['value']

class DataBuffer:
    """
    This class manages a ring buffer of data stored in a CSV file. The buffer retains data for the last 3 days (72 hours) only.
    It uses pandas DataFrame for efficient data handling and storage. As with the OCR class above, this class is agnostic toward
    the type of data being stored. It could be data from wind or wave panels. The user specifies the column labels and the class manages
    the rest. 
    :param labels: List of strings for the column names. (usually just: `list[waveSources.keys()]` or `list[windSources.keys()]`)
    :param filepath: Path to the CSV file.
    """
    def __init__(self, labels, filepath="sensor_data.csv"):
        """
        :param labels: List of strings for the column names.
        :param filepath: Path to the CSV file.
        """
        self.filepath = filepath
        self.columns = labels

        if os.path.exists(self.filepath):
            # Load existing data and ensure the index is parsed as datetime
            self.df = pd.read_csv(self.filepath, index_col=0, parse_dates=True)
            # Ensure index is timezone-aware (UTC) to match new records
            if self.df.index.tz is None:
                self.df.index = self.df.index.tz_localize(timezone.utc)
            # Ensure existing columns match the provided labels
            self.df.columns = self.columns
        else:
            # Initialize empty DataFrame with custom labels and UTC timezone awareness
            #    - 'data=[]' ensures it is empty
            #    - 'tz="US/Eastern"' sets the timezone (you can use 'UTC', 'Asia/Tokyo', etc.)
            tz_aware_index = pd.DatetimeIndex([], dtype='datetime64[ns, US/Eastern]', name='Timestamp')
            df = pd.DataFrame(columns=self.columns, index=tz_aware_index)

    def add_record(self, data_dict):
        """
        Appends a dictionary to the dataframe in one step.
        :param data_dict: Dictionary where keys match self.columns.
        """
        # 1. Create a timezone-aware timestamp for the current moment
        now = datetime.now(timezone.utc)
        
        # 2. Single-step append: loc automatically maps dictionary keys to columns
        self.df.loc[now] = data_dict
        
        # 3. Maintain the 3-day ring buffer and save
        self._truncate_and_save()

    def _truncate_and_save(self):
        """Truncates data older than 3 days and saves to CSV to persist through reboots."""
        cutoff_time = datetime.now(EST) - timedelta(days=3)
        # Keep only records from the last 72 hours
        self.df = self.df[self.df.index >= cutoff_time]
        self.df.to_csv(self.filepath)

    def get_data(self):
        """Access the dataframe for graphing or analysis."""
        return self.df


def main():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    print("----------------------------------------")
    print("--- Execution Rocks Weather Data Read:")
    obj = WeatherDataRead(execrocksWind_url, windSources)
    obj.fetch_image()
    obj.extract_regions()

    print(f"time: {obj['Timestamp'].strftime('%Y-%m-%d %I:%M:%S %P %Z')} @{obj['Timestamp']}  ")

    if datetime.now(pytz.timezone('US/Eastern')) < obj['Timestamp']:
        print("Why is the time wrong?")

    print(obj.getDict())

    print("----------------------------------------")
    print("--- Execution Rocks Wave Data Read:")
    obj = WeatherDataRead(execrocksWaves_url, waveSources)
    obj.fetch_image()
    obj.extract_regions()

    print(f"time: {obj['Timestamp'].strftime('%Y-%m-%d %I:%M:%S %P')} @{obj['Timestamp']}  ")

    print(obj.getDict())

    ## Now we want to store this data in a CSV file or a database.
    # TBD


if __name__ == "__main__":
    main()

