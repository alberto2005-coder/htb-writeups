---
machine: Chainsaw
os: Linux
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [linux, web, solidity, blockchain, ipfs, suid, slack-space]
---

# Chainsaw — Hack The Box (Linux)

[🇪🇸 Español](README.md) | **English**

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

Anonymous FTP publishes a Solidity contract and its ABI; port `9810` is an Ethereum node. Interact with the contract and its `setDomain` function runs commands, yielding a shell. IPFS contains an SSH key for `bobby`, protected by a passphrase that can be cracked. A SUID binary yields root, but the flag is hidden in the slack space of `root.txt` and is recovered with `bmap` or `debugfs`.

## Recon

```bash
nmap -Pn -sCV -p21,22,9810 <IP>
```

- `21/tcp` vsftpd with anonymous login and `22/tcp` OpenSSH.
- `9810/tcp` responds as an Ethereum JSON-RPC node.
- FTP contains `WeaponizedPing.json`, `WeaponizedPing.sol` and `address.txt`.

## Enumeration

- The contract exposes `setDomain(string)` and connects to the node with `web3.py`.
- The function passes the domain into a system command without sanitization.
- IPFS files include an SSH private key for `bobby` and a note with the passphrase.

## Foothold

Deploy or reuse the contract and call `setDomain` with a payload that starts a reverse shell. The shell lands as the user running the node.

```python
from web3 import Web3
w3 = Web3(Web3.HTTPProvider('http://<IP>:9810'))
# load ABI and address, send setDomain('; bash -c "..."')
```

Then download the IPFS key, crack its passphrase with `john` and log in as `bobby`.

## Lateral movement

There is no other host. The pivot is from the contract to the system, then to `bobby` with the SSH key and then to the privileged binary.

## Privilege escalation

`bobby` can run a SUID binary that interacts with the disk image. Use it to mount or read the system as root. The flag is not in the normal contents of `root.txt`, but in its slack space.

```bash
find / -perm -4000 -type f 2>/dev/null
bmap --mode checkslack /root/root.txt
bmap --mode slack /root/root.txt
# or with debugfs on /dev/sda2
```

## Evidence

- Contract and ABI downloaded over anonymous FTP.
- `setDomain` command execution and initial shell.
- `bobby` key and flag read from slack space.

## Lessons learned

- Smart contracts can be an interface to system commands.
- Anonymous IPFS and FTP can leak keys and sensitive material.
- Evidence may live in slack space and require forensic tools.

## Mitigation and detection

- Do not run contracts with access to the host shell.
- Restrict FTP/IPFS and rotate exposed keys.
- Audit SUID binaries and block-device access.

## References

- [0xdf — Chainsaw](https://0xdf.gitlab.io/2019/11/23/htb-chainsaw.html)
- [IppSec — Chainsaw](https://www.youtube.com/watch?v=vESegBSrm_U)
- [Hack The Box — Chainsaw](https://app.hackthebox.com/machines/chainsaw)
