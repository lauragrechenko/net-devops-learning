#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+
# (c) 2025 Laura Grechenko
# This file is part of an Ansible collection and is licensed under
# the terms of the GNU General Public License v3 or later (GPLv3+).

from __future__ import annotations

DOCUMENTATION = r'''
---
module: yc_instance
short_description: Minimal YC VM create via yc CLI
version_added: "1.0.0"
description:
  - Minimal wrapper around the Yandex Cloud CLI to ensure a VM with the given name exists.
  - Supports sizing options (CPU, RAM, disk), guaranteed vCPU performance (core fraction),
    preemptible VM flag, NAT/public IP and SSH key injection.
requirements:
  - yc CLI configured on control host
options:
  state:
    description: Desired state of the instance.
    type: str
    choices: [present]
    default: present
  name:
    description: Instance name.
    type: str
    required: true
  folder_id:
    description: Folder ID that contains the instance.
    type: str
    required: true
  zone:
    description: Availability zone (e.g. ru-central1-a).
    type: str
    required: true
  subnet_id:
    description: Subnet ID for the primary network interface.
    type: str
    required: true
  image_id:
    description: Image ID to use for the boot disk.
    type: str
    required: true

  platform_id:
    description: YC platform (CPU generation). C(standard-v2) = Intel Cascade Lake.
    type: str
    choices: [standard-v1, standard-v2, standard-v3]
    default: standard-v2
  cores:
    description: Number of vCPUs.
    type: int
    default: 2
  memory_gb:
    description: RAM size in GB.
    type: int
    default: 2
  disk_gb:
    description: Boot disk size in GB.
    type: int
    default: 10
  disk_type:
    description: Boot disk type.
    type: str
    choices: [network-hdd, network-ssd, network-ssd-nonreplicated]
    default: network-hdd
  core_fraction:
    description: Guaranteed vCPU performance (percent, YC allowed values are typically 5, 20, 50, 100).
    type: int
    default: 5
  preemptible:
    description: Create preemptible instance.
    type: bool
    default: true
  nat:
    description: Attach public IPv4 via NAT on the primary interface.
    type: bool
    default: true
  ssh_key:
    description:
      - SSH public key to inject on create (path to pubkey file or literal C(user:ssh-rsa ...)).
    type: str
    required: false
author:
  - Laura Grechenko (@lauragrechenko)
'''

EXAMPLES = r'''
- name: Ensure instance present with sizing
  netology_devops.learning.yc_instance:
    state: present
    name: demo
    folder_id: "{{ yc_folder_id }}"
    zone: ru-central1-a
    subnet_id: "{{ yc_subnet_id }}"
    image_id: "{{ yc_image_id }}"
    platform_id: standard-v2
    cores: 2
    memory_gb: 4
    disk_gb: 20
    disk_type: network-hdd
    core_fraction: 100
    preemptible: false
    nat: true
    ssh_key: "{{ lookup('file', '~/.ssh/id_rsa.pub') }}"
'''

RETURN = r'''
changed:
  description: Whether the task resulted in a change (instance created or removed).
  type: bool
  returned: always
instance_id:
  description: The ID of the instance, when known.
  type: str
  returned: when state is present
name:
  description: The name of the instance.
  type: str
  returned: when state is present
status:
  description: The status of the instance as reported by YC (e.g. RUNNING).
  type: str
  returned: when state is present
public_ip:
  description: Public IPv4 address (if NAT was enabled and IP assigned).
  type: str
  returned: when available
'''

import json
import shlex
import shutil
import subprocess
import time
from ansible.module_utils.basic import AnsibleModule


def _run(cmd: list[str]) -> str:
    """Run a command, raise on non-zero; return stdout."""
    try:
        p = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True,
        )
        return p.stdout
    except subprocess.CalledProcessError as e:
        msg = e.stderr.strip() or e.stdout.strip() or f"Command failed: {' '.join(shlex.quote(c) for c in cmd)}"
        raise RuntimeError(msg) from e


def _list_instances(folder_id: str) -> list[dict]:
    out = _run(["yc", "compute", "instance", "list", "--folder-id", folder_id, "--format", "json"])
    try:
        return json.loads(out or "[]")
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Failed to parse yc list output: {e}") from e


def _get_instance_by_name(name: str, folder_id: str) -> dict | None:
    for inst in _list_instances(folder_id):
        if inst.get("name") == name:
            return inst
    return None


def _extract_public_ip(inst: dict) -> str | None:
    try:
        nics = inst.get("network_interfaces") or []
        if not nics:
            return None
        addr = nics[0].get("primary_v4_address") or {}
        nat = addr.get("one_to_one_nat") or {}
        return nat.get("address")
    except Exception:
        return None


def _poll_status(name: str, folder_id: str, timeout_s: int = 90) -> dict | None:
    start = time.time()
    while time.time() - start < timeout_s:
        inst = _get_instance_by_name(name, folder_id)
        if inst and inst.get("status"):
            return inst
        time.sleep(2)
    return _get_instance_by_name(name, folder_id)


def main():
    module = AnsibleModule(
        argument_spec=dict(
            state=dict(type="str", choices=["present"], default="present"),
            name=dict(type="str", required=True),
            folder_id=dict(type="str", required=True),
            zone=dict(type="str", required=True),
            subnet_id=dict(type="str", required=True),
            image_id=dict(type="str", required=True),

            platform_id=dict(type="str",
                             choices=["standard-v1", "standard-v2", "standard-v3"],
                             default="standard-v2"),
            cores=dict(type="int", default=2),
            memory_gb=dict(type="int", default=2),
            disk_gb=dict(type="int", default=10),
            disk_type=dict(type="str",
                           choices=["network-hdd", "network-ssd", "network-ssd-nonreplicated"],
                           default="network-hdd"),
            core_fraction=dict(type="int", default=5),
            preemptible=dict(type="bool", default=True),
            nat=dict(type="bool", default=True),
            ssh_key=dict(type="str", required=False, no_log=True),
        ),
        supports_check_mode=True,
    )

    p = module.params

    if not shutil.which("yc"):
        module.fail_json(msg="yc CLI not found in PATH. Install it and run `yc init` (or set SA env) first.")

    if p["cores"] < 1:
        module.fail_json(msg="cores must be >= 1")
    if p["memory_gb"] < 1:
        module.fail_json(msg="memory_gb must be >= 1")
    if p["disk_gb"] < 1:
        module.fail_json(msg="disk_gb must be >= 1")
    if p["core_fraction"] not in (5, 20, 50, 100):
        module.fail_json(msg="core_fraction must be one of 5, 20, 50, 100")

    try:
        inst = _get_instance_by_name(p["name"], p["folder_id"])

        if inst is not None:
            module.exit_json(
                changed=False,
                instance_id=inst.get("id"),
                name=inst.get("name"),
                status=inst.get("status"),
                public_ip=_extract_public_ip(inst),
            )

        if module.check_mode:
            module.exit_json(changed=True)

        boot_disk = f"size={p['disk_gb']}GB,type={p['disk_type']},image-id={p['image_id']}"
        create_cmd = [
            "yc", "compute", "instance", "create",
            "--name", p["name"],
            "--folder-id", p["folder_id"],
            "--zone", p["zone"],
            "--create-boot-disk", boot_disk,
            "--cores", str(p["cores"]),
            "--memory", str(p["memory_gb"]),
            "--core-fraction", str(p["core_fraction"]),
            "--platform-id", p["platform_id"],
            "--format", "json",
        ]

        create_cmd.append("--preemptible" if p["preemptible"] else "--non-preemptible")

        # network + NAT/public IP
        nic = f"subnet-id={p['subnet_id']}"
        if p["nat"]:
            nic += ",nat-ip-version=ipv4"
        create_cmd += ["--network-interface", nic]

        # ssh key
        if p.get("ssh_key"):
            create_cmd += ["--ssh-key", p["ssh_key"]]

        out = _run(create_cmd)
        try:
            created = json.loads(out or "{}")
        except json.JSONDecodeError:
            created = {}

        # brief poll so we can return status/ip
        inst = _poll_status(p["name"], p["folder_id"], timeout_s=90)

        # module.exit_json(
        #     changed=True,
        #     instance_id=created.get("id"),
        #     name=p["name"],
        #     status=created.get("status"),
        # )

        module.exit_json(
            changed=True,
            instance_id=inst.get("id") if inst else None,
            name=p["name"],
            status=inst.get("status") if inst else None,
            public_ip=_extract_public_ip(inst) if inst else None,
        )

    except RuntimeError as e:
        module.fail_json(msg=str(e))
    except Exception as e:
        module.fail_json(msg=f"Unexpected error: {e!r}")


if __name__ == "__main__":
    main()
