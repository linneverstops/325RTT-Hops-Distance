import socket
import http.client
import json
from math import ceil, radians, cos, sin, asin, sqrt

MAX_HOPS = 32
TIMEOUT = 2  # seconds
ICMP_CODE = socket.getprotobyname('icmp')
UDP_CODE = socket.getprotobyname('udp')


def geo_to(host):
    """
    Return the geographic distance to an ip address in km.
    """

    conn = http.client.HTTPConnection('freegeoip.net')

    conn.request('GET', '/json/%s' % host)
    res = json.loads(conn.getresponse().read().decode('utf-8'))

    conn.request('GET', '/json/')
    me = json.loads(conn.getresponse().read().decode('utf-8'))

    conn.close()
    return haversine(float(res['latitude']), float(res['longitude']), float(me['latitude']), float(me['longitude']))


# haversine formula
# calculate the distance between 2 points on Earth
def haversine(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees).
    """

    # convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))

    # 6367 km is the radius of the Earth
    km = 6367 * c
    return int(km)


def computegeo(host):
    """
    Compute geographic distance to a given host and print out the
    results.
    """

    dest = socket.gethostbyname(host)
    geo = geo_to(dest)

    print('Distance to %s (%s km)\n' % (host, geo))


# run my trace and ping on each domain I was given in class
if __name__ == '__main__':
    iplist = []
    for i in open("targets.txt"):
        i = str(i.strip('\n'))
        iplist.append(i)

    for domain in iplist:
        computegeo(domain)
