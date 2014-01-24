#!/usr/bin/python3
# -*- coding: utf-8 -*-

import re
import json
import urllib.parse
import urllib.request
import argparse

class EntityList():
	headerList = []
	queryString = ''
	listEntries = []

	def __init__(self, listEntries):
		self.listEntries = listEntries

	def addEntry(self, Entity):
		self.listEntries.append(Entity)

	def printOut(self, sep='\t', fileName=None):
		result = ''
		result += sep.join(self.headerList) + '\n'
		for each in self.listEntries:
			result += each.output(sep) + '\n'
	
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

class AlbumList(EntityList):
	headerList = ['Band', 'Album', 'Type', 'Year', 'Rating']
	queryString = 'http://www.metal-archives.com/search/ajax-album-' + \
			'search/?field=name&query='

class SongList(EntityList):
	headerList = ['Artist', 'Album', 'Track', 'Title']
	queryString = 'http://www.metal-archives.com/search/ajax-song-' + \
			'search/?field=title&query='
	
class Entity():
	def output(self, sep='\t'):
		pass

	def normalize(self, listOfData):
		pass

class ArtistEntity(Entity):
	def __init__(self, name='', country='', genre='', artistID=0, \
			albumList = AlbumList([])):
		self.name = name
		self.country = country
		self.genre = genre
		self.artistID = artistID
		self.albumList = albumList

	def output(self, sep='\t'):
		return sep.join([self.name, self.country, self.genre])

class AlbumEntity(Entity):
	def __init__(self, albumType='', artist=ArtistEntity(), name='', \
			rating='', year='', songs=SongList([])):
		self.albumType = albumType
		self.artist = artist
		self.name = name
		self.rating = rating
		self.year = year
		self.songs = songs

	def output(self, sep='\t'):
		return sep.join([self.artist.name, self.name, self.albumType, \
			 self.year, self.rating])

class SongEntity(Entity):
	def __init__(self, track=0, title='', album=AlbumEntity()):
		self.track = track
		self.title = title
		self.album = album

	def output(self, sep='\t'):
		return sep.join([self.album.artist.name, self.album.name, \
			str(self.track), self.title])

class Regex():
	pattern = ''
	result  = ''

	ID_REGEX = '\d+'
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
		return self.result

class MASearcher():
	RECORD_COUNT = 'iTotalRecords'
	DATA = 'aaData'
	ERROR_MSG = 'error'

	queryURL = ''
	searchTerm = ''
	resultList = []
	rawData = {}
	error = ''
	dataCount = 0

	def __init__(self, queryURL=''):
		self.queryURL = queryURL

	def getQuery(self, searchTerm):
		response = urllib.request.urlopen(self.queryURL + \
			urllib.parse.quote_plus(searchTerm))
		content = response.read()
		self.rawData = json.loads(content.decode('utf8'))
		self.error = self.rawData.get(MASearcher.ERROR_MSG)
		self.resultList = self.rawData.get(MASearcher.DATA)
		self.dataCount = self.rawData.get(MASearcher.RECORD_COUNT)

class Arguments():
	fileToRead = ''
	queryType = ''
	fileToWrite = ''
	discographyMode = ''

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
		args = parser.parse_args()

		self.fileToRead = self.getString(args.file)
		self.fileToWrite = self.getString(args.output)
		self.queryType = self.getString(args.type)

	def getString(self, element):
		if (isinstance(element, list)):
			return element[0]
		else:
			return element

class Engine():
	ar = Arguments()
	dataList = []
	queryList = []
	entityList = EntityList([])
	entity = Entity()

	def start(self):
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
		print('wrumm wrumm...')

		self.getSearchData()
		print('found data to burn')

		self.queryData()
		print('start fueling that stuff')
		
	
	def queryData(self):
		ma = MASearcher(self.entityList.queryString)
		for data in self.dataList:
			tmpEntity = self.entity
			tmpMa = ma
			tmpMa.getQuery(data)
			self.queryList.append(tmpMa)
			if (0 == tmpMa.dataCount):
				print(data + ' not found')
			elif (1 == tmpMa.dataCount):
				print(data + ' found')
			else:
				print(tmpMa.rawData)

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
						self.ar.queryType + ' name you want ' + \
						'to search for: ')
					if (newData != ""):
						self.dataList.append(newData)
				except KeyboardInterrupt:
					print()
					break

if __name__ == '__main__':
	'''al = ArtistList([])
	a = ArtistEntity(name='Marduk', country='sweden', \
		genre='black metal', artistID=386)
	al.addEntry(a)
	ab = AlbumEntity(albumType='Full-Length', artist=a, \
		name='Plague Angel', rating='82%', year='2003')
	abl = AlbumList([])
	abl.addEntry(ab)
	s = SongEntity(track=1, title='Fuck Me Jesus', album=ab)
	sl = SongList([])
	sl.addEntry(s)
	for i in range(0, len(al.listEntries)):
		print(al.listEntries[i].name)

	print(abl.printOut())
	print(al.printOut())
	print(sl.printOut(fileName='asd'))

	r = Regex(Regex.ID_REGEX)
	print(r.search('http://www.metal-archives.com/band/discography/id/' + \
		'43892'))
	r.pattern = Regex.URL_REGEX
	print(r.search('<a href=\"http://www.metal-archives.com/bands/' + \
		'Marduk/29435\">Marduk</a>  <!-- 11.40912 -->'))
	r.pattern = Regex.NAME_REGEX
	print(r.search('<a href=\"http://www.metal-archives.com/bands/' + \
		'Marduk/29435\">Marduk</a>  <!-- 11.40912 -->'))
	'''
	e = Engine()
	e.start()
	try:
		print(e.ar.fileToRead + ' ' + e.ar.fileToWrite)
	except TypeError:
		print('one attribute was not read in')
