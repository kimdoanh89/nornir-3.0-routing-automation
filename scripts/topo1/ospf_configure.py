from nornir import InitNornir
from nornir_utils.plugins.functions import print_result
from nornir_netmiko import netmiko_send_config
from nornir.core.task import Task, Result
import ipaddress


def hello_world(task: Task) -> Result:
    return Result(
        host=task.host,
        result=f"{task.host.name} says hello world!"
    )


def no_ospf_config(task):
    pass


def ospf_config(task):
    ospf_cms = ['router ospf 1']
    nw_advertised = task.host['nw_advertised']
    id = task.host['id']
    ospf_cm = f"router-id 0.0.0.{id}"
    ospf_cms.append(ospf_cm)
    for key, values in nw_advertised.items():
        for v in values:
            nw = ipaddress.ip_network(v)
            ospf_cm = f"network {nw.network_address} {nw.hostmask} area {key}"
            ospf_cms.append(ospf_cm)
    task.run(netmiko_send_config, config_commands=ospf_cms)


def main():
    nr = InitNornir(config_file="config.yaml")
    # nr = nr.filter(name="R1")
    result = nr.run(task=ospf_config)
    print_result(result)


if __name__ == "__main__":
    main()
