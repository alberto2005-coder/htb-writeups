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

El IDS avisa de un dispositivo no autorizado en la VLAN de Active Directory y de tráfico **LLMNR** poco habitual. La víctima conocida es `Forela-WKstn002` (`172.17.79.136`). Hay que localizar al atacante, el nombre falso que usó, el hash capturado y si llegó a crackearse.

## Evidencias

- `capture.pcap` (parcial, sin el inicio de la sesión).
- Contexto: workstation víctima y dominio `forela.local`.

## Investigación

### 1. Quién responde

```bash
tshark -r capture.pcap -Y 'llmnr' -T fields -e frame.number -e ip.src -e ip.dst -e llmnr.qry.name
```

El patrón es siempre el mismo: la víctima pregunta por un nombre que no resuelve y **`172.17.79.135` contesta**, un equipo que no es el DC. En `nbns` aparece además el nombre de host del atacante, **`kali`**: un dispositivo no inventariado. El usuario tecleó `DCC01` en lugar de `DC01` y la consulta acabó en LLMNR.

### 2. Captura de NTLMv2

```bash
tshark -r capture.pcap -Y 'ntlmssp' -T fields -e frame.number -e ip.src -e ip.dst \
  -e ntlmssp.auth.username -e ntlmssp.ntlmserverchallenge
```

En SMB2 aparece `NTLMSSP_AUTH` del usuario **`john.deacon`** contra la IP del rogue, con reto de servidor **`601019d191f054f1`** y `NTProofStr` `c0cc803a6d9fb5a9082253a04dbd4cd4`. Con esos campos se arma el hash:

```text
john.deacon::FORELA:601019d191f054f1:c0cc803a6d9fb5a9082253a04dbd4cd4:<blob>
```

### 3. Crackeo

```bash
hashcat -m 5600 hash.txt /usr/share/wordlists/rockyou.txt
```

El modo es **5600 (NetNTLMv2)**. La contraseña cae con diccionario, así que la captura tuvo impacto real: credenciales válidas del dominio.

### 4. Cierre

Se documentan IP del rogue (`172.17.79.135`), hostname (`kali`), víctima, usuario, reto, hash y si crackeó. La respuesta al IDS: deshabilitar LLMNR/NBT-NS por GPO, exigir firma SMB y segmentar.

## Conclusiones

- LLMNR/NBT-NS activos permiten a cualquier equipo de la VLAN suplantar la resolución de nombres.
- La cadena acaba en NTLMv2 + diccionario = credenciales válidas.
- Un dispositivo no inventariado que responde a LLMNR es la señal más clara.

## Lecciones

- En el PCAP hay que mirar quién **responde**, no sólo quién pregunta.
- `hashcat -m 5600` es rapidísimo: la fortaleza de la contraseña es la única defensa.
- Un typo del usuario (`DCC01`) es el desencadenante: la mitigación es desactivar el protocolo, no educar.
