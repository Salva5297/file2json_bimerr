import sys
import os
import codecs
import json

from pyepw.epw import EPW
import pycountry



def encodeToUTF(file):
    BLOCKSIZE = 1048576 # or some other, desired size in bytes

    second = file.split('/')
    second.pop()
    second = "/".join(second)
    second += "/example.epw"

    with codecs.open(file, "r", "ISO-8859-1") as sourceFile:
        with codecs.open(second, "w", "utf-8") as targetFile:
            while True:
                contents = sourceFile.read(BLOCKSIZE)
                if not contents:
                    break
                targetFile.write(contents.replace('ISO-8859-1','utf-8'))

    os.rename(second,file)



def getCountryName(code):
    country = pycountry.countries.get(alpha_3=code)
    country_name = country.name
    return country_name



def chunkIt(seq, num):
    avg = len(seq) / float(num)
    out = []
    last = 0.0

    while last < len(seq):
        out.append(seq[int(last):int(last + avg)])
        last += avg

    return out



def createJsonFile(epw, epwName):
    json_file = {}

    country = getCountryName(epw.location._country)

    json_file['location'] = {
        "city" : epw.location._city,
        "country" : country,
        "adm03" : epw.location._country,
        "wmo" : int(epw.location._wmo),
        "lat" : float(epw.location._latitude),
        "long" : float(epw.location._longitude),
        "alt" : float(epw.location._elevation),
        "epwName" : epwName
    }


    json_file['typical_extremePeriods'] = []
    [json_file['typical_extremePeriods'].append({
        "typeOfPeriod" : str(period).split(',')[2],
        "firstDate" : str(period).split(',')[3].replace(" ",""),
        "lastDate" : str(period).split(',')[4].replace(" ",""),
        "season" : str(period).split(',')[1].split('-')[0].replace(" ",""),
        "city" : epw.location._city,
        "adm03" : epw.location._country,
        "wmo" : int(epw.location._wmo),
        "epwName" : epwName
    }) for period in epw.typical_or_extreme_periods._typical_or_extreme_periods]

    resInt = len(str(epw.ground_temperatures).split(",")[2:])/16


    temps = chunkIt(str(epw.ground_temperatures).split(",")[2:],resInt)

    json_file['groundTemperatures'] = [] 
    [json_file['groundTemperatures'].append({
        "groundTemperatureDepth" : elem[0],
        "groundConductivity" : elem[1],
        "groundDensity" : elem[2],
        "groundSpecificHeat" : elem[3],
        "january" : elem[4],
        "february" : elem[5],
        "march" : elem[6],
        "april" : elem[7],
        "may" : elem[8],
        "june" : elem[9],
        "july" : elem[10],
        "august" : elem[11],
        "september" : elem[12],
        "october" : elem[13],
        "november" : elem[14],
        "december" : elem[15],
        "city" : epw.location._city,
        "adm03" : epw.location._country,
        "wmo" : int(epw.location._wmo),
        "epwName" : epwName
    }) for elem in temps]

    json_file['epw'] = []
    [json_file['epw'].append({
        "Year": data._year,
        "Month": data._month,
        "Day": data._day,
        "Hour": data._hour,
        "DryBulbTemperature": data._dry_bulb_temperature,
        "DewPointTemperature": data._dew_point_temperature,
        "RelativeHumidity": data._relative_humidity,
        "AtmosphericStationPressure": data._atmospheric_station_pressure,
        "ExtraterrestrialHorizontalRadiation": data._extraterrestrial_horizontal_radiation,
        "ExtraterrestrialDirectNormalRadiation": data._extraterrestrial_direct_normal_radiation,
        "HorizontalInfraredRadiationIntensity": data._horizontal_infrared_radiation_intensity,
        "GlobalHorizontalRadiation": data._global_horizontal_radiation,
        "DirectNormalRadiation": data._direct_normal_radiation,
        "DiffuseHorizontalRadiation": data._diffuse_horizontal_radiation,
        "GlobalHorizontalIlluminance": data._global_horizontal_illuminance,
        "DirectNormalIlluminance": data._direct_normal_illuminance,
        "DiffuseHorizontalIlluminance": data._diffuse_horizontal_illuminance,
        "ZenithLuminance": data._zenith_luminance,
        "WindDirection": data._wind_direction,
        "WindSpeed": data._wind_speed,
        "TotalSkyCover": data._total_sky_cover,
        "OpaqueSkyCover": data._opaque_sky_cover,
        "Visibility": data._visibility,
        "CeilingHeight": data._ceiling_height,
        "PrecipitableWater": data._precipitable_water,
        "AerosolOpticalDepth": data._aerosol_optical_depth,
        "SnowDepth": data._snow_depth,
        "DaysSinceLastSnowfall": data._days_since_last_snowfall,
        "Albedo": data._albedo,
        "LiquidPrecipitationDepth": data._liquid_precipitation_depth,
        "LiquidPrecipitationQuantity": data._liquid_precipitation_quantity,
        "city" : epw.location._city,
        "adm03" : epw.location._country,
        "wmo" : int(epw.location._wmo),
        "epwName" : epwName 
    }) for data in epw.weatherdata]



    return json_file


def mainEPW(file):

    epw = EPW()

    epwName = os.path.splitext(file)[0]

    encodeToUTF(file)

    epw.read(file)

    json_file = createJsonFile(epw, epwName)

    return json_file