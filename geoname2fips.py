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

import re
import csv
import argparse
from typing import Pattern

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
    'CONGO': 'CG',
    'COOK ISLANDS': 'CW',
    'CORAL SEA ISLANDS': 'CR',
    'COSTA RICA': 'CS',
    'IVORY COAST': 'IV',
    'CROATIA': 'HR',
    'CUBA': 'CU',
    'CYPRUS': 'CY',
    'CZECHIA': 'EZ',
    'DEMOCRATIC REPUBLIC OF TIMOR-LESTE': 'TT',
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
    'GUINEA-BISSAU': 'PU',
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
    'MACEDONIA': 'MK',
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
    'PALESTINE': 'GZ',
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
    'REPUBLIC OF KOREA': 'KS',
    'REPUBLIC OF LITHUANIA': 'LH',
    'REPUBLIC OF MOLDOVA': 'MD',
    'REPUBLIC OF CONGO': 'CF',
    'ROMANIA': 'RO',
    'RUSSIA': 'RS',
    'RWANDA': 'RW',
    'RÉUNION': 'RE',
    'SAINT BARTHÉLEMY': 'TB',
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
    'SÃO TOMÉ AND PRÍNCIPE': 'TP',
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
    'U.S. VIRGIN ISLANDS': 'VQ',
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
    'ÅLAND',
    'BONAIRE, SINT EUSTATIUS, AND SABA',
    'CURAÇAO',
    'SINT MAARTEN',  # maybe NL?
    'U.S. MINOR OUTLYING ISLANDS',

    # empty
    'AMERICAN SAMOA',
    'COOK ISLANDS',

    # wip
    'CROATIA',
    'CUBA',
    'CYPRUS',
    'CZECHIA',
    'DEMOCRATIC REPUBLIC OF TIMOR-LESTE',
    'DENMARK',
    'DJIBOUTI',
    'DOMINICAN REPUBLIC',
    'ECUADOR',
    'EGYPT',
    'EL SALVADOR',
    'EQUATORIAL GUINEA',
    'ERITREA',
    'ESTONIA',
    'ESWATINI',
    'ETHIOPIA',
    'FEDERATED STATES OF MICRONESIA',
    'FINLAND',
    'FRENCH POLYNESIA',
    'FRENCH SOUTHERN TERRITORIES',
    'GABON',
    'GAMBIA',
    'GEORGIA',
    'GERMANY',
    'GREECE',
    'GREENLAND',
    'GRENADA',
    'GUATEMALA',
    'GUINEA',
    'GUINEA-BISSAU',
    'HAITI',
    'HASHEMITE KINGDOM OF JORDAN',
    'HONDURAS',
    'HONG KONG',
    'HUNGARY',
    'ICELAND',
    'INDIA',
    'INDONESIA',
    'IRAN',
    'IRAQ',
    'IRELAND',
    'ISRAEL',
    'IVORY COAST',
    'JAMAICA',
    'JAPAN',
    'KAZAKHSTAN',
    'KENYA',
    'KUWAIT',
    'KYRGYZSTAN',
    'LAOS',
    'LATVIA',
    'LEBANON',
    'LIBERIA',
    'LIBYA',
    'LUXEMBOURG',
    'MACAO',
    'MACEDONIA',
    'MALAWI',
    'MALAYSIA',
    'MALDIVES',
    'MALI',
    'MALTA',
    'MARSHALL ISLANDS',
    'MAURITANIA',
    'MEXICO',
    'MONGOLIA',
    'MONTENEGRO',
    'MOROCCO',
    'MOZAMBIQUE',
    'NAMIBIA',
    'NEPAL',
    'NETHERLANDS',
    'NEW CALEDONIA',
    'NEW ZEALAND',
    'NICARAGUA',
    'NIGER',
    'NIGERIA',
    'NORTH KOREA',
    'NORTHERN MARIANA ISLANDS',
    'NORWAY',
    'OMAN',
    'PAKISTAN',
    'PALAU',
    'PALESTINE',
    'PANAMA',
    'PAPUA NEW GUINEA',
    'PARAGUAY',
    'PERU',
    'PHILIPPINES',
    'POLAND',
    'PORTUGAL',
    'QATAR',
    'REPUBLIC OF CONGO',
    'REPUBLIC OF KOREA',
    'REPUBLIC OF LITHUANIA',
    'REPUBLIC OF MOLDOVA',
    'ROMANIA',
    'RUSSIA',
    'RWANDA',
    'RÉUNION',
    'SAINT BARTHÉLEMY',
    'SAINT LUCIA',
    'SAINT PIERRE AND MIQUELON',
    'SAINT VINCENT AND GRENADINES',
    'SAN MARINO',
    'SAUDI ARABIA',
    'SENEGAL',
    'SERBIA',
    'SEYCHELLES',
    'SIERRA LEONE',
    'SINGAPORE',
    'SLOVAKIA',
    'SLOVENIA',
    'SOLOMON ISLANDS',
    'SOMALIA',
    'SOUTH AFRICA',
    'SPAIN',
    'SRI LANKA',
    'ST KITTS AND NEVIS',
    'SUDAN',
    'SURINAME',
    'SVALBARD AND JAN MAYEN',
    'SWEDEN',
    'SWITZERLAND',
    'SYRIA',
    'SÃO TOMÉ AND PRÍNCIPE',
    'TAIWAN',
    'TAJIKISTAN',
    'TANZANIA',
    'THAILAND',
    'TOKELAU',
    'TONGA',
    'TRINIDAD AND TOBAGO',
    'TUNISIA',
    'TURKEY',
    'TURKMENISTAN',
    'TUVALU',
    'U.S. VIRGIN ISLANDS',
    'UGANDA',
    'UKRAINE',
    'UNITED ARAB EMIRATES',
    'UNITED KINGDOM',
    'URUGUAY',
    'UZBEKISTAN',
    'VENEZUELA',
    'VIETNAM',
    'WALLIS AND FUTUNA',
    'YEMEN',
    'ZAMBIA'
)

REGION_IGNORE = {
    'AZERBAIJAN': ('AGHSU RAYON',),

    'BAHRAIN': ('AL JASRAH', 'AL MARKH', 'AR RIFA ASH SHAMALI', 'AZ ZALLAQ', 'BANI JAMRAH', 'DAR KULAYB', 'JAWW',
                'NORTHERN', 'OIL CITY', 'SOUTHERN GOVERNORATE'),

    'BOTSWANA': ('CHOBE DISTRICT', 'KASANE', 'JWANENG', 'LOBATSE'),

    'BAHAMAS': (
        'ANDROS TOWN', 'BEHRING POINT', 'BIGHT', 'CENTRAL ABACO DISTRICT', 'CENTRAL ANDROS DISTRICT',
        'EAST GRAND BAHAMA DISTRICT', 'GRAND CAY DISTRICT', 'CROWN HAVEN', 'GRAND CAY', 'HOPE TOWN DISTRICT',
        'MOORES ISLAND DISTRICT', 'NICHOLLS TOWN', 'NORTH ABACO DISTRICT', 'NORTH ANDROS DISTRICT', 'NORTH ELEUTHERA',
        'SAN ANDROS', 'SPANISH WELLS', 'SPANISH WELLS DISTRICT', 'SWEETING CAY', 'WEST END',
        'WEST GRAND BAHAMA DISTRICT'
    ),

    'BHUTAN': ('GASA', 'TRASHI YANGTSE', 'TRASHI YANGSTE'),  # wtf subst not working?

    'BOSNIA AND HERZEGOVINA': ('BRCKO', 'BRČKO', 'DURDEVIK'),

    'BURKINA FASO': ('CASCADES REGION', 'CENTRE', 'CENTRE-EST', 'CENTRE-NORD', 'CENTRE-OUEST', 'EST', 'HAUTS-BASSINS',
                     'NORD', 'PLATEAU-CENTRAL', 'SUD-OUEST'),

    'CAMBODIA': ('KAMPRAEUS', 'TBOUNG KHMUM'),

    'CHILE': ('BULNES', 'CHILLAN', 'CHILLAN VIEJO', 'COELEMU', 'COIHUECO', 'FRUTILLAR', 'PINTO', 'QUILLON', 'QUIRIHUE',
              'SAN CARLOS', 'SAN FABIAN DE ALICO', 'SAN IGNACIO', 'ÑUBLE'),

    'CONGO': ('BOENDE',)
}

REGION_REPLACE = {
    'AE1': {
        'ABŪ Z̧ABY': 'ABU DHABI',
        'ASH SHĀRIQAH': 'ASH SHARIQAH',
        'DUBAYY': 'DUBAI'
    },
    'AF': {
        'KABOL': 'KABUL',
        'KANDAHAR KANDAHAR': 'KANDAHAR'
    },
    'AG': {
        'AIN DEFLA': 'AÏN DEFLA',
        'AIN TEMOUCHENT': 'AÏN TÉMOUCHENT',
        'ALGER': 'ALGIERS',
        'BECHAR': 'BÉCHAR',
        'BEJAIA': 'BÉJAÏA',
        'BORDJ BOU ARRERIDJ': 'BORDJ BOU ARRÉRIDJ',
        'SETIF': 'SÉTIF',
        'SIDI BEL ABBES': 'SIDI BEL ABBÈS',
        'TAMANGHASSET': 'TAMANRASSET',
        'TEBESSA': 'TÉBESSA',
    },
    'AJ': {
        'ABŞERON': 'ABSHERON',
        'BAKI': 'BAKU CITY',
        'GƏNCƏ': 'GANJA CITY',
        'NAXÇIVAN': 'NAKHICHEVAN',
        'YARDIMLI': 'YARDYMLI',
        'ŞƏKI': 'SHAKI CITY',
        'SUMQAYIT': 'SUMQAYIT CITY',
    },
    'AL': {
        'BERAT': 'BERATIT',
        'DIBËR': 'DIBRES',
        'DURRËS': 'DURRESIT',
        'ELBASAN': 'ELBASANIT',
        'FIER': 'FIERIT',
        'TIRANË': 'TIRANA',
        'GJIROKASTËR': 'GJIROKASTRES',
        'KORÇË': 'KORCES',
        'LEZHË': 'LEZHES',
        'SHKODËR': 'SHKODRES',
        'VLORË': 'VLORES'
    },
    'AM': {
        'LORRI': 'LORI'
    },
    'AN': {
        'SANT JULIA DE LORIA': 'SANT JULIÀ DE LORIA'
    },
    'AO': {
        'BIE': 'BÍE',
        'CUANDO CUBANGO': 'CUANDO COBANGO',
        'CUANZA SUL': 'KWANZA SUL',
        'HUILA': 'HUÍLA',
        'LUNDA NORTE': 'LUANDA NORTE',
        'UIGE': 'UÍGE'
    },
    'AR': {
        'TIERRA DEL FUEGO ANTÁRTIDA E ISLAS DEL ATLÁNTICO SUR': 'TIERRA DEL FUEGO'
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
        'AL MUḨARRAQ': 'MUHARRAQ',
        'AL ĀŞIMAH': 'MANAMA',
        'AR RIFA WA AL MINTAQAH AL JANUBIYAH': 'AR RIFA'
    },
    'BC': {
        'CENTRAL': 'CENTRAL DISTRICT',
        'FRANCISTOWN': 'CENTRAL',
        'SOUTH-EAST': 'GABORONE',
        'SOUTHERN': 'NGWAKETSI',
        'NORTH WEST': 'NORTH-WEST'
    },
    'BD': {
        'HAMILTON': 'HAMILTON CITY',
    },
    'BE': {
        'BRABANT WALLON': 'WALLONIA',
        'BRUSSELS HOOFDSTEDELIJK GEWEST/RÉGION DE BRUXELLES-CAPITALE': 'BRUSSELS CAPITAL',
        'VLAMMS-BRABANT': 'FLANDERS'
    },
    'BF': {
        # 'FREEPORT': 'CITY OF FREEPORT',
        'NICHOLLSTOWN AND BERRY ISLANDS': 'BERRY ISLANDS',
        'SANDY POINT': 'SOUTH ABACO'
    },
    'BG': {
        'BARISĀL': 'BARISAL',
        'RANGPUR DIVISION': 'RAJSHAHI',
        'RĀJSHĀHI': 'RAJSHAHI',
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
    'BP1': {
        'CHOISEUL': 'HONIARA',
        'MAKIRA': 'MAKIRA-ULAWA'
    },
    'BR': {
        'DISTRITO FEDERAL': 'FEDERAL DISTRICT',
        'PARAIBA': 'PARAÍBA'
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
        'KŬRDZHALI': 'KARDZHALI',
        'SOFIYA': 'SOFIA',
        'SOFIYA-GRAD': 'SOFIA-CAPITAL',
        'TŬRGOVISHTE': 'TARGOVISHTE',
        'VELIKO TŬRNOVO': 'VELIKO TARNOVO'
    },
    'CA': {
        'YUKON TERRITORY': 'YUKON'
    },
    'CB': {
        'BÂNTÉAY MÉAN CHEĂY': 'BANTEAY MEANCHEY',
        'BĂTDÂMBÂNG': 'BATTAMBANG',
        'KAMPONG SPOE': 'KAMPONG SPEU',
        'KAMPONG THUM': 'KAMPONG THOM',
        'KAOH KONG': 'KOH KONG',
        'KRACHEH': 'KRATIE',
        'KÂMPÔT': 'KAMPOT',
        'KÊB': 'KEP',
        'MONDOL KIRI': 'MONDOLKIRI',
        'PAILĬN': 'PAILIN',
        'PHNUM PÉNH': 'PHNOM PENH',
        'POUTHISAT': 'PURSAT',
        'PREĂH SEIHÂNŬ': 'PREAH SIHANOUK',
        'RÔTÂNĂH KIRI': 'RATANAKIRI',
        'SIĔM RÉAB': 'SIEM REAP',
        'STOENG TRENG': 'STUNG TRENG',
        'TAKEV': 'TAKEO',
        'ŎTDÂR MÉAN CHEĂY': 'OTAR MEANCHEY'
    },
    'CD': {
        'MAYO-KÉBBI OUEST': 'MAYO-KEBBI OUEST',
        'OUADDAÏ': 'OUADAÏ'
    },
    'CE1': {
        'AMPARAI': 'AMPARA',
        'KEGALLA': 'KEGALLE'
    },
    'CG': {
        'NORD-KIVU': 'NORD KIVU',
        'SUD-KIVU': 'SOUTH KIVU',
        'KINSHASA': 'KINSHASA CITY'
    },
    'CH': {
        'NEI MONGOL INNER MONGOLIA': 'INNER MONGOLIA AUTONOMOUS REGION',
        'XIZANG TIBET': 'TIBET',
        'NINGXIA NINGXIA': 'NINGXIA HUI AUTONOMOUS REGION'
    },
    'CI': {
        'BIO-BIO': 'BIOBIO',
        'AISEN DEL GENERAL CARLOS IBANEZ DEL CAMPO': 'AYSÉN',
        'REGION METROPOLITANA': 'SANTIAGO METROPOLITAN',
        'LIBERTADOR GENERAL BERNARDO OHIGGINS': 'OHIGGINS REGION',
        'MAGALLANES Y DE LA ANTÁRTICA CHILENA': 'REGION OF MAGALLANES'
    },
    'CM': {
        'OUEST WEST': 'WEST REGION',
        'NORD-OUEST NORTH-WEST': 'NORTH-WEST REGION',
        'SUD-OUEST SOUTH-WEST': 'SOUTH-WEST REGION',
        'SUD SOUTH': 'SOUTH'
    },
    'CN': {
        'MOHELI': 'MOHÉLI',
        'ANJOUAN': 'NDZUWANI'
    },
    'CO': {
        'ATLANTICO': 'ATLÁNTICO',
        'DISTRITO CAPITAL': 'BOGOTA D.C.'
    },
    'CT': {
        'NANA-MAMBERE': 'NANA-MAMBÉRÉ',
        'OUHAM-PENDE': 'OUHAM-PENDÉ',
        'NANA-GRÉBINGUI': 'NANA-GRÉBIZI'
    },
    'CV': {
        'CAPE VERDE': 'CABO VERDE',
        'RIBEIRA GRANDE': 'RIBEIRA GRANDE DE SANTIAGO',
        'SANTA CRUZ': 'SÃO LOURENÇO DOS ÓRGÃOS',    # since 2005
        'SAO VICENTE': 'SÃO VICENTE',
    },
    'FR': {
        'CENTRE': 'CENTRE-VAL DE LOIRE',
        'ILE-DE-FRANCE': 'ÎLE-DE-FRANCE',
        'BRETAGNE': 'BRITTANY',
        'CORSE': 'CORSICA',
        'LIMOUSIN': 'LIMOSINE'
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
        'FRIULI-VENEZIA GIULIA': 'FRIULI VENEZIA GIULIA',
        'VALLE DAOSTA': 'AOSTA VALLEY'
    },
    'UV': {
        'MOUHOUN': 'BOUCLE DU MOUHOUN'
    }
}

REGION_TO_PARENT = {
    'BY': {
        'BUJUMBURA MAIRIE PROVINCE': 'BUJUMBURA',
        'BUJUMBURA RURAL PROVINCE': 'BUJUMBURA',
        'ISALE': 'BUJUMBURA',
        'ROHERO': 'BUJUMBURA',
        'RUMONGE': 'BUJUMBURA',  # since 2015
    },
    'CD': {
        'AM DJARASS': 'BORKOU-ENNEDI-TIBESTI',
        'AOZOU': 'BORKOU-ENNEDI-TIBESTI',
        'BORKOU REGION': 'BORKOU-ENNEDI-TIBESTI',
        'ENNEDI-EST': 'BORKOU-ENNEDI-TIBESTI',
        'ENNEDI-OUEST': 'BORKOU-ENNEDI-TIBESTI',
        'FADA': 'BORKOU-ENNEDI-TIBESTI',
        'FAYA-LARGEAU': 'BORKOU-ENNEDI-TIBESTI',
        'TIBESTI REGION': 'BORKOU-ENNEDI-TIBESTI',
        'BARH EL GAZEL': 'KANEM',  # since 2008
        'SALAL': 'KANEM'
    },
    'CG': {
        'AKETI': 'ORIENTALE',
        'BAS UELE': 'ORIENTALE',
        'BUNIA': 'ORIENTALE',
        'HAUT UELE': 'ORIENTALE',
        'HAUT-LOMANI': 'KATANGA',
        'INONGO': 'BANDUNDU',
        'ISIRO': 'ORIENTALE',
        'ITURI': 'ORIENTALE',
        'KASAI': 'KASAÏ-OCCIDENTAL',
        'KIKWIT': 'BANDUNDU',
        'KOLWEZI': 'KATANGA',
        'KONGOLO': 'KATANGA',
        'KWILU': 'BANDUNDU',
        'LODJA': 'KASAÏ-ORIENTAL',
        'LOMAMI': 'KATANGA',
        'LUALABA': 'KATANGA',
        'LUBUMBASHI': 'KATANGA',
        'LUEBO': 'KASAÏ-OCCIDENTAL',
        'MAI NDOMBE': 'BANDUNDU',
        'MALUKU': 'ÉQUATEUR',
        'MONGALA': 'ÉQUATEUR',
        'MWENE-DITU': 'KATANGA',
        'PROVINCE DU SUD-UBANGI': 'ÉQUATEUR',
        'SANKURU': 'KASAÏ-ORIENTAL',
        'SUNGU-MONGA': 'KATANGA',
        'TANGANIKA': 'KATANGA',
        'TSHOPO': 'ORIENTALE',
        'TSHUAPA': 'ÉQUATEUR',
        'UPPER KATANGA': 'KATANGA',
        'YANGA-LIBENGE': 'ÉQUATEUR',
        'YANGAMBI': 'ORIENTALE'
    },
    'CV': {
        'PICOS': 'SANTA CATARINA',  # since 2005
        'COVA FIGUEIRA': 'SÃO FILIPE',
        'PORTO NOVO': 'RIBEIRA GRANDE',
        'RIBEIRA BRAVA': 'SAO NICOLAU',
        'QUEIMADAS': 'SAO NICOLAU',
        'SANTA CATARINA DO FOGO': 'SANTA CATARINA',
        'SÃO SALVADOR DO MUNDO': 'SANTA CATARINA',  # since 2005
        'TARRAFAL DE SAO NICOLAU': 'SAO NICOLAU',
        'TARRAFAL DE SÃO NICOLAU': 'SAO NICOLAU',
        'VILA DA RIBEIRA BRAVA': 'SAO NICOLAU'
    },
    'FR': {
        # Nouvelle-Aquitaine
        'AAST': 'AQUITAINE',
        'ABIDOS': 'AQUITAINE',
        'ABITAIN': 'AQUITAINE',
        'ABZAC': 'AQUITAINE',
        'ADRIERS': 'POITOU-CHARENTES',
        'AFFIEUX': 'LIMOSINE',
        # Bourgogne-Franche-Comté
        'ABBANS-DESSUS': 'FRANCHE-COMTE',
        'ABBEVILLERS': 'FRANCHE-COMTE',
        'ABERGEMENT-LA-RONCE': 'FRANCHE-COMTE',
        'ACCOLANS': 'FRANCHE-COMTE',
        'ACCOLAY': 'BOURGOGNE',
        # Occitanie
        'ABEILHAN': 'LANGUEDOC-ROUSSILLON',
        'ADAST': 'MIDI-PYRENEES',
        'ADE': 'MIDI-PYRENEES',
        'ADISSAN': 'LANGUEDOC-ROUSSILLON',
        # Hauts-de-France
        'ABBECOURT': 'PICARDIE',
        'ABBEVILLE': 'PICARDIE',
        'ABBEVILLE-SAINT-LUCIEN': 'PICARDIE',
        'ABLAIN-SAINT-NAZAIRE': 'NORD-PAS-DE-CALAIS',
        'ABSCON': 'NORD-PAS-DE-CALAIS',
        'ACHERY': 'PICARDIE',
        'ACHEVILLE': 'NORD-PAS-DE-CALAIS',
        'ACHICOURT': 'NORD-PAS-DE-CALAIS',
        'ACHIET-LE-GRAND': 'NORD-PAS-DE-CALAIS',
        'ACHY': 'PICARDIE',
        'ACY': 'PICARDIE',
        'ADINFER': 'NORD-PAS-DE-CALAIS',
        'AFFRINGUES': 'NORD-PAS-DE-CALAIS',
        # Grand Est
        'ABLANCOURT': 'CHAMPAGNE-ARDENNE',
        'ABRESCHVILLER': 'LORRAINE',
        'ACHEN': 'LORRAINE',
        'ACHENHEIM': 'ALSACE',
        'ADAINCOURT': 'LORRAINE',
        'ADAMSWILLER': 'ALSACE',
        # Auvergne-Rhône-Alpes
        'ABOEN': 'RHONE-ALPES',
        'ABONDANCE': 'RHONE-ALPES',
        'ABREST': 'AUVERGNE',
        'AFFOUX': 'RHONE-ALPES',
        # NORMANDY
        'ACON': 'HAUTE-NORMANDIE',
        'ACQUEVILLE': 'BASSE-NORMANDIE',
        'ACQUIGNY': 'HAUTE-NORMANDIE',
    },
    'UV': {
        'BANFORA': 'COMOÉ',
        'BOBO-DIOULASSO': 'HOUET',
        'DIAPAGA': 'TAPOA',
        'DIÉBOUGOU': 'BOUGOURIBA',
        'KONGOUSSI': 'BAM',
        'KOUDOUGOU': 'BOULKIEMDE',
        'OUAGADOUGOU': 'KADIOGO',
        'OUAHIGOUYA': 'YATENGA',
        'TENKODOGO': 'BOULGOU',
        'ZINIARÉ': 'OUBRITENGA'
    }
}

DIVISION_OVERRIDE = {
    'AL': 'QARKU I',                                            # Albania
    'AC': 'PARISH OF',                                          # Antigua And Barbuda
    'AR': 'F.D.',                                               # Argentina
    'BN': 'DEPARTMENT',                                         # Benin
    'BT': 'DZONGKHAG',                                          # Bhutan
    'BL': 'DEPARTAMENTO DE',                                    # Bolivia
    'BU': 'OBLAST',                                             # Bulgaria
    'CI': re.compile(r'(REGION DE LA |REGION DE |REGION DEL | REGION)'),
    'CM': 'REGION',                                             # Cameroon
    'CO': re.compile(r'(DEPARTAMENTO DE.*?\s|\sDEPARTMENT)'),   # Colombia
    'CS': 'PROVINCIA DE'
}


re_par1 = re.compile(r'\([^()]*\)')
re_par2 = re.compile(r'\[[^()]*\]')


# FIXME: better
def cleanup(text: str) -> str:
    text = text.upper()
    text = re_par1.sub('', text)
    text = re_par2.sub('', text)
    for quote in "ʼ’‘ʻ`'":
        text = text.replace(quote, '')
    for part in ('THE ', ' THE', 'CITY OF '):
        text = text.replace(part, '')
    text = text.replace('  ', ' ')
    return text.strip()


def search(rn, rd, c, e):
    names = set()
    names.add(rn)

    if isinstance(rd, Pattern):
        names.add(rd.sub('', rn))
    elif isinstance(rd, str):
        names.add('{} OF {}'.format(rd, rn))
        names.add('{} {}'.format(rn, rd))
        names.add('{} {}'.format(rd, rn))

        if rd in rn:
            rn = rn.replace(rd, '').strip()
            names.add(rn)

    import os
    if c == os.environ.get('C'):
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


def correlate(locations, fips):
    for country in sorted(locations.keys()):
        fips_country_code = FIPS_COUNTRIES.get(country)
        if fips_country_code is None and country not in COUNTRY_IGNORE:
            raise Exception('Country {} not found in fips country table'.format(country))

        if fips_country_code and fips_country_code not in fips:
            for location in locations[country].values():
                fill(location, fips_country_code, '')
            continue

        if country in COUNTRY_IGNORE:
            continue

        entry = fips[fips_country_code]

        for region_name in sorted(locations[country].keys()):
            ignore_region = country in REGION_IGNORE and region_name in REGION_IGNORE[country]
            region_division = region_divisions.get(fips_country_code)

            location = locations[country][region_name]

            region_name = REGION_TO_PARENT.get(fips_country_code, {}).get(region_name, region_name)

            region_by_city = ''
            found = search(region_name, region_division, fips_country_code, entry)
            if found is None:
                city = search(region_name, region_division, fips_country_code, cities[country])
                if city is not None:
                    region_by_city = cities[country][city]
                    region_by_city = REGION_REPLACE.get(fips_country_code, {}).get(region_by_city, region_by_city)
                    # ignore_region = country in REGION_IGNORE and region_by_city in REGION_IGNORE[country]
                    found = search(region_by_city, region_division, fips_country_code, entry)

            if found is None:
                if ignore_region:
                    fill(location, fips_country_code, '00')
                    continue
                continue
                raise Exception('Region {} ({}) not found in {} ({})'.format(region_name, region_by_city, country,
                                                                             fips_country_code))

            if ignore_region:
                raise Exception('Ignored region found: {} in {}'.format(region_name, country))

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
    parser.add_argument('-i', '--input-file', required=True, help='input csv fips 10-4 data file')
    parser.add_argument('-o', '--output-file', required=True, help='output csv file')
    parser.add_argument('-l', '--location-file', required=True, help='location file csv')
    opts = parser.parse_args()

    geoid2fips = {}
    cities = defaultdict(dict)
    region_divisions = DIVISION_OVERRIDE.copy()

    _locations = parse_locations()
    _fips = parse_fips()
    correlate(_locations, _fips)
    writecsv()

    # import json
    # with open('regions.json', 'w', encoding='utf-8') as f:
    #    json.dump(_fips, f, sort_keys=True, indent=4, ensure_ascii=False)
