---
sherlock: Reaper
domain: DFIR / Active Directory
difficulty: Very Easy
platform: Hack The Box
state: Retired
tags: [dfir, ntlm-relay, llmnr, pcap, security-log, event-4624, event-5140]
---


# Reaper — Hack The Box

[⚑ English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de método; sin respuestas literales de la plataforma.

## Escenario

El SIEM alerta de un inicio de sesión sospechoso: la **IP y el nombre del equipo de origen no coinciden**. Se entrega la captura de red del momento y el log de seguridad de Windows; hay que correlacionarlos y explicar qué pasó.

## Evidencias

```text
Reaper/ntlmrelay.pcapng
Reaper/Security.evtx
```

## Investigación

### 1. La alerta, explicada

Windows guarda en el evento **4624** el `Workstation Name` que declara el cliente y la IP desde la que llega. Un atacante que retransmite una autenticación puede enviar el nombre de un equipo y venir de otra IP: ahí salta la regla.

```powershell
Get-WinEvent -Path .\Security.evtx -FilterXPath "*[System[EventID=4624]]" |
  Select-Object TimeCreated, @{n='msg';e={$_.Message}} | Format-List
```

Se anotan `LogonType` (3 = red), usuario, `Workstation Name`, IP y hora.

### 2. El error que abre la puerta

En el PCAP se ve a la víctima escribiendo mal el nombre de un recurso compartido (`\\FORELA-WKSTN00X\...`). Como el nombre no existe, el equipo lo pregunta por **LLMNR/NBNS** a toda la red:

```bash
tshark -r ntlmrelay.pcapng -Y 'llmnr || nbns' -T fields -e frame.number -e ip.src -e ip.dst -e llmnr.name -e nbns.name
```

El atacante responde y la víctima autentica contra él.

### 3. La retransmisión

Con `ntlmrelayx` el atacante no se queda con el hash: lo **retransmite** a otra máquina donde ese usuario tiene más privilegios. En el PCAP se ve la sesión SMB saliente y en el log de seguridad, el resultado:

- **4624** tipo 3 con el usuario víctima, pero desde la IP del atacante
- **5140** acceso al recurso compartido (`\\*\share`) en el equipo destino

```bash
tshark -r ntlmrelay.pcapng -Y 'smb2' -T fields -e ip.src -e ip.dst -e smb2.filename | sort -u
```

### 4. Cronología

Unir: error de nombre → consulta LLMNR → respuesta del atacante → autenticación SMB hacia el atacante → 4624/5140 en el equipo destino. El orden y los segundos entre pasos son la prueba; un 4624 aislado no demuestra relay.

## Conclusiones

- Vector: envenenamiento LLMNR/NBT-NS tras un nombre mal escrito.
- Técnica: **NTLM relay** contra otra estación, no cracking.
- Prueba: divergencia entre `Workstation Name` e IP en el 4624, más el 5140 en el destino.

## Lecciones

- Un nombre mal escrito es suficiente para que un usuario entregue su autenticación.
- El relay se detecta cruzando red y log: el hash capturado no aparece, porque no se captura, se reenvía.
- Mitigación: deshabilitar LLMNR/NBT-NS, exigir firma SMB y canal seguro LDAP, y segmentar estaciones entre sí.
