#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import urllib
import base64
import xbmc
import json

import resources.lib.seventv as seventv
import resources.lib.navigation as nav

addon_handle = int(sys.argv[1])
seventv.addon_handle = addon_handle
nav.addon_handle = addon_handle

params = urllib.unquote(sys.argv[2][1:])
if len(params) > 0:
    if len(params) % 4 != 0:
        params += '=' * (4 - len(params) % 4)
    params = dict(json.loads(base64.urlsafe_b64decode(params)))

# Router for all plugin actions
if 'action' in params:
    xbmc.log('params' + str(params))

    if params['action'] == 'livechannels':
        nav.showLiveChannels()
    elif params['action'] == 'recenthighlights':
        nav.listVideos(params.get('path'))
    elif params['action'] == 'recenttvshows':
        nav.listTVShows(params.get('path'))
    elif params['action'] == 'recentvideos':
        nav.listVideos(params.get('path'))
    elif params['action'] == 'libraries':
        nav.showChannels()
    if params['action'] == 'listLetters':
        nav.listLetters(params.get('channel_id', None))
    elif params['action'] == 'listTVShows':
        nav.listTVShows(params.get('path'), params.get('channel_id', None), params.get('letter'), int(params.get('page')))
    elif params['action'] == 'getTVShow':
        nav.getTVShow(params.get('channel_id', None), params.get('tvshow_id'), params.get('iconImage'), params.get('infoLabels'))
    elif params['action'] == 'listVideos':
        nav.listVideos(params.get('path'), params.get('channel_id', None), params.get('tvshow_id'), params.get('video_type'), int(params.get('page')))
    elif params['action'] == 'playVideo':
        seventv.playVideo(params.get('video_id'), params.get('video_url'), infoLabels=params.get('infoLabels', None))
    elif params['action'] == 'playLiveTV':
        seventv.playLiveTV(params.get('property_name'), params.get('client_location'), params.get('access_token'), params.get('client_token'), params.get('infoLabels'))
else:
    nav.rootDir()
