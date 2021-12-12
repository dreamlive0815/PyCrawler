

import os
import requests
import re

downloadDir = './download'
def getDownloadFullPath(path):
    return os.path.join(downloadDir, path)

def makeDir(dirPath):
    if not os.path.exists(dirPath):
        os.makedirs(dirPath)

makeDir(getDownloadFullPath('quantu'))

class Quantu():

    pageHost = 'q.quantuwang1.com'

    def __init__(self) -> None:
        pass

    def getPageFullUrl(self, uri):
        if uri.startswith('http://'):
            return uri
        if not uri.startswith('/'):
            uri = '/{}'.format(uri)
        return 'http://{}{}'.format(__class__.pageHost, uri)

    def getAlbumListInfo(self, albumListPageUri):
        fullUrl = self.getPageFullUrl(albumListPageUri)
        resp = requests.get(fullUrl, timeout = 2)
        resp.encoding = 'utf-8'
        text = resp.text
        match = re.search(r'<div class="index_middle_c">[\s\S]+?</ul>', text)
        if not match:
            raise Exception('找不到图集列表 albumListPageUri={}'.format(albumListPageUri))
        ul = match.group()
        lis = re.findall(r'href="(.+?)".+?img src="(.+?)".+?<span>(.+?)</span>', ul)
        girlName = re.search(r'<li class="h3on">(.+?)</li>', text).group(1)
        albumList = []
        for li in lis:
            album = {
                'girlName': girlName,
                'pageUrl': self.getPageFullUrl(li[0]),
                'coverUrl': li[1],
                'title': li[2], 
            }
            albumList.append(album)
        pageIndexesText = re.search(r'<div class="list_page">(.+?)</div>', text).group(1)
        curIndex = int(re.search(r'<span>(\d+)</span>', pageIndexesText).group(1))
        pageIndexes = re.findall(r'href="(.+?)">(\d+)', pageIndexesText)
        hasNextPage = False
        nextPageUrl = None
        for pageIndex in pageIndexes:
            pageUrl = self.getPageFullUrl(pageIndex[0])
            index = int(pageIndex[1])
            if index == curIndex + 1:
                hasNextPage = True
                nextPageUrl = pageUrl
                break
        r = {
            'girlName': girlName,
            'curIndex': curIndex,
            'hasNext': hasNextPage,
            'nextPageUrl': nextPageUrl,
            'albumList': albumList,
        }
        return r

    def getAlbumDetail(self, albumUri):
        fullUrl = self.getPageFullUrl(albumUri)
        resp = requests.get(fullUrl, timeout = 2)
        resp.encoding = 'utf-8'
        text = resp.text

        match = re.search(r'<div class="index_c_img">[\s\S]+?src="(.+?)"', text)
        if not match:
            raise Exception('找不到图片 albumUri={}'.format(albumUri))
        picUrl = match.group(1)
        mm = re.match(r'^(.+?)[^/]+\.([^/]+)$', picUrl)
        picDirUrl = mm.group(1)
        ext = mm.group(2)
        pageIndexesText = re.search(r'<div class="index_c_page">(.+?)</div>', text).group(1)
        pageIndexes = re.findall(r'>(\d+)</', pageIndexesText)
        pageCount = 0
        for pageIndex in pageIndexes:
            index = int(pageIndex)
            pageCount = max(pageCount, index)
        picUrlList = []
        for i in range(pageCount):
            picUrl = '{}{}.{}'.format(picDirUrl, i + 1, ext)
            picUrlList.append(picUrl)
        r = {
            'picCount': pageCount,
            'picUrlList': picUrlList,
        }
        return r

    def downloadAlbum(self, albumInfo):
        print('start download album named ' + albumInfo['title'])
        albumDetail = self.getAlbumDetail(albumInfo['pageUrl'])
        def filterStr(str):
            str = str.replace('/', ' ')
            return str
        girlName = filterStr(albumInfo['girlName'])
        title = filterStr(albumInfo['title'])
        dirPath = getDownloadFullPath('quantu/{}/{}/'.format(girlName, title))
        if os.path.exists(dirPath):
            print('{} already exists, skip download'.format(dirPath))
            return
        makeDir(dirPath)
        urlList = albumDetail['picUrlList']
        for i in range(len(urlList)):
            url = urlList[i]
            fileName = re.match(r'^.+?([^/]+)$', url).group(1)
            fullFilePath = dirPath + fileName
            print('downloading {} -->> {}'.format(url, fullFilePath))
            try:
                r = requests.get(url, timeout = 2)
                with open(fullFilePath, 'wb') as f:
                    f.write(r.content)
            except:
                print('download {} failed'.format(url))

    def downloadAll(self, firstAlbumListPageUri):
        pageUri = firstAlbumListPageUri
        while True:
            albumListInfo = self.getAlbumListInfo(pageUri)
            albumList = albumListInfo['albumList']
            for album in albumList:
                crawler.downloadAlbum(album)
            if albumListInfo['hasNext']:
                pageUri = albumListInfo['nextPageUrl']
            else:
                break
        print('finished')



crawler = Quantu()
crawler.downloadAll('/t/48bada5e7225ec9f.html')

