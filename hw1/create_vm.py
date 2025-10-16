import re
import subprocess
from pathlib import Path
from os import system
from time import sleep

print("Hello!\nThis is a VM creation machine. Answer these questions, and you will get cool new VM:")

vm_name = input("Give VM a name: ")
vm_cpus = int(input("Give VM a CPUs: "))
vm_ram = int(input("Give VM a RAM: "))
vm_network = input("Give VM a network: ")
vm_password = input("Give VM a password: ")
vm_img = input("Give VM an image: ")
vm_img_variant = input("Give VM an image variant: ")
vm_ssh_path = Path(input("Give VM an authorized keys SSH path: "))
vm_html_page = Path(input("Give VM an NGINX hello HTML page path: "))

with open("meta-data", "w") as f:
    f.write(
f"""instance-id: clouds-hw1-ubuntu24.04
local-hostname: {vm_name}

"""
    )

with open(vm_html_page, "r") as f:
    html_page = " ".join(f.read().split())
    # print(f"HTML page: {html_page}")

with open(vm_ssh_path, "r") as f:
    ssh_keys = f.readlines()

    if ssh_keys:
        ssh_keys = [""] + ssh_keys
    ssh_keys = "\n  - ".join(ssh_keys)

with open("user-data", "w") as f:
    f.write(
f"""#cloud-config
password: {vm_password}
chpasswd:
  expire: false
ssh_authorized_keys:{ssh_keys}

runcmd:
  - apt update
  - apt install nginx -y
  - echo "{html_page}" > /var/www/html/index.html

"""
    )

if system("genisoimage -output tmp.iso -volid cidata -rational-rock -joliet user-data meta-data"):
    print("genisoimage failed!")
    raise SystemExit(1)
if system(f"virt-install --name cool-vm --ram {vm_ram} --vcpus {vm_cpus} --disk path={vm_img},format=qcow2 --disk path=tmp.iso,device=cdrom --os-variant {vm_img_variant} --virt-type kvm --network network={vm_network},model=virtio --import --noautoconsole"):
    print("virt-install failed!")
    raise SystemExit(1)

for i in range(10):
    sleep(5)
    result = subprocess.run(["virsh", "domifaddr", "cool-vm"], stdout=subprocess.PIPE)
    sleep(5)
    if result.returncode != 0:
        print("virsh failed!")
        raise SystemExit(1)
    result_addr = re.findall(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", result.stdout.decode())
    if result_addr:
        break
    print("VM is not configured yet. Sleeping...")
else:
    print("VM was not configured")
    raise SystemExit(1)
print(result.stdout.decode())
print(f"You may access your web-page at {result_addr[0]}")
print("Do not forget to clean everything!")
