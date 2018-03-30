import socket
import struct
import time

MAX_HOPS = 32
TIMEOUT = 2  # seconds
msg = 'measurement for class project. questions to student txl429@case.edu or professor mxr136@case.edu'
payload = bytes(msg + 'X'*(1472-len(msg)), 'ascii')
ICMP_CODE = socket.getprotobyname('icmp')
UDP_CODE = socket.getprotobyname('udp')


def ping(host, ttl=30, port=33434):
    """
    Send a UDP probe to a given ip address and return
    the ICMP response and round trip duration.
    """

    # sockets for sending udp and receiving icmp
    recv_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, ICMP_CODE)
    send_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, UDP_CODE)

    recv_socket.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
    send_socket.setsockopt(socket.SOL_IP, socket.IP_TTL, ttl)

    recv_socket.bind(('', port))
    recv_socket.settimeout(TIMEOUT)

    # for use in calculating RTT
    start = time.time()
    end = time.time() + TIMEOUT

    # send udp probe
    send_socket.sendto(payload, (host, port))
    curr_addr = None
    curr_name = None

    # attempt to read icmp response
    rcvpkt, curr_addr = recv_socket.recvfrom(512)
    end = time.time()
    curr_addr = curr_addr[0]
    try:
        curr_name = socket.gethostbyaddr(curr_addr)[0]
    except socket.error:
        curr_name = curr_addr
    finally:
        # IP Header will be the first 20 Bytes
        ip_header = rcvpkt[0:20]
        # Calculate the Packet Length
        pktlength = struct.unpack("!H", ip_header[2:4])[0]
        # remove the IP Header from packet length
        pktlength = pktlength - 20
        # ICMP Header will be the 8 Bytes after IP Header
        icmp_header = rcvpkt[20:28]
        # remove the IP Header from packet length
        pktlength = pktlength - 8
        # calculate the ICMP payload length
        icmp_payloadlength = rcvpkt[28:28 + pktlength]

        send_socket.close()
        recv_socket.close()

    return curr_addr, round((end - start) * 1000), icmp_payloadlength


def count_hops_to(host):
    """
    Use binary search to find the number of hops to
    a given ip address.
    """

    low = 0
    high = MAX_HOPS
    ttl = 0

    while low < high:
        if ttl == int((high + low) / 2):
            break  # don't run the same ttl twice
        else:
            ttl = int((high + low) / 2)

        current, _, _ = ping(host, ttl)  # try reaching host with ttl number of hops

        if current is None:  # ttl too high
            high = ttl
        elif current.find(host) != -1:  # ttl just right
            return ttl
        else:  # ttl too low
            low = ttl

    return low


def rtt_to(host, ttl):
    """
    Return the round trip duration to an ip address.
    """

    _, rtt, payload_length = ping(host, ttl)
    return int(rtt), int(payload_length)


def compute(host):
    """
    Compute the number of hops, round trip duration and print out the
    results.
    """

    dest = socket.gethostbyname(host)
    count = count_hops_to(dest)
    rtt, payload_length = rtt_to(dest, count)

    print('Host: %s  Hops: %s  RTT: %s  OriginalDatagram: %sbytes' % (host, count, rtt, payload_length))


# run my trace and ping on each domain I was given in class
if __name__ == '__main__':
    iplist = []
    for i in open("targets.txt"):
        i = str(i.strip('\n'))
        iplist.append(i)

    for domain in iplist:
        compute(domain)
