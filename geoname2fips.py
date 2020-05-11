#!/usr/bin/env python3
# The MIT License (MIT)
#
# Copyright (c) 2019 Gianluigi Tiesi
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import os
import re
import csv
import argparse
from typing import Pattern
# noinspection PyPackageRequirements
from unidecode import unidecode

from collections import defaultdict

# dataset from: https://github.com/datasets/fips-10-4
# with the help of: https://en.wikipedia.org/wiki/List_of_FIPS_region_codes

# FIPS 10-4 country codes to maxmind country names
FIPS_COUNTRIES = {
    'AFGHANISTAN': 'AF',
    'AKROTIRI SOVEREIGN BASE AREA': 'AX',
    'ALBANIA': 'AL',
    'ALGERIA': 'AG',
    'AMERICAN SAMOA': 'AQ',
    'ANDORRA': 'AN',
    'ANGOLA': 'AO',
    'ANGUILLA': 'AV',
    'ANTARCTICA': 'AY',
    'ANTIGUA AND BARBUDA': 'AC',
    'ARGENTINA': 'AR',
    'ARMENIA': 'AM',
    'ARUBA': 'AA',
    'ASHMORE AND CARTIER ISLANDS': 'AT',
    'AUSTRALIA': 'AS',
    'AUSTRIA': 'AU',
    'AZERBAIJAN': 'AJ',
    'BAHAMAS': 'BF',
    'BAHRAIN': 'BA',
    'BAKER ISLAND': 'FQ',
    'BANGLADESH': 'BG',
    'BARBADOS': 'BB',
    'BASSAS DA INDIA': 'BS',
    'BELARUS': 'BO',
    'BELGIUM': 'BE',
    'BELIZE': 'BH',
    'BENIN': 'BN',
    'BERMUDA': 'BD',
    'BHUTAN': 'BT',
    'BOLIVIA': 'BL',
    'BOSNIA AND HERZEGOVINA': 'BK',
    'BOTSWANA': 'BC',
    'BOUVET ISLAND': 'BV',
    'BRAZIL': 'BR',
    'BRITISH INDIAN OCEAN TERRITORY': 'IO',
    'BRITISH VIRGIN ISLANDS': 'VI',
    'BRUNEI': 'BX',
    'BULGARIA': 'BU',
    'BURKINA FASO': 'UV',
    'BURMA': 'BM',
    'BURUNDI': 'BY',
    'CABO VERDE': 'CV',
    'CAMBODIA': 'CB',
    'CAMEROON': 'CM',
    'CANADA': 'CA',
    'CAYMAN ISLANDS': 'CJ',
    'CENTRAL AFRICAN REPUBLIC': 'CT',
    'CHAD': 'CD',
    'CHILE': 'CI',
    'CHINA': 'CH',
    'CHRISTMAS ISLAND': 'KT',
    'CLIPPERTON ISLAND': 'IP',
    'COCOS ISLANDS': 'CK',
    'COLOMBIA': 'CO',
    'COMOROS': 'CN',
    'DR CONGO': 'CG',  # renamed from 'CONGO' in GeoLite2-City-CSV_20200505
    'COOK ISLANDS': 'CW',
    'CORAL SEA ISLANDS': 'CR',
    'COSTA RICA': 'CS',
    'IVORY COAST': 'IV',
    'CROATIA': 'HR',
    'CUBA': 'CU',
    'CYPRUS': 'CY',
    'CZECHIA': 'EZ',
    'EAST TIMOR': 'TT',  # renamed from 'DEMOCRATIC REPUBLIC OF TIMOR LESTE' in GeoLite2-City-CSV_20200505
    'DENMARK': 'DA',
    'DHEKELIA SOVEREIGN BASE AREA': 'DX',
    'DJIBOUTI': 'DJ',
    'DOMINICA': 'DO',
    'DOMINICAN REPUBLIC': 'DR',
    'ECUADOR': 'EC',
    'EGYPT': 'EG',
    'EL SALVADOR': 'ES',
    'EQUATORIAL GUINEA': 'EK',
    'ERITREA': 'ER',
    'ESTONIA': 'EN',
    'ESWATINI': 'WZ',
    'ETHIOPIA': 'ET',
    'ETOROFU HABOMAI KUNASHIRI AND SHIKOTAN ISLANDS': 'PJ',
    'EUROPA ISLAND': 'EU',
    'FALKLAND ISLANDS': 'FK',
    'FAROE ISLANDS': 'FO',
    'FEDERATED STATES OF MICRONESIA': 'FM',
    'FIJI': 'FJ',
    'FINLAND': 'FI',
    'FRANCE': 'FR',
    'FRENCH GUIANA': 'FG',
    'FRENCH POLYNESIA': 'FP',
    'FRENCH SOUTHERN TERRITORIES': 'FS',
    'GABON': 'GB',
    'GAMBIA': 'GA',
    'GEORGIA': 'GG',
    'GERMANY': 'GM',
    'GHANA': 'GH',
    'GIBRALTAR': 'GI',
    'GLORIOSO ISLANDS': 'GO',
    'GREECE': 'GR',
    'GREENLAND': 'GL',
    'GRENADA': 'GJ',
    'GUADELOUPE': 'GP',
    'GUAM': 'GQ',
    'GUATEMALA': 'GT',
    'GUERNSEY': 'GK',
    'GUINEA': 'GV',
    'GUINEA BISSAU': 'PU',
    'GUYANA': 'GY',
    'HAITI': 'HA',
    'HASHEMITE KINGDOM OF JORDAN': 'JO',
    'HEARD ISLAND AND MCDONALD ISLANDS': 'HM',
    'HONDURAS': 'HO',
    'HONG KONG': 'HK',
    'HOWLAND ISLAND': 'HQ',
    'HUNGARY': 'HU',
    'ICELAND': 'IC',
    'INDIA': 'IN',
    'INDONESIA': 'ID',
    'IRAN': 'IR',
    'IRAQ': 'IZ',
    'IRELAND': 'EI',
    'ISLE OF MAN': 'IM',
    'ISRAEL': 'IS',
    'ITALY': 'IT',
    'JAMAICA': 'JM',
    'JAPAN': 'JA',
    'JARVIS ISLAND': 'DQ',
    'JERSEY': 'JE',
    'JOHNSTON ATOLL': 'JQ',
    'JUAN DE NOVA ISLAND': 'JU',
    'KAZAKHSTAN': 'KZ',
    'KENYA': 'KE',
    'KINGMAN REEF': 'KQ',
    'KIRIBATI': 'KR',
    'KOSOVO': 'KV',
    'KUWAIT': 'KU',
    'KYRGYZSTAN': 'KG',
    'LAOS': 'LA',
    'LATVIA': 'LG',
    'LEBANON': 'LE',
    'LESOTHO': 'LT',
    'LIBERIA': 'LI',
    'LIBYA': 'LY',
    'LIECHTENSTEIN': 'LS',
    'LUXEMBOURG': 'LU',
    'MACAO': 'MC',
    'NORTH MACEDONIA': 'MK',  # before 2019 'MACEDONIA'
    'MADAGASCAR': 'MA',
    'MALAWI': 'MI',
    'MALAYSIA': 'MY',
    'MALDIVES': 'MV',
    'MALI': 'ML',
    'MALTA': 'MT',
    'MARSHALL ISLANDS': 'RM',
    'MARTINIQUE': 'MB',
    'MAURITANIA': 'MR',
    'MAURITIUS': 'MP',
    'MAYOTTE': 'MF',
    'MEXICO': 'MX',
    'MIDWAY ISLANDS': 'MQ',
    'MONACO': 'MN',
    'MONGOLIA': 'MG',
    'MONTENEGRO': 'MJ',
    'MONTSERRAT': 'MH',
    'MOROCCO': 'MO',
    'MOZAMBIQUE': 'MZ',
    'MYANMAR': 'MM',
    'NAMIBIA': 'WA',
    'NAURU': 'NR',
    'NAVASSA ISLAND': 'BQ',
    'NEPAL': 'NP',
    'NETHERLANDS': 'NL',
    'NETHERLANDS ANTILLES': 'NT',
    'NEW CALEDONIA': 'NC',
    'NEW ZEALAND': 'NZ',
    'NICARAGUA': 'NU',
    'NIGER': 'NG',
    'NIGERIA': 'NI',
    'NIUE': 'NE',
    'NORFOLK ISLAND': 'NF',
    'NORTH KOREA': 'KN',
    'NORTHERN MARIANA ISLANDS': 'CQ',
    'NORWAY': 'NO',
    'OMAN': 'MU',
    'PAKISTAN': 'PK',
    'PALAU': 'PS',
    'PALMYRA ATOLL': 'LQ',
    'PANAMA': 'PM',
    'PAPUA NEW GUINEA': 'PP',
    'PARACEL ISLANDS': 'PF',
    'PARAGUAY': 'PA',
    'PERU': 'PE',
    'PHILIPPINES': 'RP',
    'PITCAIRN ISLANDS': 'PC',
    'POLAND': 'PL',
    'PORTUGAL': 'PO',
    'PUERTO RICO': 'RQ',
    'QATAR': 'QA',
    'SOUTH KOREA': 'KS',  # renamed from 'REPUBLIC OF KOREA' in GeoLite2-City-CSV_20200505
    'REPUBLIC OF LITHUANIA': 'LH',
    'REPUBLIC OF MOLDOVA': 'MD',
    'CONGO REPUBLIC': 'CF',  # renamed from 'REPUBLIC OF CONGO' in GeoLite2-City-CSV_20200505
    'ROMANIA': 'RO',
    'RUSSIA': 'RS',
    'RWANDA': 'RW',
    'REUNION': 'RE',
    'SAINT BARTHELEMY': 'TB',
    'SAINT HELENA': 'SH',
    'SAINT LUCIA': 'ST',
    'SAINT MARTIN': 'RN',
    'SAINT PIERRE AND MIQUELON': 'SB',
    'SAINT VINCENT AND GRENADINES': 'VC',
    'SAMOA': 'WS',
    'SAN MARINO': 'SM',
    'SAUDI ARABIA': 'SA',
    'SENEGAL': 'SG',
    'SERBIA': 'RI',
    'SEYCHELLES': 'SE',
    'SIERRA LEONE': 'SL',
    'SINGAPORE': 'SN',
    'SLOVAKIA': 'LO',
    'SLOVENIA': 'SI',
    'SOLOMON ISLANDS': 'BP',
    'SOMALIA': 'SO',
    'SOUTH AFRICA': 'SF',
    'SOUTH GEORGIA AND SOUTH SANDWICH ISLANDS': 'SX',
    'SOUTH SUDAN': 'SS',
    'SPAIN': 'SP',
    'SPRATLY ISLANDS': 'PG',
    'SRI LANKA': 'CE',
    'ST KITTS AND NEVIS': 'SC',
    'SUDAN': 'SU',
    'SURINAME': 'NS',
    'SVALBARD AND JAN MAYEN': 'SV',
    'SWEDEN': 'SW',
    'SWITZERLAND': 'SZ',
    'SYRIA': 'SY',
    'SAO TOME AND PRINCIPE': 'TP',
    'TAIWAN': 'TW',
    'TAJIKISTAN': 'TI',
    'TANZANIA': 'TZ',
    'THAILAND': 'TH',
    'TOGO': 'TO',
    'TOKELAU': 'TL',
    'TONGA': 'TN',
    'TRINIDAD AND TOBAGO': 'TD',
    'TROMELIN ISLAND': 'TE',
    'TUNISIA': 'TS',
    'TURKEY': 'TU',
    'TURKMENISTAN': 'TX',
    'TURKS AND CAICOS ISLANDS': 'TK',
    'TUVALU': 'TV',
    'US VIRGIN ISLANDS': 'VQ',
    'UGANDA': 'UG',
    'UKRAINE': 'UP',
    'UNDESIGNATED SOVEREIGNTY': 'UU',
    'UNITED ARAB EMIRATES': 'AE',
    'UNITED KINGDOM': 'UK',
    'UNITED STATES': 'US',
    'URUGUAY': 'UY',
    'UZBEKISTAN': 'UZ',
    'VANUATU': 'NH',
    'VATICAN CITY': 'VT',
    'VENEZUELA': 'VE',
    'VIETNAM': 'VM',
    'WAKE ISLAND': 'WQ',
    'WALLIS AND FUTUNA': 'WF',
    'WEST BANK': 'WE',
    'WESTERN SAHARA': 'WI',
    'YEMEN': 'YM',
    'ZAMBIA': 'ZA',
    'ZIMBABWE': 'ZI'
}

COUNTRY_IGNORE = (
    # without FIPS 10-4 code
    'ALAND',
    'BONAIRE, SINT EUSTATIUS, AND SABA',
    'CURACAO',
    'SINT MAARTEN',
    'US MINOR OUTLYING ISLANDS',
    'PALESTINE',  # WE? no entries on wikipedia

    # empty in fips csv
    'AMERICAN SAMOA',
    'COOK ISLANDS',
    'EAST TIMOR',
    'FRENCH POLYNESIA',
    'FRENCH SOUTHERN TERRITORIES',
    'HONG KONG',
    'MALTA',
    'MARSHALL ISLANDS',
    'MONTENEGRO',
    'NEW CALEDONIA',
    'NORTHERN MARIANA ISLANDS',
    'SAINT PIERRE AND MIQUELON',
    'SINGAPORE',
    'SVALBARD AND JAN MAYEN',
    'TOKELAU',
    'TUVALU',
    'US VIRGIN ISLANDS',
    'WALLIS AND FUTUNA',

    # missing in fips csv
    'ISLE OF MAN',
    'MYANMAR',
    'SOUTH SUDAN',

    # wip
    'INDIA',
    'INDONESIA',
    'IRAN',
    'ISRAEL',
    'IVORY COAST',
    'KAZAKHSTAN',
    'KENYA',
    'LAOS',
    'LATVIA',
    'LIBERIA',
    'LIBYA',
    'LUXEMBOURG',
    'NORTH MACEDONIA',
    'MALAWI',
    'MAURITANIA',
    'MEXICO',
    'MONGOLIA',
    'MOROCCO',
    'MOZAMBIQUE',
    'NAMIBIA',
    'NEPAL',
    'NIGERIA',
    'NORTH KOREA',
    'PAKISTAN',
    'PAPUA NEW GUINEA',
    'PARAGUAY',
    'PHILIPPINES',
    'POLAND',
    'QATAR',
    'CONGO REPUBLIC',
    'SOUTH KOREA',
    'REPUBLIC OF LITHUANIA',
    'REPUBLIC OF MOLDOVA',
    'RUSSIA',
    'SAINT LUCIA',
    'SAUDI ARABIA',
    'SENEGAL',
    'SERBIA',
    'SLOVAKIA',
    'SLOVENIA',
    'SOMALIA',
    'SOUTH AFRICA',
    'SRI LANKA',
    'SUDAN',
    'SWITZERLAND',
    'TANZANIA',
    'THAILAND',
    'TUNISIA',
    'TURKMENISTAN',
    'UGANDA',
    'UKRAINE',
    'UNITED KINGDOM',
    'VIETNAM'
)

CITY_IGNORE = {
    'AZERBAIJAN': ('AGHSU RAYON',),

    'BAHAMAS': ('CENTRAL ABACO DISTRICT', 'EAST GRAND BAHAMA DISTRICT', 'HOPE TOWN DISTRICT', 'NORTH ELEUTHERA'),

    'CZECHIA': ('CZECHIA',),  # city?

    'DR CONGO': ('BOENDE',),

    'ESWATINI': ('ESWATINI',),  # city?
}

REGION_IGNORE = {
    'BAHAMAS': ('NORTH ANDROS DISTRICT', 'CENTRAL ANDROS DISTRICT', 'MOORES ISLAND DISTRICT', 'NORTH ABACO DISTRICT',
                'GRAND CAY DISTRICT', 'SPANISH WELLS DISTRICT', 'EAST GRAND BAHAMA DISTRICT',
                'WEST GRAND BAHAMA DISTRICT'),

    'BAHRAIN': ('NORTHERN', 'SOUTHERN GOVERNORATE'),

    'BOSNIA AND HERZEGOVINA': ('BRCKO',),

    'BOTSWANA': ('CHOBE DISTRICT', 'JWANENG', 'LOBATSE'),

    'BHUTAN': ('GASA', 'TRASHI YANGSTE'),

    'BURKINA FASO': ('CASCADES REGION', 'CENTRE', 'CENTRE EST', 'CENTRE NORD', 'CENTRE OUEST', 'EST', 'HAUTS BASSINS',
                     'NORD', 'PLATEAU CENTRAL', 'SUD OUEST'),

    'CAMBODIA': ('TBOUNG KHMUM',),

    # since 2018
    'CHILE': ('NUBLE',),

    # since 2010
    'CUBA': ('MAYABEQUE',),

    'EGYPT': ('LUXOR',),

    'FINLAND': ('CENTRAL FINLAND', 'NORTHERN OSTROBOTHNIA', 'SOUTHERN OSTROBOTHNIA', 'CENTRAL OSTROBOTHNIA',
                'OSTROBOTHNIA', 'FINLAND PROPER', 'TAVASTIA PROPER', 'PIRKANMAA', 'KYMENLAAKSO', 'UUSIMAA',
                'NORTH KARELIA', 'SATAKUNTA', 'SOUTHERN SAVONIA', 'PAIJANNE TAVASTIA', 'NORTHERN SAVO',
                'SOUTH KARELIA', 'KAINUU'),

    # since 2016
    'FRANCE': ('NOUVELLE AQUITAINE', 'BOURGOGNE FRANCHE COMTE', 'HAUTS DE FRANCE', 'OCCITANIE', 'GRAND EST',
               'AUVERGNE RHONE ALPES', 'NORMANDY'),

    'GEORGIA': ('SAMTSKHE JAVAKHETI', 'GURIA', 'IMERETI', 'KAKHETI', 'KVEMO KARTLI',
                'RACHA LECHKHUMI AND KVEMO SVANETI', 'SAMEGRELO AND ZEMO SVANETI', 'SHIDA KARTLI'),

    'GREECE': ('NORTH AEGEAN', 'SOUTH AEGEAN', 'CENTRAL GREECE', 'WEST GREECE', 'CENTRAL MACEDONIA', 'WEST MACEDONIA',
               'CRETE', 'EPIRUS', 'IONIAN ISLANDS', 'PELOPONNESE', 'MOUNT ATHOS'),

    # since 2018
    'GREENLAND': ('QEQERTALIK', 'AVANNAATA'),

    'GRENADA': ('CARRIACOU AND PETITE MARTINIQUE',),

    'IRELAND': ('LEINSTER', 'MUNSTER', 'CONNAUGHT', 'ULSTER'),

    'MALDIVES': ('NORTHERN ARI ATOLL',),

    'NEW ZEALAND': ('TASMAN',),  # Tasman Region was not assigned a code for unknown reasons. (wikipedia)

    'NORWAY': ('TRONDELAG',),

    'OMAN': ('AL BATINAH NORTH GOVERNORATE', 'AL BATINAH SOUTH', 'NORTHEASTERN GOVERNORATE',
             'SOUTHEASTERN GOVERNORATE'),

    'TAIWAN': ('YUNLIN', 'NANTOU', 'CHIAYI', 'CHIAYI COUNTY', 'PENGHU COUNTY', 'HSINCHU COUNTY', 'CHANGHUA',
               'TAICHUNG CITY', 'TAINAN', 'TAOYUAN', 'KEELUNG', 'YILAN', 'MIAOLI', 'KINMEN COUNTY', 'PINGTUNG',
               'LIENCHIANG', 'HUALIEN', 'TAITUNG', 'HSINCHU', 'NEW TAIPEI'),

    'TAJIKISTAN': ('DUSHANBE', 'GORNO BADAKHSHAN', 'REPUBLICAN SUBORDINATION'),

    'TRINIDAD AND TOBAGO': ('SAN JUAN/LAVENTILLE', 'TUNAPUNA/PIARCO', 'PENAL/DEBE', 'POINT FORTIN',
                            'COUVA TABAQUITE TALPARO', 'DIEGO MARTIN', 'CHAGUANAS', 'SIPARIA', 'PRINCES TOWN',
                            'SANGRE GRANDE'),

    'PANAMA': ('NGOEBE BUGLE', 'PANAMA OESTE', 'EMBERA WOUNAAN', 'GUNA YALA'),

    # since 2017
    'SIERRA LEONE': ('NORTH WEST',),

    'SOLOMON ISLANDS': ('HONIARA',),

    'SPAIN': ('CEUTA', 'MELILLA'),

    'TONGA': ('EUA', 'NIUAS'),

    # since 2004
    'YEMEN': ('RAYMAH', 'SOQATRA'),

    # since 2011
    'ZAMBIA': ('MUCHINGA',)
}

REGION_REPLACE = {
    'AE': {
        'ABU ZABY': 'ABU DHABI',
        'DUBAYY': 'DUBAI'
    },
    'AF': {
        'KABOL': 'KABUL',
        'KANDAHAR KANDAHAR': 'KANDAHAR'
    },
    'AG': {
        'ALGER': 'ALGIERS',
        'TAMANGHASSET': 'TAMANRASSET',
    },
    'AJ': {
        'ABSERON': 'ABSHERON',
        'BAKI': 'BAKU CITY',
        'GANCA': 'GANJA CITY',
        'NAXCIVAN': 'NAKHICHEVAN',
        'YARDIMLI': 'YARDYMLI',
        'SAKI': 'SHAKI CITY',
        'SUMQAYIT': 'SUMQAYIT CITY',
    },
    'AL': {
        'BERAT': 'BERATIT',
        'DIBER': 'DIBRES',
        'DURRES': 'DURRESIT',
        'ELBASAN': 'ELBASANIT',
        'FIER': 'FIERIT',
        'TIRANE': 'TIRANA',
        'GJIROKASTER': 'GJIROKASTRES',
        'KORCE': 'KORCES',
        'LEZHE': 'LEZHES',
        'SHKODER': 'SHKODRES',
        'VLORE': 'VLORES'
    },
    'AM': {
        'LORRI': 'LORI'
    },
    'AO': {
        'CUANDO CUBANGO': 'CUANDO COBANGO',
        'CUANZA SUL': 'KWANZA SUL',
        'LUNDA NORTE': 'LUANDA NORTE',
    },
    'AR': {
        'TIERRA DEL FUEGO ANTARTIDA E ISLAS DEL ATLANTICO SUR': 'TIERRA DEL FUEGO'
    },
    'AU': {
        'KARNTEN': 'CARINTHIA',
        'NIEDEROSTERREICH': 'LOWER AUSTRIA',
        'OBEROSTERREICH': 'UPPER AUSTRIA',
        'STEIERMARK': 'STYRIA',
        'TIROL': 'TYROL',
        'WIEN': 'VIENNA'
    },
    'BA': {
        'AL MUHARRAQ': 'MUHARRAQ',
        'AL ASIMAH': 'MANAMA',
        'AR RIFA WA AL MINTAQAH AL JANUBIYAH': 'AR RIFA'
    },
    'BC': {
        'CENTRAL': 'CENTRAL DISTRICT',
        'FRANCISTOWN': 'CENTRAL',
        'SOUTH EAST': 'GABORONE',
        'SOUTHERN': 'NGWAKETSI',
    },
    'BD': {
        'HAMILTON': 'HAMILTON CITY',
    },
    'BE': {
        'BRABANT WALLON': 'WALLONIA',
        'BRUSSELS HOOFDSTEDELIJK GEWEST/REGION DE BRUXELLES CAPITALE': 'BRUSSELS CAPITAL',
        'VLAAMS BRABANT': 'FLANDERS'
    },
    'BF': {
        # 'FREEPORT': 'CITY OF FREEPORT',
        'NICHOLLSTOWN AND BERRY ISLANDS': 'BERRY ISLANDS',
        'SANDY POINT': 'SOUTH ABACO'
    },
    'BG': {
        'RANGPUR DIVISION': 'RAJSHAHI',
        'MYMENSINGH DIVISION': 'DHAKA'
    },
    'BK': {
        'FEDERATION OF BOSNIA AND HERZEGOVINA': 'FEDERATION OF B&H',
        'REPUBLICA SRPSKA': 'REPUBLIKA SRPSKA'
    },
    'BO': {
        'BRESTSKAYA VOBLASTS': 'BREST',
        'HOMYELSKAYA VOBLASTS': 'GOMEL',
        'HRODZYENSKAYA VOBLASTS': 'GRODNENSKAYA',
        'MAHILYOWSKAYA VOBLASTS': 'MOGILEV',
        'MINSKAYA VOBLASTS': 'MINSK CITY',
        'VITSYEBSKAYA VOBLASTS': 'VITEBSK'
    },
    'BP': {
        'MAKIRA': 'MAKIRA ULAWA'
    },
    'BR': {
        'DISTRITO FEDERAL': 'FEDERAL DISTRICT'
    },
    'BT': {
        'CHHUKHA': 'CHUKHA',
        'CHIRANG': 'TSIRANG',
        'DAGA': 'DAGANA',
        'GEYLEGPHUG': 'SARPANG',
        'HA': 'HAA',
        'LHUNTSHI': 'LHUNTSE',
        'PEMAGATSEL': 'PEMAGATSHEL',
        'SAMDRUP': 'SAMDRUP JONGKHAR',
        'TASHIGANG': 'TRASHIGANG',
        'TONGSA': 'TRONGSA',
        'WANGDI PHODRANG': 'WANGDUE PHODRANG'
    },
    'BU': {
        'KHASKOVO': 'HASKOVO',
        'KURDZHALI': 'KARDZHALI',
        'SOFIYA': 'SOFIA',
        'SOFIYA GRAD': 'SOFIA CAPITAL',
        'TURGOVISHTE': 'TARGOVISHTE',
        'VELIKO TURNOVO': 'VELIKO TARNOVO'
    },
    'CA': {
        'YUKON TERRITORY': 'YUKON'
    },
    'CB': {
        'BANTEAY MEAN CHEAY': 'BANTEAY MEANCHEY',
        'BATDAMBANG': 'BATTAMBANG',
        'KAMPONG SPOE': 'KAMPONG SPEU',
        'KAMPONG THUM': 'KAMPONG THOM',
        'KAOH KONG': 'KOH KONG',
        'KRACHEH': 'KRATIE',
        'KEB': 'KEP',
        'MONDOL KIRI': 'MONDOLKIRI',
        'PHNUM PENH': 'PHNOM PENH',
        'POUTHISAT': 'PURSAT',
        'PREAH SEIHANU': 'PREAH SIHANOUK',
        'ROTANAH KIRI': 'RATANAKIRI',
        'SIEM REAB': 'SIEM REAP',
        'STOENG TRENG': 'STUNG TRENG',
        'TAKEV': 'TAKEO',
        'OTDAR MEAN CHEAY': 'OTAR MEANCHEY'
    },
    'CD': {
        'OUADDAI': 'OUADAI'
    },
    'CG': {
        'SUD KIVU': 'SOUTH KIVU',
        'KINSHASA': 'KINSHASA CITY'
    },
    'CH': {
        'NEI MONGOL INNER MONGOLIA': 'INNER MONGOLIA AUTONOMOUS REGION',
        'XIZANG TIBET': 'TIBET',
        'NINGXIA NINGXIA': 'NINGXIA HUI AUTONOMOUS REGION'
    },
    'CI': {
        'BIO BIO': 'BIOBIO',
        'AISEN DEL GENERAL CARLOS IBANEZ DEL CAMPO': 'AYSEN',
        'REGION METROPOLITANA': 'SANTIAGO METROPOLITAN',
        'LIBERTADOR GENERAL BERNARDO OHIGGINS': 'OHIGGINS REGION',
        'MAGALLANES Y DE LA ANTARTICA CHILENA': 'REGION OF MAGALLANES'
    },
    'CM': {
        'OUEST WEST': 'WEST REGION',
        'NORD OUEST NORTH WEST': 'NORTH WEST REGION',
        'SUD OUEST SOUTH WEST': 'SOUTH WEST REGION',
        'SUD SOUTH': 'SOUTH'
    },
    'CN': {
        'ANJOUAN': 'NDZUWANI'
    },
    'CO': {
        'DISTRITO CAPITAL': 'BOGOTA DC'
    },
    'CT': {
        'NANA GREBINGUI': 'NANA GREBIZI'
    },
    'CU': {
        'ISLA DE LA JUVENTUD': 'MUNICIPIO ESPECIAL ISLA DE LA JUVENTUD',
        'LA HABANA': 'HAVANA'
    },
    'CV': {
        'CAPE VERDE': 'CABO VERDE',
        'RIBEIRA GRANDE': 'RIBEIRA GRANDE DE SANTIAGO',
        'SANTA CRUZ': 'SAO LOURENCO DOS ORGAOS',    # since 2005
    },
    'CY': {
        'FAMAGUSTA': 'AMMOCHOSTOS',
        'PAPHOS': 'PAFOS',
        'LARNACA': 'LARNAKA',
        'KYRENIA': 'KERYNEIA'
    },
    'DA': {
        'SYDDANMARK': 'SOUTH DENMARK',
        'NORDJYLLAND': 'NORTH DENMARK',
        'MIDTJYLLEN': 'CENTRAL JUTLAND',
        'HOVEDSTADEN': 'CAPITAL REGION',
        'SJAELLAND': 'ZEALAND'
    },
    'DJ': {
        'TADJOURA': 'TADJOURAH'
    },
    'DR': {
        'DISTRITO NACIONAL': 'NACIONAL',
        'BAHORUCO': 'BAORUCO',
        'SALCEDO': 'HERMANAS MIRABAL'
    },
    'EC': {
        'ORELLANA': 'FRANCISCO DE ORELLANA'
    },
    'EG': {
        'AL JIZAH': 'GIZA',
        'ASH SHARQIYAH': 'SHARQIA',
        'AD DAQAHLIYAH': 'DAKAHLIA',
        'AL QALYUBIYAH': 'QALYUBIA',
        'AL GHARBIYAH': 'GHARBIA',
        'AL FAYYUM': 'FAIYUM',
        'AL ISKANDARIYAH': 'ALEXANDRIA',
        'AL QAHIRAH': 'CAIRO GOVERNORATE',
        'QINA': 'QENA',
        'AL MINUFIYAH': 'MONUFIA',
        'KAFR ASH SHAYKH': 'KAFR EL SHEIKH',
        'AL BUHAYRAH': 'BEHEIRA',
        'BANI SUWAYF': 'BENI SUWEIF',
        'DUMYAT': 'DAMIETTA GOVERNORATE',
        'AL BAHR AL AHMAR': 'RED SEA',
        'AL ISMAILIYAH': 'ISMAILIA GOVERNORATE',
        'AL MINYA': 'MINYA',
        'SHAMAL SINA': 'NORTH SINAI',
        'JANUB SINA': 'SOUTH SINAI',
        'BUR SAID': 'PORT SAID',
        'SUHAJ': 'SOHAG',
        'AS SUWAYS': 'SUEZ'
    },
    'EN': {
        'TARTUMAA': 'TARTU',
        'LAANEMAA': 'LAANE',
        'SAAREMAA': 'SAARE'
    },
    'ER': {
        'MAAKEL': 'MAEKEL',
        'DEBUBAWI KEYIH BAHRI': 'SOUTHERN RED SEA',
        'SEMENAWI KEYIH BAHRI': 'NORTHERN RED SEA'
    },
    'ET': {
        'AMARA': 'AMHARA',
        'ADIS ABEBA': 'ADDIS ABABA',
        'YEDEBUB BIHEROCH BIHERESEBOCH NA HIZBOCH': 'SOUTHERN NATIONS, NATIONALITIES, AND PEOPLES REGION',
        'GAMBELA HIZBOCH': 'GAMBELA',
        'HARERI HIZB': 'HARARI',
        'SUMALE': 'SOMALI'
    },
    'EZ': {
        'JIHOMORAVKY KRAJ': 'SOUTH MORAVIAN',
        'ZLINSKY KRAJ': 'ZLIN',
        'STREDOCESKY KRAJ': 'CENTRAL BOHEMIA',
        'MORAVSKOLEZSKY KRAJ': 'MORAVSKOSLEZSKY'
    },
    'FI': {
        'LAPPI': 'LAPLAND'
    },
    'FR': {
        'CENTRE': 'CENTRE VAL DE LOIRE',
        'BRETAGNE': 'BRITTANY',
        'CORSE': 'CORSICA',
        'LIMOUSIN': 'LIMOSINE'
    },
    'GA': {
        'WESTERN': 'WEST COAST'
    },
    'GB': {
        'NGOUNIE': 'NGOUNI'
    },
    'GG': {
        'TBILISI': 'KALAKI TBILISI',
        'MTSKHETIS RAIONI': 'MTSKHETA MTIANETI',  # wtf
    },
    'GM': {
        'BAYERN': 'BAVARIA',
        'NORDRHEIN WESTFALEN': 'NORTH RHINE WESTPHALIA',
        'HESSEN': 'HESSE',
        'NIEDERSACHSEN': 'LOWER SAXONY',
        'THURINGEN': 'THURINGIA',
        'SACHSEN ANHALT': 'SAXONY ANHALT',
        'SACHSEN': 'SAXONY',
        'BERLIN': 'LAND BERLIN'
    },
    'GR': {
        'ATTIKI': 'ATTICA',
        'LARISA': 'THESSALY',
        'EVROS': 'EAST MACEDONIA AND THRACE'
    },
    'GT': {
        'SUCHITEPEQUEZ': 'SUCHITEPEQUE'
    },
    'HA': {
        'GRAND ANSE': 'GRANDANS'
    },
    'HO': {
        'ISLAS DE LA BAHIA': 'BAY ISLANDS'
    },
    'HR': {
        'VUKOVARSKO SRIJEMSKA': 'VUKOVAR SIRMIUM',
        'SPLITSKO DALMATINSKA': 'SPLIT DALMATIA',
        'ISTARSKA': 'ISTRIA',
        'BRODSKO POSAVSKA': 'SLAVONSKI BROD POSAVINA',
        'MEDIMURSKA': 'MEGIMURSKA',
        'ZAGREBACKA': 'ZAGREB COUNTY',
        'GRAD ZAGREB': 'ZAGREB'
    },
    'IC': {
        'AUSTURLAND': 'EAST',
        'HOFUDBORGARSVAEDI': 'CAPITAL',
        'NORDURLAND EYSTRA': 'NORTHEAST',
        'NORDURLAND VESTRA': 'NORTHWEST',
        'SUDURLAND': 'SOUTH',
        'SUDURNES': 'SOUTHERN PENINSULA',
        'VESTFIRDIR': 'WESTFJORDS',
        'VESTURLAND': 'WEST'
    },
    'IT': {
        'LOMBARDIA': 'LOMBARDY',
        'TOSCANA': 'TUSCANY',
        'SARDEGNA': 'SARDINIA',
        'ABRUZZI': 'ABRUZZO',
        'SICILIA': 'SICILY',
        'PUGLIA': 'APULIA',
        'BASILICATA': 'BASILICATE',
        'LAZIO': 'LATIUM',
        'MARCHE': 'MARCHES',
        'PIEMONTE': 'PIEDMONT',
        'VALLE DAOSTA': 'AOSTA VALLEY'
    },
    'IZ': {
        'AL ANBAR': 'ANBAR',
        'AL BASRAH': 'BASRA',
        'DAHUK': 'DIHOK',
        'AT TAMIM': 'KIRKUK',
        'NINAWA': 'NINEVEH'
    },
    'JA': {
        'FUKUSHIMA': 'FUKUSHIMA KEN',
        'GUMMA': 'GUNMA'
    },
    'JO': {
        'AJLUN': 'AJLOUN',
        'AL AQABAH': 'AQABA',
        'AL KARAK': 'KARAK',
        'AL BALQA': 'BALQA',
        'AL MAFRAQ': 'MAFRAQ',
        'AT TAFILAH': 'TAFIELAH',
        'AZ ZARQA': 'ZARQA',
        'JARASH': 'JERASH',
        'JORDAN': 'HASHEMITE KINGDOM OF JORDAN',
    },
    'KG': {
        'YSYK KOL': 'ISSYK KUL',
        'CHUY': 'CHUYSKAYA',
        'BISHKEK': 'GOROD BISHKEK',
        'OSH': 'OSH OBLASTY'
    },
    'LE': {
        'LIBAN SUD': 'SOUTH GOVERNORATE'
    },
    'MC': {
        'MACAU': 'MACAO'
    },
    'MU': {
        'AL BURAYMI': 'AL BURAIMI',
        'MASQAT': 'MUSCAT',
        'ZUFAR': 'DHOFAR'
    },
    'MV': {
        'GNAVIYANI': 'GNYAVIYANI'
    },
    'MY': {
        'PULAU PINANG': 'PENANG'
    },
    'NL': {
        'NOORD BRABANT': 'NORTH BRABANT',
        'NOORD HOLLAND': 'NORTH HOLLAND',
        'ZUID HOLLAND': 'SOUTH HOLLAND'
    },
    'NU': {
        'ATLANTICO SUR': 'COSTA CARIBE SUR'
    },
    'PO': {
        'LISBOA': 'LISBON'
    },
    'PS': {
        'AIMELIK': 'AIMELIIK'
    },
    'PU': {
        'BOLAMA': 'BOLAMA AND BIJAGOS'
    },
    'RW': {
        'OUEST': 'WESTERN',
        'SUD': 'SOUTHERN',
        'NORD': 'NORTHERN'
    },
    'SC': {
        'SAINT JOHN CAPISTERRE': 'SAINT JOHN CAPESTERRE',
        'SAINT PAUL CAPISTERRE': 'SAINT PAUL CAPESTERRE',
        'SAINT THOMAS MIDDLE ISLAND': 'MIDDLE ISLAND'
    },
    'SE': {
        'GRAND ANSE': 'GRAND ANSE PRASLIN'
    },
    'SL': {

    },
    'SM': {
        'MONTE GIARDINO': 'MONTEGIARDINO',
        'SAN MARINO': 'SAN MARINO CITTA'
    },
    'SP': {
        'PAIS VASCO': 'BASQUE COUNTRY',
        'NAVARRA': 'NAVARRE',
        'ANDALUCIA': 'ANDALUSIA',
        'CASTILLA LA MANCHA': 'CASTILLE LA MANCHA',
        'CATALUNA': 'CATALONIA',
        'CASTILLA Y LEON': 'CASTILLE AND LEON',
        'CANARIAS': 'CANARY ISLANDS',
        'VALENCIANA': 'VALENCIA',
        'ISLAS BALEARES': 'BALEARIC ISLANDS'
    },
    'SY': {
        'HALAB': 'ALEPPO',
        'DIMASHQ': 'DAMASCUS',
        'HAMAH': 'HAMA',
        'AL LADHIQIYAH': 'LATAKIA'
    },
    'TD': {
        'TRINIDAD': 'TRINIDAD AND TOBAGO'  # not sure
    },
    'TP': {
        'SAO TOME': 'SAO TOME ISLAND'
    },
    'TU': {
        'DUZCE': 'DUEZCE',
        'BARTIN ILI': 'BARTIN',
        'ICEL': 'MERSIN',
        'GUMUSHANE': 'GUEMUESHANE',
        'KARABUK': 'KARABUEK'
    },
    'TW': {
        'KAO HSIUNG': 'KAOHSIUNG',
        'TAI PEI': 'TAIPEI CITY'
    },
    'UZ': {
        'SURHKONDARYO': 'SURXONDARYO',
        'FARGHONA': 'FERGANA',
        'KHORAZM': 'XORAZM',
        'QORAQALPOGHISTON': 'KARAKALPAKSTAN',
        'NAWOIY': 'NAVOIY'
    },
    'UV': {
        'MOUHOUN': 'BOUCLE DU MOUHOUN'
    },
    'YM': {
        'ADAN': 'ADEN',
        'AMRAN': 'OMRAN',
        'SANA': 'SANAA'
    }
}

LOCATION_TO_PARENT = {
    'BY': {
        'BUJUMBURA MAIRIE PROVINCE': 'BUJUMBURA',
        'BUJUMBURA RURAL PROVINCE': 'BUJUMBURA',
        'ISALE': 'BUJUMBURA',
        'ROHERO': 'BUJUMBURA',
        'RUMONGE': 'BUJUMBURA',  # since 2015
    },
    'CD': {
        'AM DJARASS': 'BORKOU ENNEDI TIBESTI',
        'AOZOU': 'BORKOU ENNEDI TIBESTI',
        'BORKOU REGION': 'BORKOU ENNEDI TIBESTI',
        'ENNEDI EST': 'BORKOU ENNEDI TIBESTI',
        'ENNEDI OUEST': 'BORKOU ENNEDI TIBESTI',
        'FADA': 'BORKOU ENNEDI TIBESTI',
        'FAYA LARGEAU': 'BORKOU ENNEDI TIBESTI',
        'TIBESTI REGION': 'BORKOU ENNEDI TIBESTI',
        'BARH EL GAZEL': 'KANEM',  # since 2008
        'SALAL': 'KANEM'
    },
    'CG': {
        'AKETI': 'ORIENTALE',
        'BAS UELE': 'ORIENTALE',
        'BUNIA': 'ORIENTALE',
        'HAUT UELE': 'ORIENTALE',
        'HAUT LOMANI': 'KATANGA',
        'INONGO': 'BANDUNDU',
        'ISIRO': 'ORIENTALE',
        'ITURI': 'ORIENTALE',
        'KASAI': 'KASAI OCCIDENTAL',
        'KIKWIT': 'BANDUNDU',
        'KOLWEZI': 'KATANGA',
        'KONGOLO': 'KATANGA',
        'KWILU': 'BANDUNDU',
        'LODJA': 'KASAI ORIENTAL',
        'LOMAMI': 'KATANGA',
        'LUALABA': 'KATANGA',
        'LUBUMBASHI': 'KATANGA',
        'LUEBO': 'KASAI OCCIDENTAL',
        'MAI NDOMBE': 'BANDUNDU',
        'MALUKU': 'EQUATEUR',
        'MONGALA': 'EQUATEUR',
        'MWENE DITU': 'KATANGA',
        'PROVINCE DU SUD UBANGI': 'EQUATEUR',
        'SANKURU': 'KASAI ORIENTAL',
        'SUNGU MONGA': 'KATANGA',
        'TANGANIKA': 'KATANGA',
        'TSHOPO': 'ORIENTALE',
        'TSHUAPA': 'EQUATEUR',
        'UPPER KATANGA': 'KATANGA',
        'YANGA LIBENGE': 'EQUATEUR',
        'YANGAMBI': 'ORIENTALE'
    },
    'CV': {
        'PICOS': 'SANTA CATARINA',  # since 2005
        'COVA FIGUEIRA': 'SAO FILIPE',
        'PORTO NOVO': 'RIBEIRA GRANDE',
        'RIBEIRA BRAVA': 'SAO NICOLAU',
        'QUEIMADAS': 'SAO NICOLAU',
        'SANTA CATARINA DO FOGO': 'SANTA CATARINA',
        'SAO SALVADOR DO MUNDO': 'SANTA CATARINA',  # since 2005
        'TARRAFAL DE SAO NICOLAU': 'SAO NICOLAU',
        'TARRAFAL DE SÃO NICOLAU': 'SAO NICOLAU',
        'VILA DA RIBEIRA BRAVA': 'SAO NICOLAU'
    },
    'EC': {
        # since 2007
        'PROVINCIA DE SANTA ELENA': 'GUAYAS',
        'SANTA ELENA': 'GUAYAS',
        'SALINAS': 'GUAYAS',
        'PROVINCIA DE SANTO DOMINGO DE LOS TSACHILAS': 'PICHINCHA',
        'SANTO DOMINGO DE LOS COLORADOS': 'PICHINCHA'
    },
    'UV': {
        'BANFORA': 'COMOE',
        'BOBO DIOULASSO': 'HOUET',
        'DIAPAGA': 'TAPOA',
        'DIÉBOUGOU': 'BOUGOURIBA',
        'KONGOUSSI': 'BAM',
        'KOUDOUGOU': 'BOULKIEMDE',
        'OUAGADOUGOU': 'KADIOGO',
        'OUAHIGOUYA': 'YATENGA',
        'TENKODOGO': 'BOULGOU',
        'ZINIARÉ': 'OUBRITENGA'
    },
    'UZ': {
        # city and region have same name but different fips code :(
        'TASHKENT': 'TOSHKENT',
        'TOSHKENT SHAHRI': 'TOSHKENT'
    },
    'VC': {
        'SAINT VINCENT AND GRENADINES': 'GRENADINES'
    }
}

DIVISION_OVERRIDE = {
    'AC': 'PARISH OF',
    'AL': 'QARKU I',
    'AR': 'FD',
    'BL': 'DEPARTAMENTO DE',
    'BN': 'DEPARTMENT',
    'BT': 'DZONGKHAG',
    'BU': 'OBLAST',
    'CI': re.compile(r'(REGION DE LA |REGION DE |REGION DEL | REGION)'),
    'CM': 'REGION',
    'CO': re.compile(r'(DEPARTAMENTO DE.*?\s|\sDEPARTMENT)'),
    'CS': 'PROVINCIA DE',
    'CU': 'PROVINCIA DE',
    'DJ': 'REGION',
    'DR': re.compile(r'(PROVINCIA DE |PROVINCIA )'),
    'EC': re.compile(r'(PROVINCIA DE |PROVINCIA DEL )'),
    'ES': 'DEPARTAMENTO DE',
    'ET': 'REGION',
    'EZ': 'KRAJ',
    'FM': 'STATE OF',
    'GA': 'DIVISION',
    'GG': 'RAIONI',
    'GM': 'REGION',
    'GT': re.compile(r'(DEPARTAMENTO DE.*?\s|\sDEPARTMENT)'),
    'GV': 'REGION',
    'HA': re.compile(r'(DEPARTEMENT DE L|DEPARTEMENT DE )'),
    'HO': 'DEPARTAMENTO DE',
    'HR': 'ZUPANIJA',
    'HU': 'MEGYE',
    'IZ': 'MUHAFAZAT',
    'JM': 'PARISH OF',
    'KG': 'OBLAST',
    'KU': 'MUHAFAZAT',
    'LE': 'MOHAFAZAT',
    'ML': 'REGION',
    'MU': 'MUHAFAZAT',
    'MV': re.compile(r'( ATHOLHU| ATOLL)'),
    'NG': 'REGION',
    'NL': 'PROVINCIE',
    'NO': 'COUNTY',
    'NS': 'DISTRIKT',
    'NU': 'DEPARTAMENTO DE',
    'PE': re.compile(r'(REGION DE | REGION|DEPARTAMENTO DE )'),
    'PM': re.compile(r'(PROVINCIA DE |PROVINCIA DEL )'),
    'PS': 'STATE OF',
    'RO': 'JUDETUL',
    'SM': 'CASTELLO DI',
    'SP': 'PRINCIPALITY OF',
    'SW': (' LAN', 'S LAN'),
    'SY': 'GOVERNORATE',
    'TD': re.compile(r'(BOROUGH OF )'),
    'TI': 'VILOYATI',
    'UP': 'OBLAST',
    'UV': 'PROVINCE DE LA ',
    'UY': 'DEPARTAMENTO DE',
    'UZ': re.compile(r'( VILOYATI| PROVINCE)'),
    'VC': 'PARISH OF',
    'VE': 'ESTADO',
    'YM': 'MUHAFAZAT'
}


re_par1 = re.compile(r'\([^()]*\)')
re_par2 = re.compile(r'\[[^()]*\]')


# FIXME: better
def cleanup(text: str) -> str:
    text = unidecode(text.upper()).replace('@', 'A').replace('\x7f', '')
    text = re_par1.sub('', text)
    text = re_par2.sub('', text)
    for part in ('THE ', ' THE', 'CITY OF '):
        text = text.replace(part, '')
    text = text.replace('  ', ' ')
    text = text.replace('-', ' ')
    text = text.replace('.', '')
    for quote in "ʼ’‘ʻ`'":
        text = text.replace(quote, '')
    return text.strip()


def search(rn, rd, c, e, verbose=False):
    names = set()
    names.add(rn)

    if isinstance(rd, Pattern):
        names.add(rd.sub('', rn))
    elif isinstance(rd, tuple):
        for r in rd:
            names.add('{}{}'.format(rn, r))
    elif isinstance(rd, str):
        names.add('{} OF {}'.format(rd, rn))
        names.add('{} {}'.format(rn, rd))
        names.add('{} {}'.format(rd, rn))

        if rd in rn:
            rn = rn.replace(rd, '').strip()
            names.add(rn)

    if c == os.environ.get('C') and verbose:
        print('\nSearching for {}:\n > {}'.format(', '.join(sorted(names)), ', '.join(sorted(e.keys()))))

    for n in names:
        if n in e:
            if c == os.environ.get('C'):
                print('Found {}'.format(n))
            return n


def fill(ids, ccode, rcode):
    for geoid in ids:
        geoid2fips[geoid] = (ccode, rcode)


def parse_locations():
    with open(opts.location_file, 'r', encoding='utf-8') as f:
        locations = defaultdict(lambda: defaultdict(set))
        for row in csv.DictReader(f):
            country = cleanup(row['country_name'])
            if not country:
                continue  # wtf?

            region = cleanup(row['subdivision_1_name'] or row['country_name'])
            city_name = cleanup(row['city_name']) if row['city_name'] else None
            geoname_id = int(row['geoname_id'])

            locations[country][region].add(geoname_id)
            if city_name is not None:
                locations[country][city_name].add(geoname_id)
                # noinspection PyTypeChecker
                cities[country][city_name] = region

                sub2_name = cleanup(row['subdivision_2_name'])
                if sub2_name:
                    # noinspection PyTypeChecker
                    sub2[country][city_name] = sub2_name

        return locations


def parse_fips():
    with open(opts.input_file, 'r', encoding='utf-8') as f:
        fips = defaultdict(dict)
        for row in csv.DictReader(f):
            fips_country_code = row['region_code'][0:2]
            fips_region_code = row['region_code'][2:4]

            region_division = row['region_division'].split()[0].upper()
            if region_division != 'COUNTRY' and fips_country_code not in region_divisions:
                region_divisions[fips_country_code] = region_division

            region_name = row['region_name'].split('  ')[0]
            region_name = cleanup(region_name)

            region_name = REGION_REPLACE.get(fips_country_code, {}).get(region_name, region_name)
            value = (region_division, fips_country_code, fips_region_code, region_name)

            if (fips_country_code in fips) \
                    and (fips_region_code in fips[fips_country_code]) \
                    and (value in fips[fips_country_code][region_name]):
                raise Exception('Duplicate key for {}'.format(row))

            # noinspection PyTypeChecker
            fips[fips_country_code][region_name] = value
        return fips


def ignore_city(country, city):
    return country in CITY_IGNORE and city in CITY_IGNORE[country]


def ignore_region(country, region):
    return country in REGION_IGNORE and region in REGION_IGNORE[country]


def correlate(locations, fips):
    for country in sorted(locations.keys()):
        fips_country_code = FIPS_COUNTRIES.get(country)
        if fips_country_code is None and country not in COUNTRY_IGNORE:
            raise Exception('Country {} not found in fips country table'.format(country))

        if country in COUNTRY_IGNORE:
            if fips_country_code:
                for location in locations[country].values():
                    fill(location, fips_country_code, '00')
            continue

        entry = fips[fips_country_code]

        for location_name in sorted(locations[country].keys()):
            location_name = LOCATION_TO_PARENT.get(fips_country_code, {}).get(location_name, location_name)
            region_name = None
            region_division = region_divisions.get(fips_country_code)
            location = locations[country][location_name]

            found = search(location_name, region_division, fips_country_code, entry, verbose=True)
            if found is None:
                city = search(location_name, region_division, fips_country_code, cities[country])
                if city is not None:
                    region_name = cities[country][city]
                    region_name = REGION_REPLACE.get(fips_country_code, {}).get(region_name, region_name)
                    found = search(region_name, region_division, fips_country_code, entry, verbose=True)

            if found is None:
                sub2_name = search(location_name, region_division, fips_country_code, sub2[country])
                if sub2_name is not None:
                    region_name = sub2[country][sub2_name]
                    region_name = REGION_REPLACE.get(fips_country_code, {}).get(region_name, region_name)
                    found = search(region_name, region_division, fips_country_code, entry, verbose=True)
                    if found is None:
                        fill(location, fips_country_code, '00')
                        continue

            if found is None:
                if ignore_city(country, location_name) or ignore_region(country, location_name) or \
                        (region_name and ignore_region(country, region_name)):
                    if fips_country_code == os.environ.get('I'):
                        print('Ignoring: {} ({}) - {} ({})'.format(location_name, region_name, country, fips_country_code))
                    fill(location, fips_country_code, '00')
                    continue

                if 'N' in os.environ:
                    print('Location {} ({}) not found in {} ({})'.format(location_name, region_name, country,
                                                                         fips_country_code))
                    continue
                raise Exception('Location {} ({}) not found in {} ({})'.format(location_name, region_name, country,
                                                                               fips_country_code))

            if region_name and ignore_region(country, region_name):
                raise Exception('Ignored region found: {} in {}'.format(location_name, country))

            fill(location, fips_country_code, entry[found][2])


def writecsv():
    with open(opts.output_file, 'w', encoding='utf-8') as _out:
        writer = csv.writer(_out)
        writer.writerow(('geoname_id', 'country', 'region'))
        for geoname_id in sorted(geoid2fips.keys()):
            country_code, fipscode = geoid2fips[geoname_id]
            writer.writerow((geoname_id, country_code, fipscode))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input-file', required=True, help='input csv fips 10-4 data file (data.csv)')
    parser.add_argument('-o', '--output-file', required=True, help='output csv file (geoname2fips.csv)')
    parser.add_argument('-l', '--location-file', required=True, help='location file csv (GeoLite2-City-Locations-en.csv)')
    opts = parser.parse_args()

    geoid2fips = {}
    cities = defaultdict(dict)
    sub2 = defaultdict(dict)
    region_divisions = DIVISION_OVERRIDE.copy()

    _locations = parse_locations()
    _fips = parse_fips()
    correlate(_locations, _fips)
    writecsv()

    # import json
    # with open('regions.json', 'w', encoding='utf-8') as f:
    #    json.dump(_fips, f, sort_keys=True, indent=4, ensure_ascii=False)
