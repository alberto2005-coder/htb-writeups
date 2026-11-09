---
sherlock: Noxious
domain: DFIR / Active Directory
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [dfir, pcap, llmnr, ntlmv2, responder, hashcat, active-directory]
---


# Noxious — Hack The Box

[⚑ English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de método; sin respuestas literales de la plataforma.

## Escenario

El IDS avisa de un posible dispositivo no autorizado en la VLAN de Active Directory y de tráfico **LLMNR** poco habitual. Se sospecha un envenenamiento LLMNR: hay que localizar al atacante, la víctima y demostrar si las credenciales se llegaron a crackear.

## Evidencias

- Captura de red parcial de la VLAN.
- Contexto de la máquina víctima (`Forela-WKstn002`).

## Investigación

### 1. Quién pregunta y quién responde

En Wireshark:

```text
llmnr
nbns
```

LLMNR y NBT-NS son mecanismos de resolución **local**: cuando el equipo no resuelve un nombre por DNS, lo pregunta a toda la red. Un atacante con Responder contesta «ese soy yo» y la víctima le manda su autenticación.

La firma de un envenenamiento es una **respuesta** LLMNR/NBT-NS desde una IP que no es la del servidor legítimo, seguida de tráfico SMB hacia esa IP.

### 2. La víctima y el atacante

```bash
tshark -r capture.pcap -Y 'llmnr' -T fields -e frame.number -e ip.src -e ip.dst -e llmnr.name
```

Se identifica la IP de la víctima (la que pregunta) y la IP del que responde siempre con el mismo nombre falso, que además resuelve un nombre de host ofensivo en NBNS. Esa IP es el dispositivo rogue.

### 3. Captura de NTLMv2

```bash
tshark -r capture.pcap -Y 'ntlmssp' -T fields -e ip.src -e ip.dst -e ntlmssp.auth.username -e ntlmssp.ntlmserverchallenge
```

En el intercambio SMB aparece `NTLMSSP_AUTH` con el usuario víctima y el `ServerChallenge`. Con esos campos se reconstruye el hash en formato `usuario::dominio:challenge:proof:blob` y se comprueba si la contraseña cae:

```bash
hashcat -m 5600 hash.txt /usr/share/wordlists/rockyou.txt
```

Si crackea, el impacto es real: la contraseña de un usuario del dominio queda en manos del atacante.

### 4. Cierre

Se documentan: IP del rogue, nombre falso usado, víctima, usuario cuyo hash se capturó, si se crackeó y en qué momento. La respuesta al IDS incluye bloquear LLMNR/NBT-NS por GPO y exigir firma SMB.

## Conclusiones

- LLMNR/NBT-NS activos permiten a cualquier equipo de la VLAN suplantar la resolución de nombres.
- El envenenamiento deriva en captura de NTLMv2 y, con contraseñas débiles, en credenciales válidas.
- Un dispositivo no inventariado que responde a LLMNR es la señal más clara del ataque.

## Lecciones

- Deshabilitar LLMNR y NBT-NS por GPO es la mitigación principal; el resto son parches.
- `hashcat -m 5600` sobre NTLMv2 es rápido: la fortaleza de la contraseña es la única defensa real.
- En el PCAP, mirar siempre quién **responde** a las consultas, no solo quién pregunta.
