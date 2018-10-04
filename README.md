geolite2legacy
=======

This tool will convert MaxMind GeoLite2 Database to the old legacy format.

It's based on [mmutils](https://github.com/mteodoro/mmutils.git) but it reads new GeoLite2
directly from zip files containings CSV databases.

You can download databases from
[https://dev.maxmind.com/geoip/geoip2/geolite2/](https://dev.maxmind.com/geoip/geoip2/geolite2/)

It's tested with python 2.7 and python 3.5+

Examples:

```
$ ./geolite2legacy.py -i GeoLite2-Country-CSV.zip -o GeoIP.dat
Database type Country - Blocks IPv4 - Locale en
wrote 306385-node trie with 300679 networks (251 distinct labels) in 8 seconds
```

Complete usage:
```
usage: geolite2legacy.py [-h] -i INPUT_FILE -o OUTPUT_FILE [-d] [-6]
                         [-l LOCALE]

optional arguments:
  -h, --help            show this help message and exit
  -i INPUT_FILE, --input-file INPUT_FILE
                        input zip file containings csv databases
  -o OUTPUT_FILE, --output-file OUTPUT_FILE
                        output GeoIP dat file
  -d, --debug           debug mode
  -6, --ipv6            use ipv6 database
  -l LOCALE, --locale LOCALE
                        locale to use for names
```

```
The MIT License (MIT)

Copyright (c) 2015 Mark Teodoro
Copyright (c) 2018 Gianluigi Tiesi

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
