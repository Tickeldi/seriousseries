#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

'''
Created on 27.08.2014

@author: ole
'''

import youtube_dl
import argparse
import urllib2
import re
import random
import string
import difflib

supported = list()

for extractor in youtube_dl.gen_extractors():
    name = extractor.IE_NAME
    supported.append(name.lower())
    
    
parser = argparse.ArgumentParser(description='Download TV-series.', epilog="If you don't provide an episode this program will try to download the provided season. If you don't provide a season it will try to download all seasons.")
parser.add_argument("name", help="name of the series you want to download", nargs=1)
parser.add_argument("-s", metavar="season", dest="season", help="the number of the season you want to download", type=int, nargs=1, required=False)
parser.add_argument("-e", metavar="episode", dest="episode", help="the number of the episode you want to download", type=int, nargs=1, required=False)

opts = vars(parser.parse_args()) #convert arguments from name space to dictionary
seriesLowerName = opts["name"][0].lower()
seriesAdressName = seriesLowerName.replace(" ", "_")

def getUrl(url):
    response = urllib2.urlopen(url)
    return response.read()

def getEpisodeList():
    episodeListPage = getUrl("http://watchtvseries.to/serie/" + seriesAdressName + "/sab")
    result = re.findall('content="(/episode/(.+)_s([0-9]+)_e([0-9]+).html)', episodeListPage)
    episodeList = {}
    for entry in result:
        try:
            episodeList[int(entry[2])].append(entry[0])
        except:
            episodeList[int(entry[2])] = []
            episodeList[int(entry[2])].append(entry[0])
    return episodeList #episodeList()[season][episode links]

def getEpisode(url):
    try:
        linkpage = getUrl(url)
        result = re.findall('<span itemprop="name">([^<]+)</span></a> - <span class="list-top"><a href="/season-[0-9]+/[^"]+">Season ([0-9]+)</a> Episode ([0-9]+) - ([^<]+)</span>', linkpage)
        series = result[0][0]
        season = int(result[0][1])
        episode = int(result[0][2])
        title = result[0][3]
        
        filename = series + " - S" + "%02d" % (season,) + "xE" + "%02d" % (episode,) + " - " + title 
            
        result = re.findall('href="(/[^"]+)" class="buttonlink" title="([^.]+)[^"]+"', linkpage)
        
        random.shuffle(result)
    except:
        return None
    
    for entry in result:
        if entry[1] in supported:
            button = re.findall('href="([^"]+)" class="push_button blue"', getUrl("http://watchtvseries.to" + entry[0]))
            ydl = youtube_dl.YoutubeDL({'outtmpl': filename + '.%(ext)s'})
            ydl.add_default_info_extractors()
            try:
                ydl.download(button)
                break
            except:
                continue

    return button

def somethingWentWrong():
    if seriesLowerName[0].upper() in string.uppercase[:26]:
        result = re.findall('>([^<]+)<span class="epnum">', getUrl("http://watchtvseries.to/letters/" + seriesLowerName[0].upper()))
    else:
        result = re.findall('>([^<]+)<span class="epnum">', "http://watchtvseries.to/letters/09")

    serieslist = []
    for entry in result:
        serieslist.append(entry.lower())
    if seriesLowerName not in serieslist:
        print("Sorry. I can't find a series with the name you provided. (" + opts["name"][0] + ")")
        candidateList = list()
        for candidate in serieslist:
            if difflib.SequenceMatcher(None, candidate, seriesLowerName).ratio() >= 0.7:
                candidateList.append(candidate)
        if candidateList.__len__() > 0:
            print("Did you mean ")
            for candidate in candidateList:
                print(candidate)
            print("?")
        quit()
    else:
        print("There is a series with the name you provided, but something else went wrong. Maybe the episode or season you chose doesn't exist.")
        quit()
    
    
try:
    if opts["season"]:
        if opts["episode"]:
            getEpisode("http://watchtvseries.to/episode/" + seriesAdressName + "_s" + str(opts["season"][0]) + "_e" + str(opts["episode"][0]) + ".html")
        else:
            for link in getEpisodeList()[opts["season"][0]]:
                getEpisode("http://watchtvseries.to" + link)
    else:
        episodeList = getEpisodeList()
        for season in episodeList:
            for link in episodeList[season]:
                getEpisode("http://watchtvseries.to" + link)
except:
    somethingWentWrong()
