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

#supported contains a list of supported websites by youtube-dl
    
    
parser = argparse.ArgumentParser(description='Download TV-series.', epilog="If you don't provide an episode this program will try to download the provided season. If you don't provide a season it will try to download all seasons.")
parser.add_argument("name", help="name of the series you want to download", nargs=1)
parser.add_argument("-s", metavar="season", dest="season", help="the number of the season you want to download", type=int, nargs=1, required=False)
parser.add_argument("-e", metavar="episode", dest="episode", help="the number of the episode you want to download", type=int, nargs=1, required=False)

opts = vars(parser.parse_args()) #convert arguments from name space to dictionary
seriesLowerName = opts["name"][0].lower()
seriesAdressName = seriesLowerName.replace(" ", "_")

def getUrl(url):
    """This just gets and returns the contents of a provided web page."""
    response = urllib2.urlopen(url)
    return response.read()

def getEpisodeList():
    """Returns a list of episodes and the links to their linkpage on watchseries.
    The name of the series is taken from the provided options directly."""

    episodeListPage = getUrl("http://watchtvseries.to/serie/" + seriesAdressName + "/sab")
    result = re.findall('content="(/episode/(.+)_s([0-9]+)_e([0-9]+).html)', episodeListPage)
    """I'm using re.findall throughout this script because I didn't fully
    understood how to access match objects right. Its okay here though because
    I actually need the links to all of the mirrors."""

    episodeList = {}
    for entry in result:
        try:
            episodeList[int(entry[2])].append(entry[0])
        except:
            episodeList[int(entry[2])] = []
            episodeList[int(entry[2])].append(entry[0])
    return episodeList #episodeList()[season][episode links]

def getEpisode(url):
    """Downloads an episode. Needs the url to the episodes page on watchseries."""
    try:
        linkpage = getUrl(url)
        result = re.findall('<span itemprop="name">([^<]+)</span></a> - <span class="list-top"><a href="/season-[0-9]+/[^"]+">Season ([0-9]+)</a> Episode ([0-9]+) - ([^<]+)</span>', linkpage)
        series = result[0][0]
        season = int(result[0][1])
        episode = int(result[0][2])
        title = result[0][3]
        #Yeah. This would be more elegant with re.search or re.match.
        
        filename = series + " - S" + "%02d" % (season,) + "xE" + "%02d" % (episode,) + " - " + title 
            
        result = re.findall('href="(/[^"]+)" class="buttonlink" title="([^.]+)[^"]+"', linkpage)
        #Same here.
        
        random.shuffle(result)
        #I'm randomly shuffling the mirror links so that all mirrors get evenly burdened.
    except:
        return None
    
    for entry in result:
        if entry[1] in supported:   #if the mirror is supported by youtube-dl
            button = re.findall('href="([^"]+)" class="push_button blue"', getUrl("http://watchtvseries.to" + entry[0]))
            ydl = youtube_dl.YoutubeDL({'outtmpl': filename + '.%(ext)s'}) #the filename. This could become changable in the future.
            ydl.add_default_info_extractors()
            """boy this is some ugly programming. If youtube-dl doesn't raise any exceptions
            I assume the file downloaded succesfully and the loop breaks.
            If there was an exception raised we don't reach the break and
            continue with the next random mirror.
            Would be clever if we stopped the whole thing if there was a
            connectivity problem for instance."""
            try:
                ydl.download(button)
                break
            except:
                continue

    return button

def somethingWentWrong():
    """This obscure method does errorhandling. I know I should better create
    tailored exceptions for this but I am new at python so for the time being
    this must suffice."""
    if seriesLowerName[0].upper() in string.uppercase[:26]: #this checks if the first character is a letter. I bet there is a better way to do that.
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
            if difflib.SequenceMatcher(None, candidate, seriesLowerName).ratio() >= 0.7:    #If there are names with more than 70 percent similarity to what the user provided, they get suggested.
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
    #Yeah every exceptions goes here. Not good.
    somethingWentWrong()
