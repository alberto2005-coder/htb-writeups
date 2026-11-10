---
sherlock: Takedown
domain: DFIR / Red
difficulty: Easy
platform: Hack The Box
evidence: Captura de red de una intrusión con SMB y PowerShell
tools: [Wireshark, tshark, CyberChef]
state: Retired
tags: [dfir, dfir-/-red]
---


# Takedown — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> Investigación defensiva. Sin respuestas literales de la plataforma.

## Escenario

El equipo detecta un patrón anómalo en el tráfico: una intrusión que empieza con un fichero **VBS** dejado en un recurso compartido y sigue con la descarga de un script de PowerShell y balizamiento a un C2. Todo está en la captura.

## Evidencias

- Un PCAP con tráfico SMB2, HTTP y conexiones salientes.

## Investigación

1. **Sesión SMB**: negociación SMB2, autenticación (NTLM) y `Tree Connect` a un recurso.

```bash
tshark -r takedown.pcap -Y 'smb2' -T fields -e frame.number -e _ws.col.Info | head -40
```

2. **Fichero creado**: una petición `Create Request` deja un `.vbs` en el recurso compartido. Ese nombre es el IOC de acceso inicial.

3. **Ejecución**: el VBS lanza PowerShell, que descarga un script por HTTP; seguir el flujo para ver la URL y el contenido.

```bash
tshark -r takedown.pcap -Y 'http.request' -T fields -e http.host -e http.request.uri
```

4. **Autenticación robada**: si aparece un `NTLMSSP_AUTH`, el hash se ha reutilizado; el tipo y el usuario identifican el movimiento lateral.

5. **C2**: conexiones periódicas (POST) a una IP externa. Contar intervalos y tamaños da el perfil del *beacon*.

## Conclusiones

- Acceso inicial: un `.vbs` escrito en un recurso compartido mediante SMB2; la víctima lo ejecuta, no hay exploit remoto.
- El VBS lanza PowerShell y descarga el siguiente script por HTTP: la captura contiene la URL completa y el contenido.
- Hay reutilización de credenciales: `NTLMSSP_AUTH` con el hash del administrador permite `pass-the-hash` sin conocer la contraseña.
- El C2 se reconoce por la periodicidad de los `POST`, no por el contenido, que va cifrado o en base64.

## Lecciones

- Buscar el `.vbs` con un filtro HTTP es el error clásico: el fichero llega por **SMB2**, no por descarga web.
- En un PCAP con SMB conviene empezar por `Create Request`: ahí está el nombre y el recurso.
- La cadencia entre `POST` (y su tamaño constante) es lo que distingue un beacon de navegación normal.

## Qué enseña

- Un recurso compartido accesible es un punto de entrega: el atacante escribe, la víctima ejecuta.
- La secuencia SMB → VBS → PowerShell → HTTP es una cadena de intrusión completa en un solo PCAP.
- El tráfico NTLM en red plana permite pass-the-hash sin tocar la contraseña.

## Tropiezos

- **SMB2 comprimido o cifrado**: sin la clave de sesión sólo quedan metadatos.
- **Filtro por HTTP**: el VBS no viaja por HTTP, se escribe por SMB; hay que leer la captura en orden.
- **Beacon con jitter**: los intervalos irregulares no descartan C2; mirar también el destino.
