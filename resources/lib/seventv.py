#!/usr/bin/python
# -*- coding: utf-8 -*-
# coding: utf8
import sys
import json
import urllib, urllib2
import xbmc, xbmcaddon, xbmcgui, xbmcplugin
import ast

addon = xbmcaddon.Addon()
addon_handle = int(sys.argv[1])
apiKey = addon.getSetting('apiKey')
if not apiKey:
    apiKey = '255d97968f286ada2c90548e34230628'
    addon.setSetting('apiKey', apiKey)

def playVideo(video_id, client_location, source_id=None, infoLabels=None):
    from hashlib import sha1

    # Inputstream settings
    isInputstream = getInputstreamAddon()
        
    if not isInputstream:
        access_token = 'h''b''b''t''v'  
        salt = '0''1''r''e''e''6''e''L''e''i''w''i''u''m''i''e''7''i''e''V''8''p''a''h''g''e''i''T''u''i''3''B'
        client_name = 'h''b''b''t''v'
    else:
        access_token = 'seventv-web'  
        salt = '01!8d8F_)r9]4s[qeuXfP%'
        client_name = ''

    if source_id is None:
        source_id = 0 
        json_url = 'http://vas.sim-technik.de/vas/live/v2/videos/%s?access_token=%s&client_location=%s&client_name=%s' % (video_id, access_token, client_location, client_name)
        json_data = getUrl(json_url)

        if isInputstream:
          for stream in json_data['sources']:
            if  stream['mimetype'] == 'application/dash+xml': 
              if int(source_id) <  int(stream['id']):               
                source_id = stream['id']
          print source_id
        else:
          if json_data["is_protected"] == True:
            xbmc.executebuiltin('Notification("Inputstream", "DRM geschützte Folgen gehen nur mit Inputstream")')
            return
          else:
            for stream in json_data['sources']:
              if  stream['mimetype'] == 'video/mp4':           
                if int(source_id) <  int(stream['id']):                                   
                    source_id = stream['id']

    client_id_1 = salt[:2] + sha1(''.join([str(video_id), salt, access_token, client_location, salt, client_name]).encode('utf-8')).hexdigest()
       
    json_url = 'http://vas.sim-technik.de/vas/live/v2/videos/%s/sources?access_token=%s&client_location=%s&client_name=%s&client_id=%s' % (video_id, access_token, client_location, client_name, client_id_1)            
    json_data = getUrl(json_url)
    server_id = json_data['server_id']
    
    #client_name = 'kolibri-1.2.5'    
    client_id = salt[:2] + sha1(''.join([salt, video_id, access_token, server_id,client_location, str(source_id), salt, client_name]).encode('utf-8')).hexdigest()
    url_api_url = 'http://vas.sim-technik.de/vas/live/v2/videos/%s/sources/url?%s' % (video_id, urllib.urlencode({
        'access_token': access_token,
        'client_id': client_id,
        'client_location': client_location,
        'client_name': client_name,
        'server_id': server_id,
        'source_ids': str(source_id),
    }))

    json_data = getUrl(url_api_url)
    max_id = 0
    for stream in json_data["sources"]:
        ul = stream["url"]
        try:
            sid = re.compile('-tp([0-9]+).mp4', re.DOTALL).findall(ul)[0]
            id = int(sid)
            if max_id < id:
                max_id = id
                data = ul
        except:
          data=ul                                 

    userAgent = 'User-Agent=Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36'

    li = xbmcgui.ListItem(path=data + "|"+userAgent)         
    li.setProperty("inputstream.adaptive.license_type", "com.widevine.alpha")
    li.setProperty("inputstream.adaptive.manifest_type", "mpd")
    li.setProperty('inputstreamaddon', 'inputstream.adaptive')
    
    try:
        lic = json_data["drm"]["licenseAcquisitionUrl"]        
        token = json_data["drm"]["token"]                
        li.setProperty('inputstream.adaptive.license_key', lic +"?token="+token+"|"+userAgent+"|R{SSM}|")            
    except:
        pass
    
    if infoLabels is not None:
        try:
            li.setInfo('video', ast.literal_eval(infoLabels))
        except:
            pass


    xbmcplugin.setResolvedUrl(addon_handle, True, li) 
    
def getUrl(url,data="x",header=""):
    xbmc.log("Get Url: " + url)

    opener = urllib2.build_opener()           
    userAgent = "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:49.0) Gecko/20100101 Firefox/49.0"
    if header == "":
      opener.addheaders = [('User-Agent', userAgent), ('key', apiKey)]        
    else:
      opener.addheaders = header        
    try:
      if data!="x" :
         content = opener.open(url,data=data).read()
      else:
         content = opener.open(url).read()
    except urllib2.HTTPError as e:
         #print e.code   
         cc = e.read()  
         xbmc.log("Error : " + cc)
   
    opener.close()
    return json.loads(content)

# Get installed inputstream addon
def getInputstreamAddon():
    r = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "id": 1, "method": "Addons.GetAddonDetails", "params": {"addonid":"inputstream.adaptive", "properties": ["enabled"]}}')
    data = json.loads(r)
    if not "error" in data.keys():
        if data["result"]["addon"]["enabled"] == True:
            return True
        
    return None
