#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
if sys.version[0] != '3':
	print('Please use python version 3')
	sys.exit(2)

from subprocess import call
from urllib.request import *
from urllib.parse import quote_plus
from json import loads
from re import search
from html.parser import HTMLParser
import argparse

parser = argparse.ArgumentParser(description='This is a script to retrieve data from metal-archives.com', prog='getMetalArchivesInfo')
parser.add_argument('-f', '--file', nargs=1, type=str, help='File with a list of data seperated via newline, if no file is present it falls back to an interactive mode, where the user can insert his query data (default bandList)', default='bandList', action='store')
parser.add_argument('-t', '--type', nargs=1, type=str, help='Type of query (default band)', default='band', action='store', choices=['album', 'band', 'song'])
parser.add_argument('-o', '--output', nargs=1, type=str, help='If you want the output in an extra csv-file (data.csv) (default cli)', default='cli', action='store', choices=['cli', 'file'])
parser.add_argument('-d', '--discography', nargs=1, type=str, help='If you want to search for the discography of one band (default no)', default='no', action='store', choices=['no', 'yes'])
args = parser.parse_args()

ALBUM_TYPE = 'album'
BAND_TYPE = 'band'
DISCO_TYPE = 'disco'
FILE_TYPE = 'file'
SONG_TYPE = 'song'

QUERY_STRINGS = {
	ALBUM_TYPE: 'http://www.metal-archives.com/search/ajax-album-search/?field=name&query=',
	BAND_TYPE: 'http://www.metal-archives.com/search/ajax-band-search/?field=name&query=',
	DISCO_TYPE: 'http://www.metal-archives.com/band/discography/id/',
	SONG_TYPE: 'http://www.metal-archives.com/search/ajax-song-search/?field=title&query='
	}

#arguments of cli will be put into a list, default arguments will be given as a string
def getFirstString(element):
	if len(element) == 1:
		return element[0]
	else:
		return element

DATA_LIST = getFirstString(args.file)
TYPE = getFirstString(args.type)
FILE_OUTPUT = getFirstString(args.output)
DISCO_SEARCH = getFirstString(args.discography)
OUTPUT_FILE = 'data.csv'

DATA_COUNT = 'iTotalRecords'
DATA_DATA = 'aaData'
ID_REGEX = '\d+'
QUERY_REGEX = '">.*</a'
ERROR_MSG = 'error'
TYPE_STRING = {
	'album': "Band\tAlbum\tType\tDate",
	'band': "Band\tCountry\tGenre",
	'disco': "Titel\tType\tYear\tRating",
	'song': "Artist\tAlbum\tType\tTitle"
}
URL_REGEX = 'href=".*"'

COUNTRY_DICT = { 'Andorra': 'AD', 'United Arab Emirates': 'AE', 'Afghanistan': 'AF', 'Antigua and Barbuda': 'AG',
'Anguilla': 'AI', 'Albania': 'AL', 'Armenia': 'AM', 'Angola': 'AO', 'Antarctica': 'AQ','Argentina': 'AR',
'American Samoa': 'AS', 'Austria': 'AT', 'Australia': 'AU', 'Aruba': 'AW', 'Åand Islands': 'AX',
'Azerbaijan': 'AZ', 'Bosnia and Herzegovina': 'BA', 'Barbados': 'BB', 'Bangladesh': 'BD', 'Belgium': 'BE',
'Burkina Faso': 'BF','Bulgaria': 'BG', 'Bahrain': 'BH', 'Burundi': 'BI', 'Benin': 'BJ','Saint Barthémy': 'BL',
'Bermuda': 'BM', 'Brunei Darussalam': 'BN', 'Bolivia, Plurinational State of': 'BO', 'Bonaire, Sint Eustatius and Saba': 'BQ',
'Brazil': 'BR', 'Bahamas': 'BS', 'Bhutan': 'BT', 'Bouvet Island': 'BV', 'Botswana': 'BW', 'Belarus': 'BY',
'Belize': 'BZ', 'Canada': 'CA', 'Cocos (Keeling) Islands': 'CC','Congo, the Democratic Republic of the': 'CD', 'Central African Republic': 'CF',
'Congo': 'CG', 'Switzerland': 'CH', 'Côd\'Ivoire': 'CI', 'Cook Islands': 'CK', 'Chile': 'CL', 'Cameroon': 'CM',
'China': 'CN', 'Colombia': 'CO', 'Costa Rica': 'CR', 'Cuba': 'CU', 'Cape Verde': 'CV', 'Curaç': 'CW',
'Christmas Island': 'CX', 'Cyprus': 'CY', 'Czech Republic': 'CZ', 'Germany': 'DE', 'Djibouti': 'DJ', 
'Denmark': 'DK', 'Dominica': 'DM', 'Dominican Republic': 'DO', 'Algeria': 'DZ', 'Ecuador': 'EC', 'Estonia': 'EE',
'Egypt': 'EG', 'Western Sahara': 'EH', 'Eritrea': 'ER', 'Spain': 'ES', 'Ethiopia': 'ET', 'Finland': 'FI', 'Fiji': 'FJ',
'Falkland Islands (Malvinas)': 'FK', 'Micronesia, Federated States of': 'FM', 'Faroe Islands': 'FO', 'France': 'FR',
'Gabon': 'GA', 'United Kingdom': 'GB', 'Grenada': 'GD', 'Georgia': 'GE', 'French Guiana': 'GF', 'Guernsey': 'GG',
'Ghana': 'GH', 'Gibraltar': 'GI', 'Greenland': 'GL', 'Gambia': 'GM', 'Guinea': 'GN', 'Guadeloupe': 'GP', 'Equatorial Guinea': 'GQ',
'Greece': 'GR', 'South Georgia and the South Sandwich Islands': 'GS', 'Guatemala': 'GT', 'Guam': 'GU', 'Guinea-Bissau': 'GW',
'Guyana': 'GY', 'Hong Kong': 'HK', 'Heard Island and McDonald Islands': 'HM', 'Honduras': 'HN', 'Croatia': 'HR',
'Haiti': 'HT', 'Hungary': 'HU', 'Indonesia': 'ID', 'Ireland': 'IE', 'Israel': 'IL', 'Isle of Man': 'IM',
'India': 'IN', 'British Indian Ocean Territory': 'IO', 'Iraq': 'IQ', 'Iran, Islamic Republic of': 'IR', 'Iceland': 'IS',
'Italy': 'IT', 'Jersey': 'JE', 'Jamaica': 'JM', 'Jordan': 'JO', 'Japan': 'JP', 'Kenya': 'KE', 'Kyrgyzstan': 'KG',
'Cambodia': 'KH', 'Kiribati': 'KI', 'Comoros': 'KM', 'Saint Kitts and Nevis': 'KN', 'Korea, Democratic People\'s Republic of': 'KP',
'Korea, Republic of': 'KR', 'Kuwait': 'KW', 'Cayman Islands': 'KY', 'Kazakhstan': 'KZ', 'Lao People\'s Democratic Republic': 'LA',
'Lebanon': 'LB', 'Saint Lucia': 'LC', 'Liechtenstein': 'LI', 'Sri Lanka': 'LK', 'Liberia': 'LR', 'Lesotho': 'LS',
'Lithuania': 'LT', 'Luxembourg': 'LU', 'Latvia': 'LV', 'Libya': 'LY', 'Morocco': 'MA', 'Monaco': 'MC',
'Moldova, Republic of': 'MD', 'Montenegro': 'ME', 'Saint Martin (French part)': 'MF', 'Madagascar': 'MG', 'Marshall Islands': 'MH',
'Macedonia, the former Yugoslav Republic of': 'MK', 'Mali': 'ML', 'Myanmar': 'MM', 'Mongolia': 'MN', 'Macao': 'MO', 'Northern Mariana Islands': 'MP',
'Martinique': 'MQ', 'Mauritania': 'MR', 'Montserrat': 'MS', 'Malta': 'MT', 'Mauritius': 'MU', 'Maldives': 'MV', 'Malawi': 'MW', 'Mexico': 'MX',
'Malaysia': 'MY', 'Mozambique': 'MZ', 'Namibia': 'NA', 'New Caledonia': 'NC', 'Niger': 'NE', 'Norfolk Island': 'NF', 'Nigeria': 'NG',
'Nicaragua': 'NI', 'Netherlands': 'NL', 'Norway': 'NO', 'Nepal': 'NP', 'Nauru': 'NR', 'Niue': 'NU', 'New Zealand': 'NZ',
'Oman': 'OM', 'Panama': 'PA', 'Peru': 'PE', 'French Polynesia': 'PF', 'Papua New Guinea': 'PG', 'Philippines': 'PH', 'Pakistan': 'PK',
'Poland': 'PL', 'Saint Pierre and Miquelon': 'PM', 'Pitcairn': 'PN', 'Puerto Rico': 'PR', 'Palestine, State of': 'PS',
'Portugal': 'PT', 'Palau': 'PW', 'Paraguay': 'PY', 'Qatar': 'QA', 'Réion': 'RE', 'Romania': 'RO', 'Serbia': 'RS',
'Russia': 'RU', 'Russian Federation': 'RU', 'Rwanda': 'RW',  'Saudi Arabia': 'SA', 'Solomon Islands': 'SB',
'Seychelles': 'SC', 'Sudan': 'SD', 'Sweden': 'SE', 'Singapore': 'SG', 'Saint Helena, Ascension and Tristan da Cunha': 'SH',
'Slovenia': 'SI', 'Svalbard and Jan Mayen': 'SJ', 'Slovakia': 'SK', 'Sierra Leone': 'SL', 'San Marino': 'SM','Senegal': 'SN',
'Somalia': 'SO', 'Suriname': 'SR', 'South Sudan': 'SS', 'Sao Tome and Principe': 'ST', 'El Salvador': 'SV', 'Sint Maarten (Dutch part)': 'SX',
'Syrian Arab Republic': 'SY', 'Swaziland': 'SZ', 'Turks and Caicos Islands': 'TC', 'Chad': 'TD', 'French Southern Territories': 'TF',
'Togo': 'TG', 'Thailand': 'TH', 'Tajikistan': 'TJ', 'Tokelau': 'TK', 'Timor-Leste': 'TL', 'Turkmenistan': 'TM',
'Tunisia': 'TN', 'Tonga': 'TO', 'Turkey': 'TR', 'Trinidad and Tobago': 'TT', 'Tuvalu': 'TV', 'Taiwan, Province of China': 'TW',
'Tanzania, United Republic of': 'TZ', 'Ukraine': 'UA', 'Uganda': 'UG', 'United States Minor Outlying Islands': 'UM', 'United States': 'US',
'Uruguay': 'UY', 'Uzbekistan': 'UZ', 'Holy See (Vatican City State)': 'VA', 'Saint Vincent and the Grenadines': 'VC', 'Venezuela, Bolivarian Republic of': 'VE',
'Virgin Islands, British': 'VG', 'Virgin Islands, U.S.': 'VI', 'Viet Nam': 'VN', 'Vanuatu': 'VU', 'Wallis and Futuna': 'WF', 'Samoa': 'WS',
'Yemen': 'YE', 'Mayotte': 'YT', 'South Africa': 'ZA', 'Zambia': 'ZM', 'Zimbabwe': 'ZW'
}

class TableHTMLParser(HTMLParser):
	''' filter coming table for discography data
	'''
	dataCount = 0
	BOUNDARY = 3 
	dataToFind = [[]]

	def handle_data(self, data):
		if (data.find('\\') == -1 and len(data) > 2):
			if (self.dataCount <= self.BOUNDARY):
				self.dataToFind[-1].append(data)
				self.dataCount += 1
			else:
				self.dataToFind.append([data])
				self.dataCount = 1

def normalizeData(data):
	dataData = []
	if TYPE == BAND_TYPE:
		dataData = normalizeBandData(data.get(DATA_DATA))
	elif TYPE == ALBUM_TYPE:
		dataData = normalizeAlbumData(data.get(DATA_DATA))
	elif TYPE == SONG_TYPE:
		dataData = normalizeSongData(data.get(DATA_DATA))
	return dataData

def normalizeBandData(bandList):
	newBandList = []
	for each in bandList:
		#re.search
		bandName = search(QUERY_REGEX, each[0]).group()
		bandCountry = COUNTRY_DICT.get(each[2])
		if (each[2] in COUNTRY_DICT):
			bandCountry = COUNTRY_DICT[each[2]]
		else:
			bandCountry = each[2]
		
		if (each[1].find(',') > 0):
			bandGenre = each[1].split(',')[0]
		elif (each[1].find('/') > 0):
			bandGenre = each[1].split('/')[0]
		else:
			bandGenre = each[1]

		newBandList.append([bandName[2:-3], bandCountry, bandGenre])
	return newBandList

def normalizeAlbumData(albumList):
	newAlbumList = []
	for each in albumList:
		#re.search
		albumBand = search(QUERY_REGEX, each[0]).group()
		albumName = search(QUERY_REGEX, each[1]).group()
		albumType = each[2]
		albumDate = each[3]
		albumDateComment = albumDate.find('<')
		newAlbumList.append([albumBand[2:-3], albumName[2:-3], albumType, albumDate[:albumDateComment]])
	return newAlbumList

def normalizeSongData(songList):
	newSongList = []
	for each in songList:
		#re.search
		songBand = search(QUERY_REGEX, each[0]).group()
		songAlbum = search(QUERY_REGEX, each[1]).group()
		songType = each[2]
		songName = each[3]
		newSongList.append([songBand[2:-3], songAlbum[2:-3], songType, songName])
	return newSongList

def outputData(dataList):
	result = ""
	result += TYPE_STRING.get(TYPE) + '\n'
	if TYPE == BAND_TYPE:
		for each in dataList:
			result += '\t'.join((each[0], each[1], each[2])) + '\n'
	else:
		for each in dataList:
			result += '\t'.join((each[0], each[1], each[2], each[3])) + '\n'
	print(result[:-1])

	if FILE_OUTPUT == FILE_TYPE:
		with open(OUTPUT_FILE, mode='w', encoding='utf8') as outputFile:
			outputFile.write(result)

def getURL(urlString):
	return search(URL_REGEX, urlString).group()[6:-1]

def numberCheck(numberString, minNum, maxNum):
	if (numberString.isdigit() and int(numberString) <= maxNum and int(numberString) > minNum):
		return True
	else:
		return False

def stripID(searchString):
	#re.search
	return search(ID_REGEX, searchString).group()

def narrowSearch():
	bandName = input('Please insert the band you are searching the discography for: ')
	band = []
	if (bandName != ''):
		response = urlopen(QUERY_STRINGS.get(BAND_TYPE)+ quote_plus(bandName))
		content = response.read()
		data = loads(content.decode('utf8'))
			
		error = data.get(ERROR_MSG)
		if (error != ""):
			print("Error recieved: " + error)
			sys.exit(1)

		dataCount = data.get(DATA_COUNT)
		if (dataCount == 0):
			print('No data found: ' + bandName)
		elif (dataCount == 1):
			founddata = normalizeData(data)[0]
			print('Found one ' + founddata[0])
			founddata.append(stripID(data.get(DATA_DATA)[0][0]))
			band.append(founddata)
		else:
			dataData = normalizeData(data)
			choice = 'n'
			while (choice == 'n'):
				i = 1
				TYPE = BAND_TYPE
				print('#\t' + TYPE_STRING.get(TYPE))
				for multidata in dataData:
					print('\t'.join((str(i), multidata[0], multidata[1], multidata[2])))
					i += 1

				choice = input('Data lookup or choice (multiple numbers for lookup, ' ' seperator) ')
				if (choice.find(' ') == -1):
					if (numberCheck(choice, 0, len(dataData))):
						band.append(dataData[int(choice)-1])
					else:
						print('No number or out of range' + choice)
						pass
				else:
					numbers = choice.split(" ")
					numbersToLookup = []
					for number in numbers:
						if (numberCheck(number, 0, len(dataData))):
							numbersToLookup.append(int(number))
						else:
							print('No number or out of range:' + number)
					callList = ['firefox']
					dataRawData = data.get(DATA_DATA)
					for number in numbersToLookup:
						urlString = getURL(dataRawData[number-1][0])
						callList.append('-new-tab')
						callList.append(urlString)
					call(callList)
				
				choice = input('Done? [y]')
		TYPE = DISCO_TYPE
		for each in band:
			print(each)
			response = urlopen(QUERY_STRINGS.get(TYPE) + each[0][3])
			content = response.read()
			htmlParser = TableHTMLParser(strict=False)
			data = htmlParser.feed(str(content))
			outputData(htmlParser.dataToFind[1:])

def wideSearch():
	dataToSearch = []
	try:
		with open(DATA_LIST, encoding='utf8') as dataToSearchFile:
			dataToSearch = dataToSearchFile.readlines()
	except IOError:
		print('No file with data found, starting interactive mode (break with ctrl+c)')
		while True:
			try:
				newData = input('Please insert a ' + TYPE + ' name you want to search for: ')
				if (newData != ""):
					dataToSearch.append(newData)
			except KeyboardInterrupt:
				break
	else:
		pass

	#newline for ctrl+c
	print()

	fulldataList = []
	for candidate in dataToSearch:
		#urllib.request.[ProxyHandler|build_opener|install_opener]
		#proxy = ProxyHandler({'http': 'proxy.intra.dmc.de:3128'})
		#opener = build_opener(proxy)
		#install_opener(opener)

		#urllib.parse.quote_plus, urllib.requests.urlopen and json.loads
		response = urlopen(QUERY_STRINGS.get(TYPE) + quote_plus(candidate))
		content = response.read()
		data = loads(content.decode('utf8'))
			
		error = data.get(ERROR_MSG)
		if (error != ""):
			print("Error recieved: " + error)
			sys.exit(1)

		dataCount = data.get(DATA_COUNT)
		if (dataCount == 0):
			print('No data found: ' + candidate)
		elif (dataCount == 1):
			founddata = normalizeData(data)[0]
			print('Found one ' + founddata[0])
			fulldataList.append(founddata)
		else:
			dataData = normalizeData(data)
			choice = 'n'
			while (choice == 'n'):
				i = 1
				print('#\t' + TYPE_STRING.get(TYPE))
				for multidata in dataData:
					if  TYPE == BAND_TYPE:
						print('\t'.join((str(i), multidata[0], multidata[1], multidata[2])))
					else:
						print('\t'.join((str(i), multidata[0], multidata[1], multidata[2], multidata[3])))
					i += 1

				choice = input('Data lookup or choice (multiple numbers for lookup, ' ' seperator) ')
				if (choice.find(' ') == -1):
					if (numberCheck(choice, 0, len(dataData))):
						fulldataList.append(dataData[int(choice)-1])
					else:
						print('No number or out of range' + choice)
						pass
				else:
					numbers = choice.split(" ")
					numbersToLookup = []
					for number in numbers:
						if (numberCheck(number, 0, len(dataData))):
							numbersToLookup.append(int(number))
						else:
							print('No number or out of range:' + number)
					callList = ['firefox']
					dataRawData = data.get(DATA_DATA)
					for number in numbersToLookup:
						urlString = getURL(dataRawData[number-1][0])
						callList.append('-new-tab')
						callList.append(urlString)
					call(callList)
				
				choice = input('Done? [y]')

	outputData(fulldataList)

def startSearch():
	if DISCO_SEARCH == 'yes':
		TYPE = DISCO_TYPE
		narrowSearch()
	else:
		wideSearch()

if __name__ == '__main__':
	startSearch()
