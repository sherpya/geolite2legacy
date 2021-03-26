#!/usr/bin/env python
# The MIT License (MIT)
#
# Copyright (c) 2015 Mark Teodoro
# Copyright (c) 2018-2019 Gianluigi Tiesi
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

from __future__ import print_function

import os
import re
import sys
import csv
import struct
import codecs
import logging
import argparse

# python 2 ipaddr
try:
    from ipaddr import IPNetwork
# python3 built-in ipaddress
except:
    from ipaddress import ip_network as IPNetwork

from time import time
from zipfile import ZipFile
from collections import defaultdict

from pygeoip_const import *

re_words = re.compile(r'\W+', re.U)


cc_idx = dict((cc.lower(), i) for i, cc in enumerate(COUNTRY_CODES))
cc_idx['cw'] = cc_idx['an']     # netherlands antilles / curacao
cc_idx['uk'] = cc_idx['gb']     # uk / great britain
cc_idx['sx'] = cc_idx['fx']     # st. martin?
cc_idx['xk'] = cc_idx['rs']     # kosovo -> serbia

continent_codes = {'AS': 'AP'}

geoname2fips = {}
output_encoding = 'utf-8'
datfilecomment = ''


def serialize_text(text):
    try:
        return text.encode(output_encoding)
    except UnicodeEncodeError:
        print('Warning cannot encode {!r} using {}'.format(text, output_encoding))
        return text.encode(output_encoding, 'replace')


if sys.version_info[0] == 2:
    # noinspection PyShadowingBuiltins,PyUnresolvedReferences
    range = xrange

    def decode_text(text):
        return text.decode('utf-8')

    # noinspection PyPep8Naming,PyUnusedLocal
    def TextIOWrapper(f, encoding=None):
        return f
else:
    from io import TextIOWrapper

    def decode_text(text):
        return text


class RadixTreeNode(object):
    __slots__ = ['segment', 'lhs', 'rhs']

    def __init__(self, segment):
        self.segment = segment
        self.lhs = None
        self.rhs = None


class RadixTree(object):
    seek_depth = -1
    edition = -1
    reclen = -1
    segreclen = -1

    def __init__(self, debug=False):
        self.debug = debug
        self.netcount = 0
        self.segments = [RadixTreeNode(0)]
        self.data_offsets = {}
        self.data_segments = []
        self.cur_offset = 1

    def __setitem__(self, net, data):
        self.netcount += 1
        # python2 ipaddr
        try:
            inet = int(net)
        # python3 built-in ipaddress
        except:
            inet = int(net.network_address)
        node = self.segments[0]
        for depth in range(self.seek_depth, self.seek_depth - (net.prefixlen - 1), -1):
            if inet & (1 << depth):
                if not node.rhs:
                    node.rhs = RadixTreeNode(len(self.segments))
                    self.segments.append(node.rhs)
                node = node.rhs
            else:
                if not node.lhs:
                    node.lhs = RadixTreeNode(len(self.segments))
                    self.segments.append(node.lhs)
                node = node.lhs

        if data not in self.data_offsets:
            self.data_offsets[data] = self.cur_offset
            enc_data = self.encode(*data)
            self.data_segments.append(enc_data)
            self.cur_offset += (len(enc_data))

        if self.debug:
            # store net after data for easier debugging
            data = data, net

        if inet & (1 << self.seek_depth - (net.prefixlen - 1)):
            node.rhs = data
        else:
            node.lhs = data

    def gen_nets(self, codes, outfile):
        raise NotImplementedError

    def load(self, locationsfile, outfile):
        locations = {}
        if locationsfile:
            for row in csv.DictReader(locationsfile):
                geoname_id = row['geoname_id']
                # remap continent codes according to https://dev.maxmind.com/geoip/legacy/codes/iso3166/
                continent_code = row['continent_code']
                row['continent_code'] = continent_codes.get(continent_code, continent_code)
                locations[geoname_id] = row

        for nets, data in self.gen_nets(locations, outfile):
            for net in nets:
                self[net] = data

    def dump_node(self, node):
        if not node:
            # empty leaf
            return '--'
        elif isinstance(node, RadixTreeNode):
            # internal node
            return node.segment
        else:
            # data leaf
            data = node[0] if self.debug else node
            return '%d %s' % (len(self.segments) + self.data_offsets[data], node)

    def dump(self):
        for node in self.segments:
            print(node.segment, [self.dump_node(node.lhs), self.dump_node(node.rhs)])

    def encode(self, *args):
        raise NotImplementedError

    def encode_rec(self, rec, reclen):
        """encode rec as 4-byte little-endian int, then truncate it to reclen"""
        assert (reclen <= 4)
        return struct.pack('<I', rec)[:reclen]

    def serialize_node(self, node):
        if not node:
            # empty leaf
            rec = len(self.segments)
        elif isinstance(node, RadixTreeNode):
            # internal node
            rec = node.segment
        else:
            # data leaf
            data = node[0] if self.debug else node
            rec = len(self.segments) + self.data_offsets[data]
        return self.encode_rec(rec, self.reclen)

    def serialize(self, f):
        if len(self.segments) >= 2 ** (8 * self.segreclen):
            logging.warning('too many segments for final segment record size!')

        for node in self.segments:
            f.write(self.serialize_node(node.lhs))
            f.write(self.serialize_node(node.rhs))

        f.write(struct.pack('B', 42))  # So long, and thanks for all the fish!
        f.write(b''.join(self.data_segments))

        f.write(datfilecomment.encode('ascii'))  # .dat file comment - can be anything
        f.write(struct.pack('B', 0xff) * 3)
        f.write(struct.pack('B', self.edition))
        f.write(self.encode_rec(len(self.segments), self.segreclen))


class ASNRadixTree(RadixTree):
    seek_depth = 31
    edition = ASNUM_EDITION
    reclen = STANDARD_RECORD_LENGTH
    segreclen = SEGMENT_RECORD_LENGTH

    def gen_nets(self, locations, infile):
        for row in csv.DictReader(infile):
            nets = [IPNetwork(row['network'])]
            org = decode_text(row['autonomous_system_organization'])
            asn = row['autonomous_system_number']
            entry = u'AS{} {}'.format(asn, org)
            yield nets, (serialize_text(entry),)

    def encode(self, data):
        return data + b'\0\0\0'


class ASNv6RadixTree(ASNRadixTree):
    seek_depth = 127
    edition = ASNUM_EDITION_V6
    reclen = STANDARD_RECORD_LENGTH
    segreclen = SEGMENT_RECORD_LENGTH


class CityRev1RadixTree(RadixTree):
    seek_depth = 31
    edition = CITY_EDITION_REV1
    reclen = STANDARD_RECORD_LENGTH
    segreclen = SEGMENT_RECORD_LENGTH

    def gen_nets(self, locations, infile):
        for row in csv.DictReader(infile):
            location = locations.get(row['geoname_id'])
            if location is None:
                continue

            nets = [IPNetwork(row['network'])]
            country_iso_code = location['country_iso_code'] or location['continent_code']
            fips_code = geoname2fips.get(location['geoname_id'])
            if fips_code is None:
                logging.debug('Missing fips-10-4 for {}'.format(location['subdivision_1_name']))
                fips_code = '00'
            else:
                logging.debug('fips-10-4 for {} is {}'.format(location['subdivision_1_name'], fips_code))

            yield nets, (country_iso_code,
                         serialize_text(fips_code),  # region
                         serialize_text(decode_text(location['city_name'])),
                         serialize_text(row['postal_code']),
                         row['latitude'],
                         row['longitude'],
                         location['metro_code'],
                         '')  # area_code

    def encode(self, country, region, city, postal_code, lat, lon, metro_code, area_code):
        def str2num(num, ntype):
            return ntype(num) if num else ntype(0)

        country = country.lower()
        lat, lon = round(str2num(lat, float), 4), round(str2num(lon, float), 4)
        metro_code, area_code = str2num(metro_code, int), str2num(area_code, int)

        buf = []
        try:
            buf.append(struct.pack('B', cc_idx[country]))
        except KeyError:
            logging.warning("'%s': missing country. update const.COUNTRY_CODES?", country)
            buf.append(struct.pack('B', cc_idx['']))
        buf.append(b'\0'.join((region, city, postal_code)))
        buf.append(b'\0')
        buf.append(self.encode_rec(int((lat + 180) * 10000), 3))
        buf.append(self.encode_rec(int((lon + 180) * 10000), 3))
        if (metro_code or area_code) and country == 'us':
            buf.append(self.encode_rec(metro_code * 1000 + area_code, 3))
        else:
            buf.append(b'\0\0\0')
        return b''.join(buf)


class CityRev1v6RadixTree(CityRev1RadixTree):
    seek_depth = 127
    edition = CITY_EDITION_REV1_V6
    reclen = STANDARD_RECORD_LENGTH
    segreclen = SEGMENT_RECORD_LENGTH


class CountryRadixTree(RadixTree):
    seek_depth = 31
    edition = COUNTRY_EDITION
    reclen = STANDARD_RECORD_LENGTH
    segreclen = SEGMENT_RECORD_LENGTH

    def gen_nets(self, locations, infile):
        for row in csv.DictReader(infile):
            location = locations.get(row['geoname_id'])
            if location is None:
                continue

            nets = [IPNetwork(row['network'])]
            country_iso_code = location['country_iso_code'] or location['continent_code']
            yield nets, (country_iso_code,)

    def encode(self, cc):
        # unused
        return ''

    def serialize_node(self, node):
        if not node:
            # empty leaf
            rec = COUNTRY_BEGIN
        elif isinstance(node, RadixTreeNode):
            # internal node
            rec = node.segment
        else:
            # data leaf
            data = node[0] if self.debug else node
            cc = data[0]
            try:
                offset = cc_idx[cc.lower()]
            except KeyError:
                logging.warning("'%s': missing country. update const.COUNTRY_CODES?", cc)
                offset = 0
            # data leaves directly encode cc index as an offset
            rec = COUNTRY_BEGIN + offset
        return self.encode_rec(rec, self.reclen)

    def serialize(self, f):
        for node in self.segments:
            f.write(self.serialize_node(node.lhs))
            f.write(self.serialize_node(node.rhs))

        f.write(struct.pack('B', 0x00) * 3)
        f.write(datfilecomment.encode('ascii'))  # .dat file comment - can be anything
        f.write(struct.pack('B', 0xff) * 3)
        f.write(struct.pack('B', self.edition))
        f.write(self.encode_rec(len(self.segments), self.segreclen))


class Countryv6RadixTree(CountryRadixTree):
    seek_depth = 127
    edition = COUNTRY_EDITION_V6
    reclen = STANDARD_RECORD_LENGTH
    segreclen = SEGMENT_RECORD_LENGTH


RTree = {
    'Country': {'IPv4': CountryRadixTree, 'IPv6': Countryv6RadixTree},
    'City': {'IPv4': CityRev1RadixTree, 'IPv6': CityRev1v6RadixTree},
    'ASN': {'IPv4': ASNRadixTree, 'IPv6': ASNv6RadixTree}
}

Filenames = {
    'Country': {'IPv4': "GeoIP.dat", 'IPv6': "GeoIPv6.dat"},
    'City': {'IPv4': "GeoIPCity.dat", 'IPv6': "GeoIPCityv6.dat"},
    'ASN': {'IPv4': "GeoIPASNum.dat", 'IPv6': "GeoIPASNumv6.dat"}
}


def parse_fips(fipsfile):
    with open(fipsfile) as f:
        for row in csv.DictReader(f):
            geoname2fips[row['geoname_id']] = row['region']
    return geoname2fips


def main():
    global output_encoding, datfilecomment

    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input-file', required=True, help='input zip file containings csv databases')
    parser.add_argument('-o', '--output-file', help='output GeoIP dat file')
    parser.add_argument('-f', '--fips-file', help='geonameid to fips code mappings')
    parser.add_argument('-e', '--encoding', help='encoding to use for the output rather than utf-8')
    parser.add_argument('-d', '--debug', action='store_true', default=False, help='debug mode')
    parser.add_argument('-6', '--ipv6', action='store_const', default='IPv4', const='IPv6', help='use ipv6 database')
    opts = parser.parse_args()

    if opts.encoding:
        try:
            codecs.lookup(opts.encoding)
        except LookupError as e:
            print(e)
            sys.exit(1)
        output_encoding = opts.encoding

    re_entry = re.compile(r'.*?/Geo(?:Lite|IP)2-(?P<database>.*?)-(?P<filetype>.*?)-(?P<arg>.*)\.csv')

    entries = defaultdict(lambda: defaultdict(dict))

    ziparchive = ZipFile(opts.input_file)
    for entry in ziparchive.filelist:
        match = re_entry.match(entry.filename)
        if match is None:
            continue

        db, filetype, arg = match.groups()
        entries[db][filetype][arg] = entry

    if len(entries) != 1:
        print('More than one kind of database found, please check the archive')
        sys.exit(1)

    # noinspection PyUnboundLocalVariable
    datfilecomment = '{} converted to legacy MaxMind DB with geolite2legacy'.format(os.path.dirname(entry.filename))
    dbtype, entries = entries.popitem()

    if dbtype == 'ASN':
        locs = None
    else:
        if not {'Locations', 'Blocks'} <= set(entries.keys()):
            print('Missing Locations or Block files, please check the archive')
            sys.exit(1)

        locs = entries['Locations'].get('en')
        if locs is None:
            print('Selected locale not found in archive')
            sys.exit(1)

        locs = TextIOWrapper(ziparchive.open(locs, 'r'), encoding='utf-8')

    if dbtype not in RTree:
        print('{} not supported'.format(dbtype))
        sys.exit(1)

    r = RTree[dbtype][opts.ipv6](debug=opts.debug)
    blocks = entries['Blocks'].get(opts.ipv6)

    if blocks is None:
        print('The selected block file not found in archive')
        sys.exit(1)

    if dbtype != 'ASN':
        fips_file = opts.fips_file or os.path.join(os.path.dirname(os.path.realpath(__file__)), 'geoname2fips.csv')
        parse_fips(fips_file)

    tstart = time()
    print('Database type {} - Blocks {} - Encoding: {}'.format(dbtype, opts.ipv6, output_encoding))

    r.load(locs, TextIOWrapper(ziparchive.open(blocks, 'r'), encoding='utf-8'))

    if not opts.output_file:
        opts.output_file = Filenames[dbtype][opts.ipv6]
        print('Output file {}'.format(opts.output_file))

    with open(opts.output_file, 'wb') as output:
        r.serialize(output)

    tstop = time()

    print('wrote %d-node trie with %d networks (%d distinct labels) in %d seconds' % (
        len(r.segments), r.netcount, len(r.data_offsets), tstop - tstart))


if __name__ == '__main__':
    main()
