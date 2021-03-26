# geolite2legacy

This tool will convert MaxMind GeoLite2 Database to the old legacy format.

It's based on [mmutils](https://github.com/mteodoro/mmutils.git) but it reads new GeoLite2
directly from zip files containings CSV databases.

You can download databases from
[https://dev.maxmind.com/geoip/geoip2/geolite2/](https://dev.maxmind.com/geoip/geoip2/geolite2/)

It's tested with python/pypy 2.7 and python 3.5+

## Limitations

- Processing may be slow, expecially for City blocks, consider using pypy, it is a lot faster
- Some software may expect iso-8859-1 encoded names, but the script will output utf-8,
  you can force a different encoding e.g. using `-e iso-8859-1` but some name may result wrong  

## Examples

```text
$ ./geolite2legacy.py -i GeoLite2-Country-CSV.zip -f geoname2fips.csv -o GeoIP.dat
Database type Country - Blocks IPv4
wrote 306385-node trie with 300679 networks (251 distinct labels) in 8 seconds

# ./geolite2legacy.py -i GeoLite2-ASN-CSV.zip -o GeoIPASNum.dat 
Database type ASN - Blocks IPv4
wrote 518484-node trie with 417952 networks (62896 distinct labels) in 15 seconds
```

## Usage

```text
usage: geolite2legacy.py [-h] -i INPUT_FILE -o OUTPUT_FILE [-f FIPS_FILE]
                         [-e ENCODING] [-d] [-6]

optional arguments:
  -h, --help            show this help message and exit
  -i INPUT_FILE, --input-file INPUT_FILE
                        input zip file containings csv databases
  -o OUTPUT_FILE, --output-file OUTPUT_FILE
                        output GeoIP dat file
  -f FIPS_FILE, --fips-file FIPS_FILE
                        geonameid to fips code mappings
  -e ENCODING, --encoding ENCODING
                        encoding to use for the output rather than utf-8
  -d, --debug           debug mode
  -6, --ipv6            use ipv6 database
```

```text
The MIT License (MIT)

Copyright (c) 2015 Mark Teodoro
Copyright (c) 2019 Gianluigi Tiesi

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

### Run inside Docker container
1. Build the Docker image:
```bash
docker build -t geolite2legacy .
```
2. This command assmes that you have downloaded the GeoLite2 database to the current directory.
```bash
docker run -it -v $(pwd):/src geolite2legacy:latest -i /src/GeoLite2-Country-CSV.zip -o /src/GeoIP.dat
```

