#!/usr/bin/env python3

import json
import sys
import subprocess

def scan_vms():
    try:
        vm_raw_list = subprocess.check_output('vmrun list', shell=True, text=True).splitlines()[1:]
    except subprocess.CalledProcessError:
        return []

    vm_operative_list = []
    
    for vm in vm_raw_list:
        vm_cleaned_list = {}
        vm_cleaned_list["hostname"] = vm.split("/")[-1].split(".vmx")[0]

        try:
            ip_address = subprocess.check_output(f'vmrun getGuestIPAddress \"{vm}\"', shell=True, text=True).strip()
            if ip_address:
                vm_cleaned_list["ip"] = ip_address
                vm_operative_list.append(vm_cleaned_list)
        except subprocess.CalledProcessError:
            continue

    return vm_operative_list

def generate_inventory():
    inventory = {"_meta": {"hostvars": {}}, "all": {"hosts": []}}
    
    live_hosts = scan_vms()
    if not live_hosts:
        return inventory

    for host in live_hosts:
        hostname = host["hostname"]
        inventory["_meta"]["hostvars"][hostname] = {
            "ansible_host": host["ip"]
        }
        inventory["all"]["hosts"].append(hostname)

    return inventory

if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == "--list":
        print(json.dumps(generate_inventory(), indent=4))
    elif len(sys.argv) == 2 and sys.argv[1] == "--host":
        print(json.dumps({}, indent=4))
    else:
        print(json.dumps({}))
