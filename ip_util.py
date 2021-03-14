import re


def validate_ip(ip_address: str):
    """
    Validates a given string to be compliant to IPv4 address format.
    """
    ipv4_address_regex = r'^((25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9][0-9]|[0-9])\.){3}(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9][0-9]|[0-9])$'
    return re.match(ipv4_address_regex, ip_address)


def compute_ip_to_numeric(input: str):
    """
    Converts an IPv4 address string into a numeric value.
    """
    tokens = [int(i) for i in input.split('.')]
    return sum([tokens[i]*(256**(len(tokens)-1-i)) for i in range(len(tokens))])


def compute_numeric_to_ip(input: int):
    """
    Converts a numeric value into an IPv4 address string.
    """
    octet1 = input // (256**3)
    octet2 = (input % (256**3)) // (256**2)
    octet3 = ((input % (256**3)) % (256**2)) // 256
    octet4 = ((input % (256**3)) % (256**2)) % 256
    return '.'.join([str(octet1), str(octet2), str(octet3), str(octet4)])