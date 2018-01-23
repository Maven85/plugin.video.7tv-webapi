#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import xbmc, xbmcaddon, xbmcgui, xbmcplugin
import re
from datetime import datetime

import seventv
import common

addon = xbmcaddon.Addon()
addon_handle = int(sys.argv[1])
icon_path = xbmc.translatePath(addon.getAddonInfo('path') + '/resources/media/channels/').decode('utf-8')

serviceUrl = 'https://mobileapi.prosiebensat1.com/7tv/web/v1'

img_profile = '/profile:ezone-teaser'
img_sizes = ['140x79', '200x260', '229x122', '300x160', '620x348']
videos_per_page = int(addon.getSetting('videos_per_page'))

rootDirs = [
              {'label': 'Live', 'action': 'livechannels'}
            , {'label': 'Highlights', 'action': 'recenthighlights', 'path': '/recent/highlights'}
            , {'label': 'Beliebte Sendungen', 'action': 'recenttvshows', 'path': '/recent/tvshows'}
            , {'label': 'Ganze Folgen', 'action': 'recentvideos', 'path': '/recent/videos'}
            , {'label': 'Mediatheken', 'action': 'libraries'}
           ]

channels = [
              {
                  'label': 'Alle Sender'
                , 'icon': 'seventv.png'
              }
            , {
                  'id': '1'
                , 'label': 'ProSieben'
                , 'icon': 'pro7.png'
                , 'property_name': 'prosieben-de-24x7'
                , 'client_location': 'https://www.prosieben.de/livestream'
                , 'access_token': 'prosieben'
                , 'client_token':  '01b353c155a9006e80ae7c5ed3eb1c09c0a6995556'
              }
            , {
                  'id': '2'
                , 'label': 'SAT.1'
                , 'icon': 'sat1.png'
                , 'property_name': 'sat1-de-24x7'
                , 'client_location': 'https://www.sat1.de/livestream'
                , 'access_token': 'sat1'
                , 'client_token':  '01e491d866b37341734d691a8acb48af37a77bf26f'
              }
            , {
                  'id': '3'
                , 'label': 'kabel eins'
                , 'icon': 'kabel1.png'
                , 'property_name': 'kabeleins-de-24x7'
                , 'client_location': 'https://www.kabeleins.de/livestream'
                , 'access_token': 'kabeleins'
                , 'client_token':  '014c87bfe2ce4aebf6219ed699602a1f152194e4cd'
              }
            , {
                  'id': '4'
                , 'label': 'Sixx'
                , 'icon': 'sixx.png'
                , 'property_name': 'sixx-de-24x7'
                , 'client_location': 'https://www.sixx.de/livestream'
                , 'access_token': 'sixx'
                , 'client_token':  '017705703133050842d3ca11fc20a6fc205b8b4025'
              }
            , {
                  'id': '5'
                , 'label': 'ProSiebenMaxx'
                , 'icon': 'prosiebenmaxx.png'
                , 'property_name' : 'prosiebenmaxx-de-24x7'
                , 'client_location': 'https://www.prosiebenmaxx.de/livestream'
                , 'access_token' : 'prosiebenmaxx'
                , 'client_token':  '01963623e9b364805dbe12f113dba1c4914c24d189'
              }
            , {
                  'id': '6'
                , 'label': 'SAT.1 Gold'
                , 'icon': 'sat1gold.png'
                , 'property_name' : 'sat1gold-de-24x7'
                , 'client_location': 'https://www.sat1gold.de/livestream'
                , 'access_token' : 'sat1gold'
                , 'client_token': '01107e433196365e4d54d0f90bdf1070cd2df5e190'
              }
            , {
                  'id': '7'
                , 'label': 'kabel eins Doku'
                , 'icon': 'kabeleinsdoku.png'
                , 'property_name' : 'kabeleinsdoku-de-24x7'
                , 'client_location': 'https://www.kabeleinsdoku.de/livestream'
                , 'access_token' : 'kabeleinsdoku'
                , 'client_token': '01ea6d32ff5de5d50d0290dbdf819f9b856bcfd44a'
              }
            , {
                  'id': '110'
                , 'label': 'DMAX'
                , 'icon': 'dmax.png'
              }
            , {
                  'id': '111'
                , 'label': 'TLC'
                , 'icon': 'tlc.png'
              }
            , {
                  'id': '112'
                , 'label': 'Eurosport'
                , 'icon': 'eurosport.png'
              }
           ]

letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '#']

tvShowDirs = ['Clips', 'Ganze Folgen']


def rootDir():
    for dir in rootDirs:
        url = common.build_url({'action': dir.get('action'), 'path': dir.get('path')})
        addDir(dir.get('label'), url)

    xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=True)


def showLiveChannels():
    selection = '{totalCount,data{title,tvShow{title},season{number},episode{number},images(subType:"cover"){url,subType},tvChannelName,description,productionYear,startTime,endTime}}'
    url = '{}/epg/now?selection={}'.format(serviceUrl, selection)

    response = seventv.getUrl(url).get('response')
    content = response.get('data')

    addDir('Aktualisieren', 'xbmc.executebuiltin("container.refresh")', infoLabels={'plot': 'Aktualisieren'})
    for channel in channels:
        infoLabels = {}
        thumbnailImage = None
        if channel.get('property_name', None) is not None:
            for channel_content in content:
                if channel_content.get('tvChannelName').lower() == channel.get('label').lower():
                    infoLabels = getInfoLabel(channel_content, 'live', channel.get('id'))
                    thumbnailImage = getIcon(channel_content)

            url = common.build_url({'action': 'playLiveTV', 'property_name': channel.get('property_name'), 'client_location': channel.get('client_location'), 'access_token': channel.get('access_token'), 'client_token': channel.get('client_token'), 'callback': channel.get('callback'), 'infoLables': infoLabels})
            title = infoLabels.get('title') if infoLabels.get('tvshowtitle', None) is None or infoLabels.get('tvshowtitle') == infoLabels.get('title') else '[COLOR blue]' + infoLabels.get('tvshowtitle') + ' |[/COLOR] ' + infoLabels.get('title')
            title = '[COLOR orange][{}][/COLOR] {}'.format(channel.get('label'), title)
            addFile(title, url, icon_path + channel.get('icon'), thumbnailImage, infoLabels)

    xbmcplugin.setContent(addon_handle, 'files')
    xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=False)


def showChannels():
    for channel in channels:
        parameter = {'action': 'listLetters'}
        if channel.get('id', None) is not None:
            parameter['channel_id'] = channel.get('id')

        url = common.build_url(parameter)
        addDir(channel.get('label'), url, icon_path + channel.get('icon'))

    xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=True)


def addDir(label, url, icon=None, thumbnail=None, infoLabels={}):
    addFile(label, url, icon, thumbnail, infoLabels, True)


def addFile(label, url, icon=None, thumbnail=None, infoLabels={}, isFolder=False):
    li = xbmcgui.ListItem(label)
    li.setInfo('video', infoLabels)
    li.setArt({'banner': icon, 'fanart': icon, 'icon': icon, 'thumb': thumbnail})
    li.setProperty('IsPlayable', str(isFolder))

    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=isFolder)


def listLetters(channel_id):
    for letter in letters:
        parameter = {'action': 'listTVShows', 'path': '/tvshows', 'letter': letter if letter != '#' else '\d', 'page': 0}
        if channel_id is not None:
            parameter['channel_id'] = channel_id

        url = common.build_url(parameter)
        addDir(letter.title(), url)

    xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=True)


def listTVShows(path, channel_id=None, letter=None, page=0):
    selection = '{totalCount,data{id,titles{default},images(subType:"Teaser"){url,subType},shortDescriptions{default}}}'
    # url = '{}{}?selection={}&limit={}&skip={}&sortBy=titles.default&sortAscending=true'.format(serviceUrl, path, selection, videos_per_page, page * videos_per_page)
    url = '{}{}?selection={}&sortBy=titles.default&sortAscending=true&limit=5000'.format(serviceUrl, path, selection)

    if channel_id is not None:
        url += '&channelId=' + channel_id
    # if letter is not None:
        # url += '&search=(^{})'.format(letter)

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

        addDir(title, url, iconImage, iconImage, infoLabels)
        xbmcplugin.setContent(addon_handle, 'tvshows')

#    if response.get('totalCount') > ((page + 1) * videos_per_page):
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

        addDir(tvShowDir, url, iconImage, iconImage, infoLabels)
        xbmcplugin.setContent(addon_handle, 'tvshows')

    xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=True)


def listVideos(path, channel_id=None, tvshow_id=None, video_type=None, page=0):
    selection = '{totalCount,data{id,type,titles{default},images(subType:"Teaser"){url,subType},shortDescriptions{default},links,duration, subType,productionYear,createdAt,tvShow{titles{default}},season{number},episode{number,titles{default},metaDescriptions{default},productionYear,createdAt,modifiedAt,airdates}}}'
    url = '{}{}?selection={}&limit={}&skip={}&sortBy={}&sortAscending={}'.format(serviceUrl, path, selection, videos_per_page, page * videos_per_page, 'seasonsOrder' if tvshow_id is not None else 'airdate', 'true' if tvshow_id is not None else 'false')

    if channel_id is not None:
        url += '&channelId={}'.format(channel_id)
    if tvshow_id is not None:
        url += '&tvShowId={}'.format(tvshow_id)
    if video_type == tvShowDirs[0]:
        url += '&subType=!Hauptfilm'
    elif video_type == tvShowDirs[1]:
        url += '&subType=Hauptfilm'

    response = seventv.getUrl(url).get('response')
    content = response.get('data')

    for item in content:
        if len(item.get('links')) == 0:
            continue

        iconImage = getIcon(item)
        infoLabels = getInfoLabel(item, 'video', channel_id)
        title = infoLabels['title'] if tvshow_id is not None else '[COLOR orange][{}][/COLOR] [COLOR blue]{} |[/COLOR] {}'.format(item.get('links')[0].get('brand'), item.get('tvShow', {}).get('titles', {}).get('default', ''), item.get('titles').get('default'))

        if tvshow_id is not None and infoLabels.get('season', None) is not None and infoLabels.get('episode', None) is not None:
            title = '{:02d}x{:02d}. {}'.format(infoLabels.get('season'), infoLabels.get('episode'), infoLabels.get('title'))

        url = common.build_url({'action': 'playVideo', 'video_id': item.get('id'), 'video_url': item.get('links')[0].get('url'), 'infoLabels': infoLabels})

        addFile(title, url, iconImage, iconImage, infoLabels)
        xbmcplugin.setContent(addon_handle, 'episode')

    if response.get('totalCount') > ((page + 1) * videos_per_page):
        page += 1

        parameter = {'action': 'listVideos', 'path': path, 'tvshow_id': tvshow_id, 'video_type': video_type, 'page': page}
        if channel_id is not None:
            parameter['channel_id'] = channel_id
        if tvshow_id is not None:
            parameter['tvshow_id'] = tvshow_id
        if video_type is not None:
            parameter['video_type'] = video_type

        url = common.build_url(parameter)
        addDir('Nächste Seite', url)

    xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=True)


def getInfoLabel(item_data, item_type, channel_id):
    info = {}

    if item_type != 'live':
        info['title'] = item_data.get('titles').get('default') if item_data.get('titles', None) is not None and item_data.get('titles').get('default', '').find('Episode') == -1 else item_data.get('titles').get('default')[item_data.get('titles').get('default').find(':') + 1:]
        if item_data.get('shortDescriptions', {}).get('default', None) is not None:
            info['plot'] = cleanhtml(item_data.get('shortDescriptions').get('default'))
    else:
        info['title'] = item_data.get('title') if item_data.get('title') is not None else item_data.get('tvShow').get('title')
        if item_data.get('description', None) is not None:
            info['plot'] = item_data.get('description')

    if item_data.get('duration', None) is not None and item_data.get('duration') > 0:
        info['duration'] = item_data.get('duration') / 1000
    if item_data.get('productionYear', None) is not None and  item_data.get('productionYear') > 0 and item_data.get('productionYear') > 1901:
        info['year'] = item_data.get('productionYear')
    if item_data.get('createdAt', None) is not None and item_data.get('createdAt') > 0:
        info['date'] = datetime.fromtimestamp(item_data.get('createdAt')).strftime("%d.%m.%Y")
    if item_data.get('modifiedAt', None) is not None and item_data.get('modifiedAt') > 0:
        info['date'] = datetime.fromtimestamp(item_data.get('modifiedAt')).strftime("%d.%m.%Y")
    if item_data.get('startTime', None) is not None and item_data.get('startTime') > 0 and item_data.get('endTime', None) is not None and item_data.get('endTime') > 0:
        info['plot'] = datetime.fromtimestamp(item_data.get('startTime')).strftime("%H:%M") + ' - ' + datetime.fromtimestamp(item_data.get('endTime')).strftime("%H:%M") + ("\n\n" + info.get('plot') if info.get('plot', None) is not None else '')

    if len(item_data.get('tvShow', {})) > 0:
        if item_data.get('tvShow', {}).get('titles', {}).get('default', None) is not None:
            info['tvshowtitle'] = item_data.get('tvShow').get('titles').get('default')
        elif item_data.get('tvShow', {}).get('title', None) is not None:
            info['tvshowtitle'] = item_data.get('tvShow').get('title')

    if len(item_data.get('season', {})) > 0 and item_data.get('season').get('number', None) is not None and item_data.get('season').get('number') > 0:
        info['season'] = item_data.get('season').get('number')

    if len(item_data.get('episode', {})) > 0:
        # info['title'] = item_data.get('episode').get('titles').get('default') if item_data.get('episode').get('titles').get('default').find('Folge') == -1 else info['title']
        if item_data.get('episode').get('number', None) is not None and item_data.get('episode').get('number') > 0:
            info['episode'] = item_data.get('episode').get('number')
        elif 'season' in info:
            del info['season']
        if item_data.get('episode').get('metaDescriptions', {}).get('default', None) is not None and item_data.get('episode').get('metaDescriptions', {}).get('default', '') != '':
            info['plot'] = item_data.get('episode').get('metaDescriptions').get('default')
        if item_data.get('episode').get('productionYear', None) is not None and item_data.get('episode').get('productionYear') > 0 and item_data.get('episode').get('productionYear') > 1901:
            info['year'] = item_data.get('episode').get('productionYear')
        if item_data.get('episode').get('createdAt', None) is not None and item_data.get('episode').get('createdAt') > 0:
            info['date'] = datetime.fromtimestamp(item_data.get('episode').get('createdAt')).strftime("%d.%m.%Y")
        if len(item_data.get('episode').get('airdates', {})) > 0:
            dates = [date for date in item_data.get('episode').get('airdates') if date.get('brand') == channel_id] if len([date for date in item_data.get('episode').get('airdates') if date.get('brand') == channel_id]) > 0 else item_data.get('episode').get('airdates')
            info['aired'] = datetime.fromtimestamp(dates[0].get('date')).strftime("%Y-%m-%d")
            info['dateadded'] = datetime.fromtimestamp(dates[0].get('date')).strftime("%Y-%m-%d %H:%M:%S")

    if info.get('season', None) is None and item_data.get('titles', None) is not None and item_data.get('titles').get('default').find('Staffel') > -1:
        info['season'] = re.compile('Staffel ([0-9]+)', re.DOTALL).findall(item_data.get('titles').get('default'))[0]

    if info.get('episode', None) is None and item_data.get('titles', None) is not None and item_data.get('titles').get('default').find('Episode') > -1:
        info['episode'] = re.compile('Episode ([0-9]+)', re.DOTALL).findall(item_data.get('titles').get('default'))[0]

    if item_type == 'tvshow':
        info['tvshowtitle'] = info['title']
    else:
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
    return item.get('images')[0].get('url', '') + img_profile + img_sizes[4] if len(item.get('images', {})) > 0 else None
