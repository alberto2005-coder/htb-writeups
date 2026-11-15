---
topic: BGP — secuestro de rutas y captura de tráfico
tags: [network, bgp, routing, mitm, ftp]
---

# BGP — secuestro de rutas y captura de tráfico

[🇬🇧 English](bgp-hijack.en.md) | **Español**

## Concepto

BGP intercambia prefijos entre sistemas autónomos sin autenticación por defecto. Un router comprometido puede anunciar un prefijo más específico que el legítimo; los routers vecinos prefieren esa ruta y el tráfico del host pasa por el atacante, que puede capturarlo o modificarlo.

## Cuándo aplica

- Se controla un router con sesión BGP establecida.
- El vecino acepta anuncios sin RPKI ni filtros de prefijos.
- El tráfico interesante (FTP, HTTP, SMTP) atraviesa ese router.

## Procedimiento

1. Revisar vecinos, prefijos y tablas con `show ip bgp summary`.
2. Anunciar un prefijo `/32` o más específico hacia el host objetivo.
3. Comprobar que la ruta cambia en la tabla del router.
4. Capturar el tráfico con `tcpdump` o redirigirlo a un listener.

```bash
router bgp 65001
 network 10.10.10.0 mask 255.255.255.0
 neighbor 10.10.10.1 remote-as 65000
```

```bash
tcpdump -i any -nn -A 'tcp port 21'
```

## Variantes

- Anunciar el prefijo del servidor FTP para robar credenciales.
- Redirigir DNS o HTTP a un servidor controlado.
- Usar un prefijo más específico que el anuncio original.

## Limitaciones

- RPKI, BGPsec o filtros de prefijos bloquean el anuncio.
- La sesión debe estar autenticada con MD5 o TCP-AO.
- El tráfico puede estar cifrado (FTPS, HTTPS).

## Mitigación

- Firmar rutas con RPKI y BGPsec.
- Filtrar prefijos y usar max-prefix.
- Autenticar sesiones BGP y monitorizar cambios de ruta.

## Detección

- Anuncios nuevos de prefijos más específicos.
- Cambios de next-hop sin mantenimiento.
- Caídas de latencia o tráfico asimétrico.

## Referencias

- [RFC 4271 — BGP](https://www.rfc-editor.org/rfc/rfc4271)
- [0xdf — Carrier](https://0xdf.gitlab.io/2019/03/16/htb-carrier.html)
- [MITRE ATT&CK — T1557](https://attack.mitre.org/techniques/T1557/)
