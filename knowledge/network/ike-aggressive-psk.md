---
topic: IKE — modo agresivo y crackeo de PSK
tags: [network, ike, ipsec, vpn, psk, hashcat]
---

# IKE — modo agresivo y crackeo de PSK

[🌐 English](ike-aggressive-psk.en.md) | **Español**

## Concepto

En IKEv1 en modo agresivo, el iniciador envía en el primer paquete la propuesta, el intercambio Diffie-Hellman, su identidad y un hash autenticado con la PSK. La identidad viaja en claro y el hash permite probar candidatos de PSK sin completar el handshake. Es el equivalente a capturar un hash de contraseña de red.

## Cuándo aplica

- UDP/500 abierto y respuesta IKE.
- El servidor permite modo agresivo (habitual con múltiples grupos o PSK por usuario).
- La PSK es débil o se reutiliza como contraseña de sistema.

## Procedimiento

1. Confirmar IKE con `ike-scan`.
2. Solicitar el handshake agresivo y anotar la identidad.
3. Guardar el material con `--pskcrack`.
4. Crackear con `hashcat -m 5400` y un diccionario.
5. Probar la PSK en SSH, VPN u otros servicios.

## Comandos

```bash
ike-scan -A <IP>
ike-scan -A <IP> --pskcrack=handshake.txt
hashcat -m 5400 handshake.txt rockyou.txt
```

## Variantes

- Fuerza bruta de identidad con `ike-scan -A -I <id>`.
- Ataque de diccionario con `psk-crack`.
- Uso de la PSK para establecer el túnel IPsec y pivotar.
- TFTP/69 expuesto puede entregar la configuración del router y confirmar la identidad.
- Reutilización de la PSK en cuentas locales.

## Limitaciones

- El modo principal no filtra la identidad.
- IKEv2 con PSK no es vulnerable de la misma forma.
- Una PSK larga y aleatoria resiste el diccionario.
- Algunos dispositivos limitan o deshabilitan el modo agresivo.

## Mitigación

- Usar IKEv2 en modo principal.
- PSK larga, aleatoria y distinta por usuario.
- Certificados en lugar de PSK cuando sea posible.
- No reutilizar secretos de red como contraseñas.

## Detección

- Muchos handshakes agresivos desde una misma IP.
- Identidades no válidas o barridos de UDP/500.
- Intentos de autenticación SSH con la PSK.
- TFTP/69 expuesto con configuraciones de red.
- Tráfico IKE desde hosts que no son la VPN.

## Referencias

- [RFC 7296 — IKEv2](https://datatracker.ietf.org/doc/html/rfc7296)
- [ike-scan — Documentación](https://github.com/royhills/ike-scan)
- [0xdf — Expressway](https://0xdf.gitlab.io/2026/03/07/htb-expressway.html)
