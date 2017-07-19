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

    if params['action'] == 'listLetters':
        nav.listLetters(params.get('channel_id'))
    elif params['action'] == 'listTVShows':
        nav.listTVShows(params.get('channel_id'), params.get('letter'), int(params.get('page')))
    elif params['action'] == 'getTVShow':
        nav.getTVShow(params.get('channel_id'), params.get('tvshow_id'), params.get('iconImage'), params.get('infoLabels'))
    elif params['action'] == 'listVideos':
        nav.listVideos(params.get('channel_id'), params.get('tvshow_id'), params.get('video_type'), int(params.get('page')))
    elif params['action'] == 'playVideo':
        seventv.playVideo(params.get('video_id'), params.get('video_url'))
else:
    nav.rootDir()