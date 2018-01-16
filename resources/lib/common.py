#!/usr/bin/python
# -*- coding: utf-8 -*-

import xbmcaddon
import base64
import json

base_url = "plugin://" + xbmcaddon.Addon().getAddonInfo('id')


def build_url(query):
    return base_url + '?' + base64.urlsafe_b64encode(json.dumps(query))
