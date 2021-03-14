import re


def validate_ip(ip_address: str):
    ipv4_address_regex = r'^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
    return re.match(ipv4_address_regex, ip_address)


def compute_ip_to_numeric(input: str):
    tokens = [int(i) for i in input.split('.')]
    return sum([tokens[i]*(256**(len(tokens)-1-i)) for i in range(len(tokens))])


def compute_numeric_to_ip(input: int):
    t1 = input // (256**3)
    t2 = (input % (256**3)) // (256**2)
    t3 = ((input % (256**3)) % (256**2)) // 256
    t4 = ((input % (256**3)) % (256**2)) % 256
    return '.'.join([str(t1), str(t2), str(t3), str(t4)])