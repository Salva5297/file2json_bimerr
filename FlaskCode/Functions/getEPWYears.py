import json
from bs4 import BeautifulSoup
import requests
import urllib
import urllib.request
from urllib.request import Request,urlopen, urlretrieve
import time
import os
import re
from io import BytesIO
import zipfile
from pyepw.epw import EPW



def splitUrlName(url):
    name = url.split('/')
    name = name[-1]
    return name


def createEPWFile(urls):
    listYears = []
    for url in urls:
        req = Request(url, headers = {"User-Agent": "Mozilla/5.0"})
        resp = urlopen(req).read()
        data = resp.decode("utf-8", 'ignore')
        epw = EPW()

        name = splitUrlName(url)

        f = open('tmp/'+name,"a+")
        f.write("\n".join(data.splitlines()))
        f.close()

        epw.read('tmp/'+name)
        os.remove('tmp/'+name)

        [listYears.append(str(year._year)) for year in epw.weatherdata]
    listYears = list(dict.fromkeys(listYears))
    listYears.sort()
    return listYears



def createEPWFile2(listYears, data, name):
    epw = EPW()

    f = open('tmp/'+name,"a+")
    f.write("".join(data).replace('\r\n','\n'))
    f.close()

    epw.read('tmp/'+name)
    os.remove('tmp/'+name)

    [listYears.append(str(year._year)) for year in epw.weatherdata]
    listYears = list(dict.fromkeys(listYears))
    listYears.sort()
    return listYears


# EPW
def continentGetLink(continent):
    if continent == "Africa":
        continentLink = "/weather-region/africa_wmo_region_1"
    elif continent == "Asia":
        continentLink = "/weather-region/asia_wmo_region_2"
    elif continent == "South America":
        continentLink = "/weather-region/south_america_wmo_region_3"
    elif continent == "North and Central America":
        continentLink = "/weather-region/north_and_central_america_wmo_region_4"
    elif continent == "SouthwestPacific":
        continentLink = "/weather-region/southwest_pacific_wmo_region_5"
    elif continent == "Europe":
        continentLink = "/weather-region/europe_wmo_region_6"
    return continentLink


#EPW
def scrapeEP(city,country,continentLink):

    epwLinkList = []

    link = "https://energyplus.net"

    responseContinent = requests.get(link+continentLink,timeout=10)
    continent = BeautifulSoup(responseContinent.content, "html.parser")

    for countryLink in continent.find_all('a', attrs={"class": "btn btn-default left-justify blue-btn"}, href=True):
        countryName = countryLink.get_text()
        if country in countryName:
            countryName = countryLink['href']
            responseCountry = requests.get(link+countryName,timeout=10)
            countryData = BeautifulSoup(responseCountry.content, "html.parser")

            for cityLink in countryData.find_all('a', attrs={"class": "btn btn-default left-justify blue-btn"}, href=True):
                cityName = cityLink.get_text()
                if city in cityName:
                    cityName = cityLink['href']
                    responseCity = requests.get(link+cityName,timeout=10)
                    cityData = BeautifulSoup(responseCity.content, "html.parser")

                    for downloadLink in cityData.find_all('a', attrs={"class": "btn btn-default left-justify blue-btn"}, href=True):
                        if downloadLink.text == 'epw':
                            epwLinkList.append(link+downloadLink['href'])
    return epwLinkList


#OneBuilding
def continentLinker(continent):
    if continent == "Africa":
        continentLink = "/WMO_Region_1_Africa/"
    elif continent == "Asia":
        continentLink = "/WMO_Region_2_Asia/"
    elif continent == "South America":
        continentLink = "/WMO_Region_3_South_America/"
    elif continent == "North and Central America":
        continentLink = "/WMO_Region_4_North_and_Central_America/"
    elif continent == "SouthwestPacific":
        continentLink = "/WMO_Region_5_Southwest_Pacific/"
    elif continent == "Europe":
        continentLink = "/WMO_Region_6_Europe/"
    elif continent == "Antarctica":
        continentLink = "/WMO_Region_7_Antarctica/"
    return continentLink


#OneBuilding
def scrapeOB(city,country,continentLink):
    epwLinkList = []

    link = "http://climate.onebuilding.org"

    responseContinent = requests.get(link+continentLink,timeout=10)
    continentData = BeautifulSoup(responseContinent.content, "html.parser")

    for countryLink in continentData.find_all('a', attrs={"href":""}, href=True):
        countryName = countryLink.get_text()
        if country in countryName:
            countryName = countryLink['href']
            responseCountry = requests.get(link+continentLink+countryName,timeout=10)
            countryData = BeautifulSoup(responseCountry.content, "html.parser")

            for cityLink in countryData.find_all('a', attrs={"href":""}, href=True):
                cityName = cityLink.get_text()
                if city in cityName:
                    cityName = cityLink['href']
                    if cityName.endswith('.zip'):
                        epwLinkList.append(link+continentLink+countryName.replace('/index.html','/')+cityName)

    return epwLinkList



def extractEPWFile(url):

    resp = urlopen(url)
    zipfiles = zipfile.ZipFile(BytesIO(resp.read()))
    file = zipfiles.namelist()[2]

    epwFile = [file for file in zipfiles.namelist() if file.endswith('.epw')]

    file = epwFile[0]

    data = zipfiles.open(file).readlines() # Información perteneciente al archivo EPW
    data = [d.decode("utf-8") for d in data]

    name = url.split('/')[-1].replace('.zip','')

    zipfiles.close()

    return data, name


def jsonReaderYears(data):
    city = data["city"]
    country = data["country"]
    continent = data["continent"]
    source = data["source"]
    return city, country, continent, source


def mainGetEpwYears(json_info): # main
    city, country, continent, source = jsonReaderYears(json_info)
    
    if source == "EnergyPlus":
        continentLink = continentGetLink(continent)
        epwLinkList = scrapeEP(city,country,continentLink)
        listYears = createEPWFile(epwLinkList)
    
        return listYears
    
    elif source == "OneBuilding":
        continentLink = continentLinker(continent)
        epwLinkList = scrapeOB(city,country,continentLink)
        listYears = []
        for url in epwLinkList:
            data, name = extractEPWFile(url)
            listYears = createEPWFile2(listYears, data, name)
        return listYears


    