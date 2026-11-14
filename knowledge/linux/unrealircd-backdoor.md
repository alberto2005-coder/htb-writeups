---
topic: Backdoor en UnrealIRCd 3.2.8.1
tags: [linux, unrealircd, backdoor, irc, cve-2010-2075, supply-chain]
---

# Backdoor en UnrealIRCd 3.2.8.1

[🌐 English](unrealircd-backdoor.en.md) | **Español**

## Concepto

La versión 3.2.8.1 distribuida desde el sitio oficial entre 2009 y 2010 incluía una puerta trasera. El binario aceptaba el comando `AB;` seguido de una instrucción y la ejecutaba con los privilegios del servicio.

## Cuándo aplica

- Servicio IRC en el puerto 6667.
- Banner `UnrealIRCd` con versión 3.2.8.1.
- Contenedores o imágenes antiguas sin actualizar.
- Retos y laboratorios que replican la versión vulnerable.

## Procedimiento

1. Identificar el servicio y la versión con `nmap` o el banner.
2. Confirmar la versión vulnerable.
3. Enviar `AB;` con un comando de prueba.
4. Usar una reverse shell si el comando se ejecuta.
5. Verificar el usuario del servicio.

```bash
nmap -Pn -sV -p 6667 <IP>
printf 'AB;id\n' | nc <IP> 6667
```

## Variantes

- Ejecución directa de comandos con `AB;`.
- Descarga y ejecución de un script remoto.
- Servicio ejecutado como root en imágenes antiguas.
- Backdoor incluida en un tarball de cadena de suministro.

## Limitaciones

- Solo afecta a la distribución comprometida de 3.2.8.1.
- El servicio debe aceptar conexiones del atacante.
- Algunos despliegues ejecutan el daemon como usuario sin privilegios.
- La versión puede estar parcheada aunque el banner la imite.

## Mitigación y detección

- Actualizar UnrealIRCd y verificar hashes de los paquetes.
- Ejecutar el servicio con un usuario dedicado y sin shell.
- Restringir el puerto a redes de confianza.
- Alertar de comandos `AB;` y de procesos hijos del daemon IRC.

## Referencias

- <https://nvd.nist.gov/vuln/detail/CVE-2010-2075>
- <https://www.exploit-db.com/exploits/16922>
- <https://attack.mitre.org/techniques/T1195/001/>
- <https://www.unrealircd.org/>
