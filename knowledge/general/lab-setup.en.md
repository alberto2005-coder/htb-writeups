---
topic: lab-setup
tags: [lab, vpn, ssh, methodology]
---

# Attack channel: Kali VM, VPN and preflight check

**English** | [🇪🇸 Español](lab-setup.md)

> Before enumerating a box you should know **where you attack from** and **whether you can reach it**. This note documents the lab topology, the check script and the recurring failures.

## Topology

```
Windows (host)                 Kali VM (VirtualBox)              HTB
192.168.56.1  ── host-only ── 192.168.56.x  ── tun0 (VPN) ──  10.129.x.x
```

- **Adapter 1 – NAT**: Internet access so the VM can bring up the VPN.
- **Adapter 2 – host-only**: management channel from the host (`192.168.56.1`).
- Box traffic leaves **through `tun0`**, not the host: that is why scanning happens inside the VM.

Tools (`nmap`, `ffuf`, `gobuster`, `smbclient`…) are already in Kali and the VPN lives there, so the host network setup stays untouched.

## VM requirements

```bash
sudo systemctl start ssh          # or: enable --now ssh
ip -4 -o addr show | grep 192.168.56
ip a | grep tun0                  # VPN must be up
```

The host's public key goes into `~/.ssh/authorized_keys` (`700` for `.ssh`, `600` for the file).

## Preflight script

`preflight.sh` (kept outside this repo, never with keys) finds the VM, checks access, inspects `tun0`, lists tooling and verifies target reachability:

```bash
#!/usr/bin/env bash
set -u
KEY="${KEY:-htb/id_ed25519}"
VM_USER="${VM_USER:-kali}"
SUBNET="${SUBNET:-192.168.56}"
TARGET="${1:-}"

find_vm() {
  for ip in $(seq 100 130); do
    timeout 1 bash -c "echo >/dev/tcp/$SUBNET.$ip/22" 2>/dev/null && { echo "$SUBNET.$ip"; return 0; }
  done
  return 1
}

VM="$(find_vm)" || { echo "[!] VM not found: powered on? host-only?"; exit 1; }
echo "[+] VM: $VM"

ssh -i "$KEY" -o StrictHostKeyChecking=accept-new -o ConnectTimeout=8 "$VM_USER@$VM" 'bash -s' <<'REMOTE'
echo "[*] tun0:"; ip -4 -o addr show tun0 2>/dev/null | awk '{print "    " $4}' || echo "    [!] no tun0"
echo "[*] tools:"
for t in nmap ffuf gobuster feroxbuster smbclient redis-cli; do
  printf "    %-12s %s\n" "$t" "$(command -v "$t" 2>/dev/null || echo NO)"
done
REMOTE

[ -n "$TARGET" ] && ssh -i "$KEY" "$VM_USER@$VM" "TARGET=$TARGET bash -s" <<'REMOTE'
ping -c 2 -W 2 "$TARGET" >/dev/null 2>&1 && echo "    [+] ICMP ok" || echo "    [i] no ICMP (normal on HTB)"
for p in 22 80 443; do timeout 2 bash -c "echo >/dev/tcp/$TARGET/$p" 2>/dev/null && echo "    [+] $p open"; done
REMOTE
```

Usage:

```bash
bash htb/preflight.sh                 # channel and tooling only
bash htb/preflight.sh 10.129.x.x      # also target reachability
```

## Recurring failures

| Symptom | Cause | Fix |
|---|---|---|
| `Connection timed out` on 22 | VM off or host-only detached | boot the VM / attach the adapter |
| `Permission denied (publickey)` | key not authorised or bad perms | check `authorized_keys`, `chmod` |
| SSH works but no box reachability | `tun0` down | connect the VPN inside the VM |
| Box ignores `ping` | ICMP filtered on HTB | test 22/80/443 with `/dev/tcp` |
| Host-only IP changed | VirtualBox DHCP | the script sweeps the range; do not assume the IP |

## Rules

- The private key **never** enters the writeups repository (`.gitignore`).
- Box credentials and flags go to `private/`, not into documents.
- Diagnose a `timed out` in layers: VM → sshd → key → VPN → target.

## References

- <https://www.virtualbox.org/manual/topics/networkingdetails.html>
- <https://www.hackthebox.com/network-access>
