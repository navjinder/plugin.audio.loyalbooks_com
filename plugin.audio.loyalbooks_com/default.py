#!/usr/bin/python
# -*- coding: utf-8 -*-
import urllib,urllib2,re,xbmcplugin,xbmcgui,sys,xbmcaddon,base64,socket

socket.setdefaulttimeout(30)
pluginhandle = int(sys.argv[1])
addon = xbmcaddon.Addon(id='plugin.audio.loyalbooks_com')
translation = addon.getLocalizedString
forceViewMode=addon.getSetting("forceViewMode")
viewMode=str(addon.getSetting("viewMode"))

def index():
        xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_LABEL)
        addDir(translation(30001),"",'enMain',"")
        content = getUrl("http://www.loyalbooks.com/language-menu")
        content = content[content.find('<table class="link" summary="All Languages">'):]
        content = content[content.find('<tr>'):]
        content = content[:content.find('</table>')]
        match=re.compile('<td class="link menu"><a href="(.+?)"><div id="(.+?)" class="l-s s-desk"></div>(.+?)</a></td>', re.DOTALL).findall(content)
        for url,uid, title in match:
          addDir(title,"http://www.loyalbooks.com/"+url+"?results=100",'listEbooks',"")
        xbmcplugin.endOfDirectory(pluginhandle)
        if forceViewMode=="true":
          xbmc.executebuiltin('Container.SetViewMode('+viewMode+')')

def enMain():
        addDir(translation(30002),"http://www.loyalbooks.com/Top_100",'listEbooks',"")
        content = getUrl("http://www.loyalbooks.com/genre-menu")
        content = content[content.find('<table class="link" summary="All Genres">'):]
        content = content[content.find('<tr>'):]
        content = content[:content.find('</table>')]
        match=re.compile('<td class="link menu"><a href="(.+?)"><div id="(.+?)" class="g-s s-desk"></div>(.+?)</a></td>', re.DOTALL).findall(content)
        for url, uid, title in match:
          addDir(title,"http://www.loyalbooks.com/"+url+"?results=100",'listEbooks',"")
        xbmcplugin.endOfDirectory(pluginhandle)
        if forceViewMode=="true":
          xbmc.executebuiltin('Container.SetViewMode('+viewMode+')')

def listEbooks(url):
        content = getUrl(url)
        contentPage = content[content.find('<div class="result-pages">'):]
        contentPage = contentPage[:contentPage.find('</ul></div></div>')]
        spl=content.split('<td class="layout2-blue"')
        for i in range(1,len(spl),1):
            entry=spl[i]
            if "alt=" in entry:
              match=re.compile('alt="(.+?)"', re.DOTALL).findall(entry)
              title=match[0]
              title=cleanTitle(title)
              match=re.compile('href="(.+?)"', re.DOTALL).findall(entry)
              url="http://www.loyalbooks.com/"+match[0]
              match=re.compile('src="(.+?)"', re.DOTALL).findall(entry)
              thumb="http://www.loyalbooks.com/"+match[0]
              addDir(title,url+"/feed",'listChapters',thumb)
        match=re.compile('<a href="(.+?)">(.+?)</a>', re.DOTALL).findall(contentPage)
        for url, title in match:
          if title==">":
            addDir(translation(30003),"http://www.loyalbooks.com/"+url,'listEbooks',"")
        xbmcplugin.endOfDirectory(pluginhandle)
        if forceViewMode=="true":
          xbmc.executebuiltin('Container.SetViewMode('+viewMode+')')

def listChapters(url):
        content = getUrl(url)
        match=re.compile('<channel>(.+?)</channel>', re.DOTALL).findall(content)
        content=match[0]
        spl=content.split('<item>')
        for i in range(1,len(spl),1):
            entry=spl[i]
            match=re.compile('<title>(.+?)</title>', re.DOTALL).findall(entry)
            title=match[0]
            title=cleanTitle(title)
            match=re.compile('<enclosure url="(.+?)"', re.DOTALL).findall(entry)
            url=match[0]
            match=re.compile('<itunes:author>(.+?)</itunes:author>', re.DOTALL).findall(entry)
            author=match[0]
            author=cleanTitle(author)
            match=re.compile('<itunes:duration>(.+?)</itunes:duration>', re.DOTALL).findall(entry)
            duration=match[0]
            duration=cleanTime(duration)
            addLink(title,url,'playAudio',"", duration, author)
        xbmcplugin.endOfDirectory(pluginhandle)
        if forceViewMode=="true":
          xbmc.executebuiltin('Container.SetViewMode('+viewMode+')')

def playAudio(url):
        listitem = xbmcgui.ListItem(path=url)
        return xbmcplugin.setResolvedUrl(pluginhandle, True, listitem)

def cleanTitle(title):
        title=title.replace("&lt;","<").replace("&gt;",">").replace("&amp;","&").replace("&#8217;","'").replace("&#8211;","-").replace("&#039;","'").replace("&quot;","\"").replace("&szlig;","ß").replace("&ndash;","-")
        title=title.replace("&Auml;","Ä").replace("&Uuml;","Ü").replace("&Ouml;","Ö").replace("&auml;","ä").replace("&uuml;","ü").replace("&ouml;","ö")
        title=title.replace("<![CDATA[","").replace("]]>","")
        title=title.strip()
        return title

def cleanTime(time):
        timetemp=time.split(':')
        time=int(timetemp[0]) * 60 + int(timetemp[1])
        return time

def getUrl(url):
        req = urllib2.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; rv:18.0) Gecko/20100101 Firefox/18.0')
        response = urllib2.urlopen(req)
        link=response.read()
        response.close()
        return link

def parameters_string_to_dict(parameters):
        ''' Convert parameters encoded in a URL to a dict. '''
        paramDict = {}
        if parameters:
            paramPairs = parameters[1:].split("&")
            for paramsPair in paramPairs:
                paramSplits = paramsPair.split('=')
                if (len(paramSplits)) == 2:
                    paramDict[paramSplits[0]] = paramSplits[1]
        return paramDict

def addLink(name,url,mode,iconimage,dur,auth):
        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)
        ok=True
        liz=xbmcgui.ListItem(name, iconImage="DefaultAudio.png", thumbnailImage=iconimage)
        liz.setInfo( type="music", infoLabels={ "Title": name , "duration": dur ,"artist":auth } )
        liz.setProperty('IsPlayable', 'true')
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz)
        return ok

def addDir(name,url,mode,iconimage):
        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)
        ok=True
        liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
        liz.setInfo( type="music", infoLabels={ "Title": name } )
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
        return ok

params=parameters_string_to_dict(sys.argv[2])
mode=params.get('mode')
url=params.get('url')
if type(url)==type(str()):
  url=urllib.unquote_plus(url)

if mode == 'enMain':
    enMain()
elif mode == 'otherMain':
    otherMain()
elif mode == 'listEbooks':
    listEbooks(url)
elif mode == 'listChapters':
    listChapters(url)
elif mode == 'playAudio':
    playAudio(url)
else:
    index()
