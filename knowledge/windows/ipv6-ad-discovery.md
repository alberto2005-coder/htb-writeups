---
topic: Descubrimiento de Active Directory por IPv6
tags: [windows, ad, ipv6, rpc, discovery]
---

# Descubrimiento de Active Directory por IPv6

[🌐 English](ipv6-ad-discovery.en.md) | **Español**

## Concepto

Un host puede filtrar los puertos de Active Directory en IPv4 pero seguir exponiéndolos en IPv6. RPC permite obtener la dirección IPv6 del DC y, al escanearla, aparecen DNS, Kerberos, LDAP, SMB y WinRM.

## Cuándo aplica

- IPv4 solo muestra HTTP y RPC.
- El endpoint RPC responde a `IOXIDResolver`.
- La red permite tráfico IPv6.

## Procedimiento

1. Consultar las interfaces del DC por RPC.
2. Escuchar la respuesta y extraer la IPv6.
3. Escanear todos los puertos sobre esa dirección.
4. Usar el nombre del dominio y actualizar `/etc/hosts`.

```bash
python3 IOXIDResolver.py -t <IP>
nmap -6 -p- --min-rate 10000 <IPv6>
nmap -6 -sCV -p53,88,389,445,5985 <IPv6>
```

## Variantes

- Usar `rpcclient` o `impacket` para consultar interfaces.
- Descubrir el DC por DNS y probar su IPv6.
- Escanear solo los puertos habituales de AD si el escaneo completo es lento.

## Limitaciones

- La red debe enrutar IPv6.
- El firewall puede filtrar también IPv6.
- La respuesta RPC puede requerir credenciales nulas.

## Mitigación y detección

- Filtrar IPv6 con las mismas reglas que IPv4.
- Deshabilitar IPv6 si no es necesario.
- Auditar RPC y el descubrimiento de interfaces.

## Referencias

- <https://learn.microsoft.com/en-us/windows/win32/rpc/rpc-start-page>
- <https://attack.mitre.org/techniques/T1016/>
- <https://0xdf.gitlab.io/2021/04/10/htb-apt.html>
