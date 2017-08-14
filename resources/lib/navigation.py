# coding: utf8
import sys
import xbmc, xbmcaddon, xbmcgui, xbmcplugin
import re
import ast
from datetime import datetime

import seventv
import resources.lib.common as common

addon = xbmcaddon.Addon()
addon_handle = int(sys.argv[1])
icon_path = xbmc.translatePath(addon.getAddonInfo('path') +'/resources/media/channels/').decode('utf-8')

serviceUrl = 'https://mobileapi.prosiebensat1.com/7tv/web/v1'

img_profile = '/profile:ezone-teaser'
img_sizes = ['140x79', '200x260', '229x122', '300x160', '620x348']
items_per_page = int(addon.getSetting('items_per_page'))

rootDirs = [ 
              {'label': 'Highlights', 'action': 'recenthighlights', 'path': '/recent/highlights'}
            , {'label': 'Beliebte Sendungen', 'action': 'recenttvshows', 'path': '/recent/tvshows'}
            , {'label': 'Ganze Folgen', 'action': 'recentvideos', 'path': '/recent/videos'}
            , {'label': 'Mediatheken', 'action': 'libraries'} 
           ]

channels = [
              {'label': 'Alle Sender', 'icon': 'seventv.png'}
            , {'id': '1', 'label': 'ProSieben', 'icon': 'pro7.png'}
            , {'id': '2', 'label': 'SAT.1', 'icon': 'sat1.png'}
            , {'id': '3', 'label': 'kabel eins', 'icon': 'kabel1.png'}
            , {'id': '4', 'label': 'Sixx', 'icon': 'sixx.png'}
            , {'id': '5', 'label': 'ProSieben MAXX', 'icon': 'prosiebenmaxx.png'}
            , {'id': '6', 'label': 'SAT.1 Gold', 'icon': 'sat1gold.png'}                
            , {'id': '7', 'label': 'kabel eins Doku', 'icon': 'kabeleinsdoku.png'}
           ]

letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '#']

tvShowDirs = ['Clips', 'Ganze Folgen']
        
def rootDir():
    for dir in rootDirs:
        url = common.build_url({'action': dir.get('action'), 'path': dir.get('path')})
        addDir(dir.get('label'), url)
        xbmcgui.ListItem(dir.get('label'))

    xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=True)
    
def showChannels():
    for channel in channels:
        parameter = {'action': 'listLetters'}
        if channel.get('id', None) is not None:
            parameter['channel_id'] = channel.get('id')

        url = common.build_url(parameter)
        addDir(channel.get('label'), url, icon_path + channel.get('icon'))
        xbmcgui.ListItem(channel.get('label'))

    xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=True)
    
def addDir(label, url, icon=None, infoLabels={}):
    return addVideo(label, url, icon, infoLabels)

def addVideo(label, url, icon=None, infoLabels={}, isFolder=True):
    li = xbmcgui.ListItem(label, iconImage=icon)
    li.setInfo('video', infoLabels)
    if not isFolder:
        li.setProperty('IsPlayable', 'true')
        li.setArt({'banner': icon})

    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=isFolder)
    return li
    
def listLetters(channel_id):
    for letter in letters:
        parameter = {'action': 'listTVShows', 'path': '/tvshows', 'letter': letter if letter != '#' else '\d', 'page': 0}
        if channel_id is not None:
            parameter['channel_id'] = channel_id

        url = common.build_url(parameter)
        addDir(letter.title(), url)
        xbmcgui.ListItem(letter.title())
        
    xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=True)

def listTVShows(path, channel_id=None, letter=None, page=0):
    selection = '{totalCount,data{id,titles{default},images(subType:"Teaser"){url,subType},shortDescriptions{default}}}'
#    url = serviceUrl + path + '?selection=' + selection + "&limit=" + str(items_per_page) + '&skip=' + str(page * items_per_page) + '&sortBy=titles.default&sortAscending=true'
    url = serviceUrl + path + '?selection=' + selection + '&sortBy=titles.default&sortAscending=true' + '&limit=5000'

    if channel_id is not None:
        url += '&channelId=' + channel_id    
#    if letter is not None:
#        url += '&search=(^' + letter + ')'

    response = seventv.getUrl(url).get('response')
    content = response.get('data')

    for item in content:
        title = item.get('titles').get('default')

        if letter is not None:
            if letter != '\d' and re.search('(^[' + letter.lower() + letter.title() + '])', title) is None:
                continue
            elif letter == '\d' and re.search('(^' + letter + ')', title) is None:
                continue

        iconImage = getIcon(item)
        infoLabels = getInfoLabel(item, 'tvshow', channel_id)
        
        parameter = {'action': 'getTVShow', 'tvshow_id': item.get('id'), 'iconImage': iconImage, 'infoLabels': infoLabels}
        if channel_id is not None:
            parameter['channel_id'] = channel_id

        url = common.build_url(parameter)
        
        addDir(title, url, iconImage, infoLabels)
        xbmcplugin.setContent(addon_handle, 'tvshows')

#    if response.get('totalCount') > ((page + 1) * items_per_page):
#        page += 1
#
#        parameter = {'action': 'listTVShows', 'path': path, 'letter': letter if letter != '#' else '\d', 'page': page}
#        if channel_id is not None:
#            parameter['channel_id'] = channel_id
#
#        url = common.build_url(parameter)
#        addDir('Nächste Seite', url)

    xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=True)

def getTVShow(channel_id, tvshow_id, iconImage, infoLabels):
    for tvShowDir in tvShowDirs:
        parameter = {'action': 'listVideos', 'path': '/videos', 'tvshow_id': tvshow_id, 'video_type': tvShowDir, 'page': 0}
        if channel_id is not None:
            parameter['channel_id'] = channel_id

        url = common.build_url(parameter)

        addDir(tvShowDir, url, iconImage, ast.literal_eval(infoLabels))
        xbmcplugin.setContent(addon_handle, 'tvshows')

    xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=True)

def listVideos(path, channel_id=None, tvshow_id=None, video_type=None, page=0):
    selection = '{totalCount,data{id,type,titles{default},images(subType:"Teaser"){url,subType},shortDescriptions{default},links,duration, subType,productionYear,createdAt,tvShow{titles{default}},season{number},episode{number,titles{default},metaDescriptions{default},productionYear,createdAt,modifiedAt,airdates}}}'
#    url = serviceUrl + path + '?selection=' + selection + '&limit=' + str(items_per_page) + '&skip=' + str(page * items_per_page) + '&sortBy=airdate&sortAscending=false'
    url = serviceUrl + path + '?selection=' + selection + '&sortBy=airdate&sortAscending=false' + '&limit=5000'
    
    if channel_id is not None:
        url += '&channelId=' + channel_id 
    if tvshow_id is not None:
        url += '&tvShowId=' + tvshow_id
    if video_type == tvShowDirs[0]:
        url += '&subType=!Hauptfilm'
    elif video_type == tvShowDirs[1]:
        url += '&subType=Hauptfilm'

    response = seventv.getUrl(url).get('response')
    content = response.get('data')

    for item in content:
        title = item.get('titles').get('default')
        iconImage = getIcon(item) 
        infoLabels = getInfoLabel(item, 'video', channel_id)
            
        url = common.build_url({'action': 'playVideo', 'video_id': item.get('id'), 'video_url': item.get('links')[0].get('url') if len(item.get('links')) > 0 else None})
        
        addVideo(title, url, iconImage, infoLabels, False)
        xbmcplugin.setContent(addon_handle, 'episode')

#    if response.get('totalCount') > ((page + 1) * items_per_page):
#        page += 1
#
#        parameter = {'action': 'listVideos', 'path': path, 'tvshow_id': tvshow_id, 'video_type': video_type, 'page': page}
#        if channel_id is not None:
#            parameter['channel_id'] = channel_id
#        if tvshow_id is not None:
#            parameter['tvshow_id'] = tvshow_id
#        if video_type is not None:
#            parameter['video_type'] = video_type
#
#        url = common.build_url(parameter)
#        addDir('Nächste Seite', url)

    xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=True)

def getInfoLabel(item_data, item_type, channel_id):
    info = {}

    info['title'] = item_data.get('titles').get('default') if item_data.get('titles').get('default').find('Episode') == -1 else item_data.get('titles').get('default')[item_data.get('titles').get('default').find(':') + 1:]
    if item_data.get('shortDescriptions', {}).get('default', '') != '':
        info['plot'] = cleanhtml(item_data.get('shortDescriptions').get('default'))
    if item_data.get('duration', 0) > 0:
        info['duration'] = item_data.get('duration') / 1000
    if item_data.get('productionYear', 0) > 0 and item_data.get('productionYear') > 1901:
        info['year'] = item_data.get('productionYear')
    if item_data.get('createdAt', 0) > 0:
        info['date'] = datetime.fromtimestamp(item_data.get('createdAt')).strftime("%d.%m.%Y")
    if item_data.get('modifiedAt', 0) > 0:
        info['date'] = datetime.fromtimestamp(item_data.get('modifiedAt')).strftime("%d.%m.%Y")

    if len(item_data.get('tvShow', {})) > 0:
        if item_data.get('tvShow', {}).get('titles', {}).get('default', '') != '':
            info['tvshowtitle'] =  item_data.get('tvShow', {}).get('titles', {}).get('default', '')
        
    if len(item_data.get('season', {})) > 0:
        if item_data.get('season').get('number', 0) > 0:
            info['season'] = item_data.get('season').get('number')
            
    if len(item_data.get('episode', {})) > 0:
        #info['title'] = item_data.get('episode').get('titles').get('default') if item_data.get('episode').get('titles').get('default').find('Folge') == -1 else info['title']
        if item_data.get('episode').get('number', 0) > 0:
            info['episode'] = item_data.get('episode').get('number')
        elif 'season' in info:
            del info['season']
        if item_data.get('episode').get('metaDescriptions', {}).get('default', '') != '':
            info['plot'] = item_data.get('episode').get('metaDescriptions').get('default')
        if item_data.get('episode').get('productionYear', 0) > 0 and item_data.get('episode').get('productionYear') > 1901:
            info['year'] = item_data.get('episode').get('productionYear')
        if item_data.get('episode').get('createdAt', 0) > 0:
            info['date'] = datetime.fromtimestamp(item_data.get('episode').get('createdAt')).strftime("%d.%m.%Y")  
        if len(item_data.get('episode').get('airdates', [])) > 0:
            dates = [date for date in item_data.get('episode').get('airdates') if date.get('brand') == channel_id] if len([date for date in item_data.get('episode').get('airdates') if date.get('brand') == channel_id]) > 0 else item_data.get('episode').get('airdates')
            info['aired'] = datetime.fromtimestamp(dates[0].get('date')).strftime("%Y-%m-%d")
            info['dateadded'] = datetime.fromtimestamp(dates[0].get('date')).strftime("%Y-%m-%d %H:%M:%S")

    if item_type == 'tvshow':
        info['tvshowtitle'] = info['title']

    if 'season' not in info and 'episode' not in info:
        info['mediatype'] = 'movie'
    else:
        info['mediatype'] = 'episode'

    return info

def cleanhtml(raw_html):
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    return cleantext


def getIcon(item):
    return item.get('images')[0].get('url', '') + img_profile + img_sizes[4] if len(item.get('images')) > 0 else ''