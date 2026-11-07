---
topic: lab-setup
tags: [lab, vpn, ssh, metodologia]
---

# Canal de ataque: VM de Kali, VPN y comprobación previa

[🇬🇧 English](lab-setup.en.md) | **Español**

> Antes de enumerar un box conviene saber **desde dónde** se ataca y **si se llega**. Esta nota documenta la topología del laboratorio, el script de comprobación y los fallos que se repiten.

## Topología

```
Windows (host)                 VM Kali (VirtualBox)              HTB
192.168.56.1  ── host-only ── 192.168.56.x  ── tun0 (VPN) ──  10.129.x.x
```

- **Adaptador 1 – NAT**: salida a Internet para que la VM levante la VPN.
- **Adaptador 2 – host-only**: canal de administración desde el host (`192.168.56.1`).
- El tráfico al box sale **desde `tun0`**, no desde el host: por eso el escaneo se lanza dentro de la VM y no en Windows.

Ventaja: las herramientas (`nmap`, `ffuf`, `gobuster`, `smbclient`…) ya están en Kali, y la VPN vive allí, así que no hay que tocar la configuración de red del host.

## Requisitos en la VM

```bash
sudo systemctl start ssh          # o: enable --now ssh
ip -4 -o addr show | grep 192.168.56
ip a | grep tun0                  # la VPN debe estar arriba
```

La clave pública del host va en `~/.ssh/authorized_keys` (permisos `700` para `.ssh` y `600` para el fichero).

## Script de comprobación

`preflight.sh` (repositorio local, nunca aquí con claves) localiza la VM, comprueba el acceso, mira `tun0`, lista herramientas y verifica el alcance al target:

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

VM="$(find_vm)" || { echo "[!] VM no encontrada: ¿encendida? ¿host-only?"; exit 1; }
echo "[+] VM: $VM"

ssh -i "$KEY" -o StrictHostKeyChecking=accept-new -o ConnectTimeout=8 "$VM_USER@$VM" 'bash -s' <<'REMOTE'
echo "[*] tun0:"; ip -4 -o addr show tun0 2>/dev/null | awk '{print "    " $4}' || echo "    [!] sin tun0"
echo "[*] herramientas:"
for t in nmap ffuf gobuster feroxbuster smbclient redis-cli; do
  printf "    %-12s %s\n" "$t" "$(command -v "$t" 2>/dev/null || echo NO)"
done
REMOTE

[ -n "$TARGET" ] && ssh -i "$KEY" "$VM_USER@$VM" "TARGET=$TARGET bash -s" <<'REMOTE'
ping -c 2 -W 2 "$TARGET" >/dev/null 2>&1 && echo "    [+] ICMP ok" || echo "    [i] sin ICMP (normal en HTB)"
for p in 22 80 443; do timeout 2 bash -c "echo >/dev/tcp/$TARGET/$p" 2>/dev/null && echo "    [+] $p abierto"; done
REMOTE
```

Uso:

```bash
bash htb/preflight.sh                 # sólo canal y herramientas
bash htb/preflight.sh 10.129.x.x      # además alcance al target
```

## Fallos que se repiten

| Síntoma | Causa | Arreglo |
|---|---|---|
| `Connection timed out` al 22 | VM apagada o host-only desconectado | arrancar la VM / conectar el adaptador |
| `Permission denied (publickey)` | clave no autorizada o permisos | revisar `authorized_keys`, `chmod` |
| Hay SSH pero no se llega al box | `tun0` caída | conectar la VPN dentro de la VM |
| El box no responde a `ping` | ICMP filtrado en HTB | probar `/dev/tcp` a 22/80/443 |
| El host-only cambió de IP | DHCP de VirtualBox | el script barre el rango, no asumas la IP |

## Reglas

- La clave privada **nunca** entra en el repositorio de writeups (`.gitignore`).
- Las credenciales y flags del box van a `private/`, no a los documentos.
- Un `timed out` se diagnostica en capas: VM → sshd → clave → VPN → target.

## Referencias

- <https://www.virtualbox.org/manual/topics/networkingdetails.html>
- <https://www.hackthebox.com/network-access>
