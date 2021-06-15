#!/usr/bin/python3
import requests
import json
import ffmpeg
import argparse
from pathlib import Path
from getpass import getpass
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
from io import StringIO
import sys, getopt


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
downloader.headers.update(header)
outpath=""
type=""
mark=36
links=[]

try:
    opts, args = getopt.getopt(sys.argv[1:],"hl:o:",["help","url=","output="])
except getopt.GetoptError:
    print("Usage: rbtv-dl.py -l <URL> -o <OUTPUT_FOLDER>")
    sys.exit(2)

for opt, arg in opts:
    if(opt == '-h'):
        print("Usage: rbtv-dl.py -l <URL> -o <OUTPUT_FOLDER>")
        sys.exit()
        
    elif(opt == '-o'):
        outpath=arg
        if(outpath[len(outpath)-1] != '/'):
            outpath=outpath+'/'
    else:
        links.append(arg)


for j in links:
    link=j
    page=downloader.get(token_url, verify=False)
    #print(page.text)
    response=json.load(StringIO(page.text))
    token=response["token"]
    #print(token)
    #link="https://www.redbull.com/int-en/live/red-bull-bc-one-cypher-russia-2021"#video_source
    identifier=link[31:36]
    if(identifier == "live/"):
            type="live-videos"
    else:
        mark=38
        identifier=link[31:38]
        if(identifier == "videos/"):
            type="videos"
        else:
            mark=40
            identifier=link[31:40]
            if(identifier == "episodes/"):
                type="episode-videos"
            else:
                mark=37
                identifier=link[31:37]
                if(identifier == "films/"):
                    type="films"
                else:
                    mark=37
                    identifier=link[31:37]
                    if(identifier == "shows/"):
                        type="shows"

    title=link[mark:len(link)]
    get_video_url="https://www.redbull.com/v3/api/graphql/v1/v3/query/en-INT%3Een-INT?filter[type]="+type+"&page[limit]=1&filter[uriSlug]="+title+"&rb3Schema=v1:hero"

    getvideo_return=downloader.get(get_video_url,verify=False)
    response=json.load(StringIO(getvideo_return.text))

  #  print("VIDEO="+response["data"]["id"]) #video_id

    if(identifier == "live/"):
        video_link= live_video_url + response["data"]["id"][:60] + "/"+token+"/playlist.m3u8"
       # print(video_link)
        
    elif(identifier == "videos/"):
        video_link= live_video_url + response["data"]["id"][:55] + "/"+token+"/playlist.m3u8"
        
    elif(identifier == "episodes/"):
        video_link= live_video_url + response["data"]["id"][:63] + "/"+token+"/playlist.m3u8"
        
    elif(identifier == "films/"):
        video_link= live_video_url + response["data"]["id"][:54] + "/"+token+"/playlist.m3u8"
        
    elif(identifier == "shows/"):
        video_link= live_video_url + response["data"]["id"][:54] + "/"+token+"/playlist.m3u8"

    #page=downloader.get(video_link, verify=False)
    #print(page.content)

    stream=ffmpeg.input(video_link)
    stream=ffmpeg.output(stream, outpath+title+'.mp4')
    ffmpeg.run(stream)
