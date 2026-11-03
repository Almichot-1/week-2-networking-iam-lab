"""Inspect the Linux lab network and verify the subnet and IAM exercises."""
import fcntl
import ipaddress
import json
from pathlib import Path
import socket
import struct

print(next(x for x in Path("/etc/os-release").read_text().splitlines() if x.startswith("PRETTY_NAME=")))
for line in Path("/proc/net/dev").read_text().splitlines()[2:]:
    iface = line.split(":")[0].strip()
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        req = struct.pack("256s", iface.encode())
        addr = socket.inet_ntoa(fcntl.ioctl(s, 0x8915, req)[20:24])
        mask = socket.inet_ntoa(fcntl.ioctl(s, 0x891b, req)[20:24])
        print(iface, ipaddress.IPv4Interface(f"{addr}/{mask}"))
routes = [row.split() for row in Path("/proc/net/route").read_text().splitlines()[1:]]
gateways = [socket.inet_ntoa(struct.pack("<I", int(row[2], 16))) for row in routes if row[1] == "00000000"]
print("Default IPv4 gateway:", ", ".join(gateways) or "none visible")
parent = ipaddress.ip_network("10.0.0.0/24")
subnets = list(parent.subnets(new_prefix=26))
assert len(subnets) == 4 and sum(n.num_addresses for n in subnets) == parent.num_addresses
for net in subnets:
    print(net, "hosts", net[1], "to", net[-2], "broadcast", net[-1], "AWS assignable", net.num_addresses - 5)
policy = json.loads(Path(__file__).with_name("s3-read-policy.json").read_text())
assert policy["Version"] == "2012-10-17"
stmt, = policy["Statement"]
assert (stmt["Effect"], stmt["Action"], stmt["Resource"]) == ("Allow", "s3:GetObject", "arn:aws:s3:::example-bucket/*")
print("PASS: four /26s cover the /24; IAM document grants only the intended object read.")
