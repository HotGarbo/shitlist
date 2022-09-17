#!/usr/bin/python3

"""
Shitkicker shitlist generator

IP Geolocation by DB-IP https://db-ip.com'
"""

import csv
import datetime
import gzip
import ipaddress
import urllib.request

_SHITHOLE_STATE = "Texas"

opener = urllib.request.build_opener()
opener.addheaders = [('User-Agent', '')]
urllib.request.install_opener(opener)

now = datetime.datetime.now()
year_month = "%d-%02d" % (now.year, now.month)
url = "https://download.db-ip.com/free/dbip-city-lite-{}.csv.gz".format(year_month)
print("Downloading {}".format(url))
gzfile, _ = urllib.request.urlretrieve(url)

blocks = {
    'v4': [],
    'v6': []
}
with gzip.open(gzfile, 'rt') as f:
    r = csv.reader(f)
    print("Processing CSV")
    for line in r:
        if line[3] == "US" and line[4] == _SHITHOLE_STATE:
            first = ipaddress.ip_address(line[0])
            last = ipaddress.ip_address(line[1])
            for net in ipaddress.summarize_address_range(first, last):
                if net.version == 4:
                    if net.prefixlen > 24:
                        # Assume the whole /24 is shit
                        net = net.supernet(new_prefix=24)
                    blocks['v4'].append(net)
                if net.version == 6:
                    if net.prefixlen > 32:
                        # and the whole /32
                        net = net.supernet(new_prefix=32)
                    blocks['v6'].append(net)

urllib.request.urlcleanup()

# Use collapse_addresses to summarize blocks
for ver, nets in blocks.items():
    with open("{}_{}_{}.txt".format(_SHITHOLE_STATE.lower(), ver, year_month), 'w') as f:
        print("Saving", f.name)
        for net in ipaddress.collapse_addresses(nets):
            f.write("%s\n" % net)
