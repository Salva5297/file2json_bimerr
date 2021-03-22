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
from Functions.getEPWYears import continentGetLink, scrapeEP, continentLinker, scrapeOB, extractEPWFile, splitUrlName


def jsonReader(data):
    city = data["city"]
    country = data["country"]
    continent = data["continent"]
    year = data["year"]
    source = data["source"]
    return city, country, continent, year, source



def createEPWFile(urls, year):
    listYears = []
    listLinks = []
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

        if str(year) in listYears:
            listLinks.append(url)

    listYears = list(dict.fromkeys(listYears))
    listYears.sort()
    return listYears, listLinks



def createEPWFile2(listYears, data, name, listLinks):
    epw = EPW()

    f = open('tmp/'+name,"a+")
    f.write("".join(data).replace('\r\n','\n'))
    f.close()

    epw.read('tmp/'+name)
    os.remove('tmp/'+name)

    [listYears.append(year._year) for year in epw.weatherdata]
    listYears = list(dict.fromkeys(listYears))
    listYears.sort()
    return listYears, listLinks


def execute(data):

    city, country, continent, year, source = jsonReader(data)

    if source == "EnergyPlus":
        continentLink = continentGetLink(continent)

        epwLinkList = scrapeEP(city,country,continentLink)

        listYears, listLinks = createEPWFile(epwLinkList, year)


        if listLinks != []:
            return listLinks
        else:
            return listYears


    elif source == "OneBuilding":
        continentLink = continentLinker(continent)
        epwLinkList = scrapeOB(city,country,continentLink)

        listYears = []
        listLinks = []
        for url in epwLinkList:
            data,name = extractEPWFile(url)
            listYears, listLinks = createEPWFile2(listYears, data, name, listLinks)
            if year in listYears:
                listLinks.append(url)
        
        

        if listLinks != []:
            return listLinks
        else:
            return listYears

def mainDownloadEPW(data):
        resultList = execute(data)
        if str(resultList[0]).startswith("http"):
            resultList = ','.join(resultList)
            dictionary = {
                'info': 'The links of the epw files that you have requested are as follows:',
                'links': resultList
            }
            return dictionary

        else:
            newResultList = []
            [newResultList.append(str(year)) for year in resultList]
            resultList = ','.join(newResultList)
            dictionary = {
                'info': 'Your year does not coincide with any of the years established within the epw files, please select one of the following',
                'years': resultList
            }

            return dictionary