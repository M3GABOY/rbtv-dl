#!/usr/bin/python3
import requests
import json
import argparse
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
import os
from io import StringIO
from bs4 import BeautifulSoup

token_url = "https://api.redbull.tv/v3/session?os_family=http"
live_video_url= "https://dms.redbull.tv/v3/"

downloader=requests.session()
header={
    'accept': '*/*',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'en-US,en;q=0.9',
    'cache-control': 'no-cache',
    'dnt': '1',
    'origin': 'https://www.redbull.com',
    'pragma': 'no-cache',
    'referer': 'https://www.redbull.com/',
    'sec-ch-ua': '"Google Chrome";v="89", "Chromium";v="89", ";Not A Brand";v="99"',
    'sec-ch-ua-mobile': '?0',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'cross-site',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.128 Safari/537.36'
}

outpath=""
type=""
mark=36

parser = argparse.ArgumentParser()
parser.add_argument("url", help="URL of Video Page", type=str)
parser.add_argument("-o", "--output", default='./',dest="output", help="Set Output Location", action="store")
args=parser.parse_args()
outpath=args.output
link=args.url
if(link[len(link)-1] == '/'):
    link=link[:-1]

downloader.headers.update(header)

webpage=downloader.get(link, verify=False)
soup = BeautifulSoup(webpage.text,features="html.parser")
title=soup.find("title").string
invalid = '<>:"/\|?*'
for char in invalid:
    title = title.replace(char,'-')

page=downloader.get(token_url, verify=False)
response=json.load(StringIO(page.text))
token=response["token"]
locale_string=link[23:31]
locale_check_validity=locale_string[0]+locale_string[len(locale_string)-1]
locale=link[24:30]
if(locale_check_validity == "//"):
    locale=(locale[4:6]+'-'+locale[0:3].upper())
    leftstrLoc=31
    rightstrLoc=36
else:
    locale=link[24:29]
    locale=(locale[3:5]+'-'+locale[0:2].upper())
    locale_string=link[23:30]
    leftstrLoc=30
    rightstrLoc=35
identifier=link[leftstrLoc:rightstrLoc]
if(identifier == "live/"):
        type="live-videos"
else:
    mark=rightstrLoc+2
    identifier=link[leftstrLoc:rightstrLoc+2]
    if(identifier == "videos/"):
        type="videos"
    else:
        mark=rightstrLoc+4
        identifier=link[leftstrLoc:rightstrLoc+4]
        if(identifier == "episodes/"):
            type="episode-videos"
        else:
            mark=rightstrLoc+1
            identifier=link[leftstrLoc:rightstrLoc+1]
            if(identifier == "films/"):
                type="films"
            else:
                mark=rightstrLoc+1
                identifier=link[leftstrLoc:rightstrLoc+1]
                if(identifier == "shows/"):
                    type="shows"

title_url=link[mark:len(link)]
get_video_url="https://www.redbull.com/v3/api/graphql/v1/v3/query/"+locale+"%3E"+locale+"?filter[type]="+type+"&page[limit]=1&filter[uriSlug]="+title_url+"&rb3Schema=v1:hero"
getvideo_return=downloader.get(get_video_url,verify=False)
response=json.load(StringIO(getvideo_return.text))

if(identifier == "live/"):
    video_link= live_video_url + response["data"]["id"][:60] + "/"+token+"/playlist.m3u8"
        
elif(identifier == "videos/"):
    video_link= live_video_url + response["data"]["id"][:55] + "/"+token+"/playlist.m3u8"
        
elif(identifier == "episodes/"):
    video_link= live_video_url + response["data"]["id"][:63] + "/"+token+"/playlist.m3u8"
        
elif(identifier == "films/"):
    video_link= live_video_url + response["data"]["id"][:54] + "/"+token+"/playlist.m3u8"
        
elif(identifier == "shows/"):
    video_link= live_video_url + response["data"]["id"][:54] + "/"+token+"/playlist.m3u8"


os.system('ffmpeg -i '+video_link+' -c copy -bsf:a aac_adtstoasc "'+outpath+title+'.mp4"')
