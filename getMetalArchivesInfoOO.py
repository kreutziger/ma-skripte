#!/usr/bin/python3
# -*- coding: utf-8 -*-

import re
import json
import urllib.parse
import urllib.request
import argparse
from html.parser import HTMLParser
from subprocess import call, getoutput

COUNTRY_DICT = {'Andorra':'AD','United Arab Emirates':'AE',
'Afghanistan':'AF','Antigua and Barbuda':'AG','Anguilla':'AI',
'Albania':'AL','Armenia':'AM','Angola':'AO','Antarctica':'AQ',
'Argentina':'AR','American Samoa':'AS','Austria':'AT','Australia':'AU',
'Aruba':'AW','Azerbaijan':'AZ','Bosnia and Herzegovina':'BA',
'Barbados':'BB','Bangladesh':'BD','Belgium':'BE','Burkina Faso':'BF',
'Bulgaria':'BG','Bahrain':'BH','Burundi':'BI','Benin':'BJ',
'Saint Barthémy':'BL','Bermuda':'BM','Brunei Darussalam':'BN',
'Bolivia':'BO',
'Bonaire, Sint Eustatius and Saba':'BQ','Brazil':'BR','Bahamas':'BS',
'Bhutan':'BT','Bouvet Island':'BV','Botswana':'BW','Belarus':'BY',
'Belize':'BZ','Canada':'CA','Cocos (Keeling) Islands':'CC',
'Congo, the Democratic Republic of the':'CD','Central African Republic':'CF',
'Congo':'CG','Switzerland':'CH','Côd\'Ivoire':'CI','Cook Islands':'CK',
'Chile':'CL','Cameroon':'CM','China':'CN','Colombia':'CO','Costa Rica':'CR',
'Cuba':'CU','Cape Verde':'CV','Christmas Island':'CX','Cyprus':'CY',
'Czech Republic':'CZ','Germany':'DE','Djibouti':'DJ','Denmark':'DK',
'Dominica':'DM','Dominican Republic':'DO','Algeria':'DZ','Ecuador':'EC',
'Estonia':'EE','Egypt':'EG','Western Sahara':'EH','Eritrea':'ER','Spain':'ES',
'Ethiopia':'ET','Finland':'FI','Fiji':'FJ','Falkland Islands (Malvinas)':'FK',
'Micronesia, Federated States of':'FM','Faroe Islands':'FO','France':'FR',
'Gabon':'GA','United Kingdom':'GB','Grenada':'GD','Georgia':'GE',
'French Guiana':'GF','Guernsey':'GG','Ghana':'GH','Gibraltar':'GI',
'Greenland':'GL','Gambia':'GM','Guinea':'GN','Guadeloupe':'GP',
'Equatorial Guinea':'GQ','Greece':'GR',
'South Georgia and the South Sandwich Islands':'GS','Guatemala':'GT',
'Guam':'GU','Guinea-Bissau':'GW','Guyana':'GY','Hong Kong':'HK',
'Heard Island and McDonald Islands':'HM','Honduras':'HN','Croatia':'HR',
'Haiti':'HT','Hungary':'HU','Indonesia':'ID','Ireland':'IE','Israel':'IL',
'Isle of Man':'IM','India':'IN','British Indian Ocean Territory':'IO',
'Iraq':'IQ','Iran':'IR','Iceland':'IS','Italy':'IT',
'Jersey':'JE','Jamaica':'JM','Jordan':'JO','Japan':'JP','Kenya':'KE',
'Kyrgyzstan':'KG','Cambodia':'KH','Kiribati':'KI','Comoros':'KM',
'Saint Kitts and Nevis':'KN','Korea, North':'KP',
'Korea, South':'KR','Kuwait':'KW','Cayman Islands':'KY',
'Kazakhstan':'KZ','Lao People\'s Democratic Republic':'LA','Lebanon':'LB',
'Saint Lucia':'LC','Liechtenstein':'LI','Sri Lanka':'LK','Liberia':'LR',
'Lesotho':'LS','Lithuania':'LT','Luxembourg':'LU','Latvia':'LV','Libya':'LY',
'Morocco':'MA','Monaco':'MC','Moldova':'MD', 'Moldova, Republic of':'MD','Montenegro':'ME',
'Saint Martin (French part)':'MF','Madagascar':'MG','Marshall Islands':'MH',
'Macedonia (FYROM)':'MK','Mali':'ML','Myanmar':'MM',
'Mongolia':'MN','Macao':'MO','Northern Mariana Islands':'MP','Martinique':'MQ',
'Mauritania':'MR','Montserrat':'MS','Malta':'MT','Mauritius':'MU'
,'Maldives':'MV','Malawi':'MW','Mexico':'MX','Malaysia':'MY','Mozambique':'MZ',
'Namibia':'NA','New Caledonia':'NC','Niger':'NE','Norfolk Island':'NF',
'Nigeria':'NG','Nicaragua':'NI','Netherlands':'NL','Norway':'NO','Nepal':'NP',
'Nauru':'NR','Niue':'NU','New Zealand':'NZ','Oman':'OM','Panama':'PA',
'Peru':'PE','French Polynesia':'PF','Papua New Guinea':'PG','Philippines':'PH',
'Pakistan':'PK','Poland':'PL','Saint Pierre and Miquelon':'PM','Pitcairn':'PN',
'Puerto Rico':'PR','Palestine, State of':'PS','Portugal':'PT','Palau':'PW',
'Paraguay':'PY','Qatar':'QA','Réion':'RE','Romania':'RO','Serbia':'RS',
'Russia':'RU','Russian Federation':'RU','Rwanda':'RW','Saudi Arabia':'SA',
'SolomonIslands':'SB','Seychelles':'SC','Sudan':'SD','Sweden':'SE',
'Singapore':'SG','Saint Helena, Ascension and Tristan da Cunha':'SH',
'Slovenia':'SI','Svalbard and Jan Mayen': 'SJ','Slovakia':'SK',
'Sierra Leone':'SL','San Marino':'SM','Senegal':'SN','Somalia':'SO',
'Suriname':'SR','South Sudan':'SS','Sao Tome and Principe': 'ST',
'El Salvador':'SV','Sint Maarten (Dutch part)':'SX',
'Syria':'SY','Swaziland':'SZ','Turks and Caicos Islands':'TC',
'Chad':'TD','French Southern Territories':'TF','Togo':'TG','Thailand':'TH',
'Tajikistan':'TJ','Tokelau':'TK','Timor-Leste':'TL','Turkmenistan':'TM',
'Tunisia':'TN','Tonga':'TO','Turkey':'TR','Trinidad and Tobago':'TT',
'Tuvalu':'TV','Taiwan':'TW','Taiwan, Province of China':'TW',
'Tanzania, United Republic of':'TZ','Ukraine':'UA','Uganda':'UG',
'United States Minor Outlying Islands':'UM','United States':'US', 'Unknown':'--','Uruguay':'UY',
'Uzbekistan':'UZ','Holy See (Vatican City State)':'VA',
'Saint Vincent and the Grenadines':'VC',
'Venezuela':'VE',
'Virgin Islands, British': 'VG','Virgin Islands, U.S.':'VI','Viet Nam':'VN',
'Vanuatu':'VU','Wallis and Futuna':'WF','Samoa':'WS','Yemen':'YE',
'Mayotte':'YT','South Africa':'ZA','Zambia':'ZM','Zimbabwe':'ZW',
'International':'INT'
}

class Regex():
    pattern = ''
    result  = ''

    ID_REGEX = '/\d+'
    DATE_REGEX = '\d{4}'
    NAME_REGEX = '">.*</a'
    URL_REGEX = 'href=".*"'

    def __init__(self, pattern='.*'):
        self.pattern = pattern

    def search(self, searchString):
        self.result = re.search(self.pattern, searchString).group()
        if (self.NAME_REGEX == self.pattern):
            self.result = self.result[2:-3]
        elif (self.URL_REGEX == self.pattern):
            self.result = self.result[6:-1]
        elif (self.ID_REGEX == self.pattern):
            self.result = self.result[1:]
        return self.result

class DiscoHTMLParser(HTMLParser):
    dataToFind = []
    tr = False
    body = False
    onlyA = False

    def handle_starttag(self, tag, attrs):
        if ('tr' == tag):
            self.tr = True
            self.onlyA = True
            if (self.body):
                self.dataToFind.append([])
        if ('tbody' == tag):
            self.body = True
        if (self.onlyA and 'a' == tag):
            self.onlyA = False
            self.dataToFind[-1].append(attrs[0][1])

    def handle_endtag(self, tag):
        if ('tr' == tag):
            self.tr = False
            if (0 < len(self.dataToFind)):
                tmp = self.dataToFind[-1]
                if (5 < len(tmp)):
                    tmp.pop(4)
                    self.dataToFind[-1] = tmp

    def handle_data(self, htmlData):
        data = htmlData.replace('\\n', '').replace('\\t', '')
        data = htmlData.replace('\n', '').replace('\t', '')
        if (len(data) > 0 and self.body and self.tr):
            self.dataToFind[-1].append(data)

    def clearResults(self):
        self.dataToFind = []
        self.tr = False
        self.body = False

class EntityList():
    headerList = []
    queryString = ''
    extra = ''
    listEntries = []
    logoHost = 'http://www.metal-archives.com'
    logoDir = '/images'
    logoExtension = ''
    logoFileType = ['.jpg','.jpeg','.gif','.png','.JPG','.JPEG','.GIF','.PNG']

    def __init__(self, listEntries):
        self.listEntries = listEntries

    def addEntry(self, Entity):
        self.listEntries.append(Entity)

    def headers(self):
        return headerList

    def createLogoID(self, entityID):
        '''
        examples:
        album:
        http://www.metal-archives.com/images/3/9/4/8/394846.jpg
        band:
        http://www.metal-archives.com/images/1/0/0/0/100000_logo.jpg

        '''
        result = self.logoHost + self.logoDir
        try:
            tmp = list(str(entityID))
            for i in range(0, 4):
                result += '/' + tmp.pop(0)
        except IndexError:
            pass
        result += '/' + entityID + self.logoExtension
        for each in self.logoFileType:
            returnCode = getoutput('curl -Is ' + result + each + \
                '  | grep HTTP')
            if (-1 < returnCode.find('200')):
                return result + each
        return result

    def printOut(self, sep='\t', fileName=None, linkAddress=False):
        result = ''
        result += sep.join(self.headerList) + '\n'
        for each in self.listEntries:
            result += each.output(sep) + '\n'
            if (linkAddress):
                result += self.createLogoID(each.entityID) \
                    + '\n'
    
        if (None != fileName):
            try:
                with open(fileName, mode='w', \
                    encoding='utf8') as fileToWrite:
                     fileToWrite.write(result)
            except IOError:
                print('could not write to file')

        return result

class ArtistList(EntityList):
    headerList = ['Band', 'Country', 'Genre']
    queryString = 'http://www.metal-archives.com/search/ajax-band-' + \
            'search/?field=name&query='
    logoExtension = '_logo'

class AlbumList(EntityList):
    headerList = ['Band', 'Album', 'Type', 'Year']
    queryString = 'http://www.metal-archives.com/search/ajax-album-' + \
            'search/?field=name&query='

class SongList(EntityList):
    headerList = ['Artist', 'Album', 'Title']
    queryString = 'http://www.metal-archives.com/search/ajax-song-' + \
            'search/?field=title&query='
    
class DiscoList(EntityList):
    headerList = ['Name', 'Type', 'Year', 'Rating']
    queryString= 'http://www.metal-archives.com/band/discography/id/'
    extra = '/tab/all'

class Entity():
    def output(self, sep='\t'):
        pass

    def normalize(self, listOfData):
        pass

class ArtistEntity(Entity):
    def __init__(self, name='', country='', genre='', entityID=0, \
            albumList = AlbumList([])):
        self.name = name
        self.country = country
        self.genre = genre
        self.entityID = entityID
        self.albumList = albumList

        self.regex = Regex()

    def normalize(self, maSearcherResult):
        self.regex.pattern = Regex.ID_REGEX
        self.entityID = self.regex.search(maSearcherResult[0])
        self.regex.pattern = Regex.NAME_REGEX
        self.name = self.regex.search(maSearcherResult[0])
        self.genre = maSearcherResult[1]
        self.country = maSearcherResult[2]

    def output(self, sep='\t'):
        try:
            return sep.join([self.name, COUNTRY_DICT.get(self.country), \
            self.genre])
        except TypeError:
            print('did not find: {0}'.format(self.country))
            return sep.join([self.name, '--'])

class AlbumEntity(Entity):
    #def __init__(self, albumType='', artist=ArtistEntity(), name='', \
    def __init__(self, albumType='', artist='', name='', \
            rating='', year='', songs=SongList([]), \
            entityID=0):
        self.albumType = albumType
        self.artist = artist
        self.name = name
        self.rating = rating
        self.year = year
        self.songs = songs
        self.entityID = entityID

        self.regex = Regex()

    def normalize(self, maSearcherResult):
        self.albumType = maSearcherResult[2]
        self.regex.pattern = Regex.NAME_REGEX
        self.artist = self.regex.search(maSearcherResult[0])
        self.name = self.regex.search(maSearcherResult[1])
        self.regex.pattern = Regex.DATE_REGEX
        self.year = self.regex.search(maSearcherResult[3])
        self.regex.pattern = Regex.ID_REGEX
        self.entityID = self.regex.search(maSearcherResult[1])

    def output(self, sep='\t'):
        #return sep.join([self.artist.name, self.name, self.albumType, \
        return sep.join([self.artist, self.name, self.albumType, \
             self.year])

class DiscoEntity(Entity):
    def __init__(self, albumType='', artist='', name='', entityID=0, \
            rating='', year='', songs=SongList([])):
        self.albumType = albumType
        self.artist = artist
        self.name = name
        self.rating = rating
        self.year = year
        self.entityID = entityID

    def output(self, sep='\t'):
        return sep.join([self.name, self.albumType, self.year, \
            self.rating])

class SongEntity(Entity):
    #def __init__(self, track=0, title='', album=AlbumEntity()):
    def __init__(self, track=0, title='', album='', artist=''):
        self.track = track
        self.title = title
        self.album = album
        self.artist = artist

        self.regex = Regex()

    def normalize(self, maSearcherResult):
        self.regex.pattern = Regex.NAME_REGEX
        self.album = self.regex.search(maSearcherResult[1])
        self.artist = self.regex.search(maSearcherResult[0])
        self.title = maSearcherResult[3]

    def output(self, sep='\t'):
        #return sep.join([self.album.artist.name, self.album.name, \
        return sep.join([self.artist, self.album, self.title])

class MASearcher():
    RECORD_COUNT = 'iTotalRecords'
    DATA = 'aaData'
    ERROR_MSG = 'error'

    queryURL = ''
    extraURL = ''
    searchTerm = ''
    resultList = []
    rawData = {}
    error = ''
    dataCount = 0

    def __init__(self, queryURL='', extraURL=''):
        self.queryURL = queryURL
        self.extraURL = extraURL

    def getQuery(self, searchTerm):
        response = urllib.request.urlopen(self.queryURL + \
            urllib.parse.quote_plus(searchTerm) + self.extraURL)
        content = response.read()
        self.rawData = json.loads(content.decode('utf8'))
        self.error = self.rawData.get(MASearcher.ERROR_MSG)
        self.resultList = self.rawData.get(MASearcher.DATA)
        self.dataCount = self.rawData.get(MASearcher.RECORD_COUNT)

    def getRawQuery(self, searchTerm):
        response = urllib.request.urlopen(self.queryURL + \
            urllib.parse.quote_plus(searchTerm) + self.extraURL)
        return response.read()

class Arguments():
    fileToRead = ''
    queryType = ''
    fileToWrite = ''
    discographyMode = ''
    logos = False

    BAND_TYPE = 'band'
    ALBUM_TYPE = 'album'
    SONG_TYPE = 'song'
    DISCO_TYPE = 'disco'

    def __init__(self):
        parser = argparse.ArgumentParser(description='This is a' + \
            ' script to retrieve data from metal-archives.com',\
             prog='getMetalArchivesInfo')
        parser.add_argument('-f', '--file', nargs=1, type=str, \
            help='File with a list of data seperated via' + \
            ' newline, if no file is present it falls back' + \
            ' to an interactive mode, where the user can insert' + \
            ' his query data', action='store')
        parser.add_argument('-t', '--type', nargs=1, type=str, \
            help='Type of query (default band)', default='band', \
            action='store', choices=['album', 'band', 'disco',\
             'song'])
        parser.add_argument('-o', '--output', nargs=1, type=str, \
            help='If you want the output in an extra csv-file' + \
            ' set this option', action='store')
        parser.add_argument('-l', '--logos', action='store_true', \
            help='Set this option to get the image links of ' + \
            ' the searched entities')
        args = parser.parse_args()

        self.fileToRead = self.getString(args.file)
        self.fileToWrite = self.getString(args.output)
        self.queryType = self.getString(args.type)
        self.logos = args.logos

        if (self.logos and Arguments.SONG_TYPE == self.queryType):
            self.logos = False
            print('-l/--logso works only with -t album/band/disco')

    def getString(self, element):
        if (isinstance(element, list)):
            return element[0]
        else:
            return element

class Engine():
    '''
        dataList = entities to search on metal-archives
        queryList = data for ma search objects which were searched
        entityList = object list to save entities
        entity = object to save entity
    '''
    ar = Arguments()
    dataList = []
    queryList = []
    entityList = None
    entity = Entity()

    def createEntities(self):
        if (None == self.entityList):
            if (Arguments.BAND_TYPE == self.ar.queryType or \
                Arguments.DISCO_TYPE == self.ar.queryType):
            
                self.entityList = ArtistList([])
                self.entity = ArtistEntity()
            elif (Arguments.ALBUM_TYPE == self.ar.queryType):

                self.entityList = AlbumList([])
                self.entity = AlbumEntity()
            elif (Arguments.SONG_TYPE == self.ar.queryType):

                self.entityList = SongList([])
                self.entity = SongEntity()
        else:
            if (Arguments.BAND_TYPE == self.ar.queryType or \
                Arguments.DISCO_TYPE == self.ar.queryType):

                self.entity = ArtistEntity()
            elif (Arguments.ALBUM_TYPE == self.ar.queryType):

                self.entity = AlbumEntity()
            elif (Arguments.SONG_TYPE == self.ar.queryType):

                self.entity = SongEntity()
            
    def start(self):
        self.createEntities()
        self.getSearchData()
        self.queryData()

        if (Arguments.DISCO_TYPE == self.ar.queryType):
            self.getDiscography()
        else:
            print(self.entityList.printOut(fileName=\
                self.ar.fileToWrite,linkAddress=\
                self.ar.logos))

    def numberCheck(self, numberString, minN, maxN):
        try:
            num = int(numberString)
            if (num <= maxN and num > minN):
                return True
            else:
                return False
        except TypeError:
            raise(TypeError)
    
    def multipleChoice(self, maSearcher):
        choice = 'n'
        while 'n' == choice:
            i = 1
            print('{0}\t{1}'.format('#', \
                '\t'.join(self.entityList.headerList)))
            for each in maSearcher.resultList:
                self.entity.normalize(each)
                print('{0}\t{1}'.format(i, \
                    self.entity.output()))
                i += 1

            choice = input('data lookup or choice (' \
                + 'multiple numbers for lookup, " " ' \
                + 'seperator): ')

            maxN = len(maSearcher.resultList)
            try:
                if (choice.find(' ') == -1):
                    if (self.numberCheck(choice, 0, maxN)):
                        result = maSearcher. \
                            resultList[int(choice)-1]
                    else:
                        print('number out ' + \
                            'of range')
                else:
                    numbers = choice.split(' ')
                    numbersToLookup = []
                    for number in numbers:
                        if (self.numberCheck(number, \
                             0, maxN)):
                            numbersToLookup. \
                            append(int(number))
                        else:
                            print('number out ' + \
                                'of range')
                    callList = ['firefox']
                    regex = Regex()
                    regex.pattern = Regex.URL_REGEX
                    for number in numbersToLookup:
                        urlString = regex.search( \
                            maSearcher.resultList \
                            [number-1][0])
                        callList.append('-new-tab')
                        callList.append(urlString)
                    call(callList)
            except TypeError:
                print('no number input')

            choice = input('Done? [y] ')
        return result
        
    def queryData(self):
        for data in self.dataList:
            tmpEntity = self.entity
            ma = MASearcher(self.entityList.queryString, self.entityList.extra)
            ma.getQuery(data)
            if (ma.error == ''):
                if (0 == ma.dataCount):
                    print('{0} not found'.format(data))
                elif (1 == ma.dataCount):
                    print('{0} found'.format(data))
                    ma.resultList = ma.resultList[0]
                    self.queryList.append(ma)
                    self.entity.normalize(ma.resultList)
                    self.entityList.addEntry(self.entity)
                    self.createEntities()
                else:
                    print('do multiple choice for {0}'.format(data))
                    self.queryList.append(ma)
                    self.entity.normalize(self. \
                        multipleChoice(ma))
                    self.entityList.addEntry(self.entity)
                    self.createEntities()
            else:
                print('no data received: ' + ma.error)

    def getSearchData(self):
        if not (self.ar.fileToRead is None):
            try:
                with open(self.ar.fileToRead, encoding='utf8') as \
                    fileInput:
                    self.dataList = fileInput.readlines()
            except IOError:
                print('no file found')
        if not (self.dataList):
            print('starting interactive mode (break with ctrl+c)')
            while True:
                try:
                    newData = input('please insert a ' + \
                        self.ar.queryType + ' name ' \
                        'you want to search for: ')
                    if (newData != ""):
                        self.dataList.append(newData)
                except KeyboardInterrupt:
                    print()
                    break
    def getDiscography(self):
        regex = Regex(Regex().ID_REGEX)
        ma = MASearcher(DiscoList([]).queryString, DiscoList([]).extra)
        #htmlParser = DiscoHTMLParser(strict=False)
        htmlParser = DiscoHTMLParser()
        for each in self.entityList.listEntries:
            print(each.output())
            tmpList = DiscoList([])
            htmlData = ma.getRawQuery(each.entityID)
            htmlParser.feed(htmlData.decode('utf-8'))
            for album in htmlParser.dataToFind:
                tmpEntity = DiscoEntity()
                tmpEntity.entityID = regex.search(album[0])
                tmpEntity.name = album[1]
                tmpEntity.rating = album[4]
                tmpEntity.albumType = album[2]
                tmpEntity.year = album[3]
                tmpList.addEntry(tmpEntity)
            print(tmpList.printOut(fileName=self.ar.fileToWrite, \
                linkAddress=self.ar.logos))
            htmlParser.reset()
            htmlParser.clearResults()

if __name__ == '__main__':
    e = Engine()
    e.start()
