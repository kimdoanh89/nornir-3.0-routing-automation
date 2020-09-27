from nornir import InitNornir
from nornir.core.filter import F
from nornir_utils.plugins.functions import print_result
from nornir_netmiko import netmiko_send_config
import ipaddress


def interfaces_config(task):
    interfaces_cms = []
    interfaces = task.host['interfaces']
    for name, interface in interfaces.items():
        cm = f"interface {name}"
        interfaces_cms.append(cm)
        if "lo" not in name.lower():
            interfaces_cms.append("no shut")
        interface = ipaddress.IPv4Interface(interface)
        cm = f"ip address {interface.ip} {interface.network.netmask}"
        interfaces_cms.append(cm)
    task.run(netmiko_send_config, config_commands=interfaces_cms)


def eigrp_config(task):
    eigrp_cms = []
    eigrp_advertised = task.host['eigrp_advertised']
    for key, values in eigrp_advertised.items():
        cm = f"router eigrp {key}"
        eigrp_cms.append(cm)
        for v in values:
            nw = ipaddress.ip_network(v)
            cm = f"network {nw.network_address} {nw.hostmask}"
            eigrp_cms.append(cm)
    task.run(netmiko_send_config, config_commands=eigrp_cms)


def ospf_config(task):
    ospf_cms = []
    interfaces = task.host['interfaces']
    ospf_advertised = task.host['ospf_advertised']
    router_id = task.host['ospf_router_id']
    for name, _ in interfaces.items():
        if "lo" in name:
            ospf_cms.append(f"interface {name}")
            ospf_cms.append("ip ospf network point-to-point")

    ospf_cms.append("router ospf 1")
    ospf_cms.append(f"router-id 0.0.0.{router_id}")
    for key, values in ospf_advertised.items():
        for v in values:
            nw = ipaddress.ip_network(v)
            cm = f"network {nw.network_address} {nw.hostmask} area {key}"
            ospf_cms.append(cm)
    task.run(netmiko_send_config, config_commands=ospf_cms)


def rip_config(task):
    rip_cms = []
    rip_cms.append("router rip")
    rip_cms.append("version 2")
    rip_cms.append("no auto")
    rip_advertised = task.host['rip_advertised']
    for nw in rip_advertised:
        rip_cms.append(f"network {nw}")
    task.run(netmiko_send_config, config_commands=rip_cms)


def redistribute_at_R1_config(task):
    redis_cms = ["router eigrp 100",
                 "redistribute ospf 1 metric 10 10 1 1 1",
                 "router ospf 1",
                 "redistribute eigrp 100 subnets"]
    task.run(netmiko_send_config, config_commands=redis_cms)


def redistribute_at_R6_config(task):
    redis_cms = ["router rip",
                 "redistribute ospf 1 metric 1",
                 "router ospf 1",
                 "redistribute rip"]
    task.run(netmiko_send_config, config_commands=redis_cms)


def route_summarization_at_R1(task):
    summarize_cms = ["router ospf 1",
                     "summary-address 207.1.4.0 255.255.252.0",
                     "summary-address 208.1.4.0 255.255.252.0"]
    task.run(netmiko_send_config, config_commands=summarize_cms)


def route_summarization_at_R6(task):
    summarize_cms = ["router ospf 1",
                     "summary-address 109.1.4.0 255.255.252.0"]
    task.run(netmiko_send_config, config_commands=summarize_cms)


def stub_area_config(task, area: int):
    stub_cms = ["router ospf 1", f"area {area} stub"]
    task.run(netmiko_send_config, config_commands=stub_cms)


def not_so_stubby_area_config(task, area: int):
    stub_cms = ["router ospf 1", f"area {area} nssa"]
    task.run(netmiko_send_config, config_commands=stub_cms)


def main():
    nr = InitNornir(config_file="config-topo2.yaml")
    result = nr.run(task=interfaces_config)
    print_result(result)

    nr2 = nr.filter(F(groups__contains="eigrp"))
    result = nr2.run(task=eigrp_config)
    print_result(result)

    nr3 = nr.filter(F(groups__contains="ospf"))
    result = nr3.run(task=ospf_config)
    print_result(result)

    nr4 = nr.filter(F(groups__contains="rip"))
    result = nr4.run(task=rip_config)
    print_result(result)
    # Redistribute routes at R1
    nr5 = nr.filter(name="R1")
    result = nr5.run(task=redistribute_at_R1_config)
    print_result(result)
    # Redistribute routes at R6
    nr6 = nr.filter(name="R6")
    result = nr6.run(task=redistribute_at_R6_config)
    print_result(result)
    # Summarize routes at R1
    nr7 = nr.filter(name="R1")
    result = nr7.run(task=route_summarization_at_R1)
    print_result(result)
    # Summarize routes at R6
    nr8 = nr.filter(name="R6")
    result = nr8.run(task=route_summarization_at_R6)
    print_result(result)
    # Configure Area 10 as stub-area
    nr9 = nr.filter(F(groups__contains="area10"))
    result = nr9.run(task=stub_area_config, area=10)
    print_result(result)
    # Configure Area 20 as not-so-stubby-area
    nr10 = nr.filter(F(groups__contains="area20"))
    result = nr10.run(task=not_so_stubby_area_config, area=20)
    print_result(result)


if __name__ == "__main__":
    main()
