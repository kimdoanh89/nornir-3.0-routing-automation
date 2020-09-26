"""
nw_advertised is defined in hosts.yaml as a dictionary of OSPF area keys,
and list of networks to be advertised in each OSPF area as values.
Each OSPF area will advertised some networks.
For example: R7
nw_advertised: {"0": ["192.1.67.0/24", "7.0.0.0/8"], "10": ["192.1.78.0/24"]}
R7 will advertise 2 networks in area 0: ["192.1.67.0/24", "7.0.0.0/8"];
and 1 network in area 10: ["192.1.78.0/24"]
"""
from nornir import InitNornir
import ipaddress


nr = InitNornir(config_file="config.yaml")
print("Hosts: ", nr.inventory.hosts)
print("Groups: ", nr.inventory.groups)
print("Hosts of Group area0: ", nr.inventory.children_of_group("area0"))
print("Hosts of Group area10: ", nr.inventory.children_of_group("area10"))

print("network Advertised of router R6: ",
      nr.inventory.hosts["R6"]["nw_advertised"])

for key, values in nr.inventory.hosts["R6"]["nw_advertised"].items():
    for v in values:
        print("Area", key, ":", v)
        nw = ipaddress.ip_network(v)
        # print(nw.network_address, nw.hostmask)
        print("network {} {} area {}".format(nw.network_address,
                                             nw.hostmask, key))

print("-"*95)

print("network Advertised of router R7: ",
      nr.inventory.hosts["R7"]["nw_advertised"])

for key, values in nr.inventory.hosts["R7"]["nw_advertised"].items():
    for v in values:
        print("Area", key, ":", v)
        nw = ipaddress.ip_network(v)
        # print(nw.network_address, nw.hostmask)
        print("network {} {} area {}".format(nw.network_address,
                                             nw.hostmask, key))
