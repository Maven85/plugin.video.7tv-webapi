#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import urlparse

import resources.lib.seventv as seventv
import resources.lib.navigation as nav

params = dict(urlparse.parse_qsl(sys.argv[2][1:]))

# Router for all plugin actions
if 'action' in params:
    print params

    if params['action'] == 'recenthighlights':
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
        seventv.playVideo(params.get('video_id'), params.get('video_url'))
else:
    nav.rootDir()