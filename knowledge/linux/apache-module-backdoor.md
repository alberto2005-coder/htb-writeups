---
topic: Apache — módulo malicioso y sshd backdooreado
tags: [linux, apache, module, backdoor, sshd, reversing, privesc]
---

# Apache — módulo malicioso y sshd backdooreado

[🌐 English](apache-module-backdoor.en.md) | **Español**

## Concepto

Un atacante con root puede añadir un módulo Apache que descargue y reemplace binarios del sistema, como `sshd`. El módulo se carga con `LoadModule` y el binario modificado incluye una contraseña oculta que permite acceso root.

## Cuándo aplica

- Hay módulos Apache fuera del catálogo o con fechas anómalas.
- `mods-enabled` apunta a un `.so` sospechoso.
- El binario `sshd` tiene un tamaño o hash distinto.

## Procedimiento

1. Listar módulos y revisar fechas.
2. Analizar el `.so` con `strings` y un descompilador.
3. Identificar la URL de descarga y el binario reemplazado.
4. Revertir la comparación XOR de la contraseña.
5. Entrar por SSH como root.

## Comandos

```bash
apache2ctl -M
ls -l /usr/lib/apache2/modules/
cat /etc/apache2/mods-enabled/reader.load
strings -a /usr/lib/apache2/modules/mod_reader.so | less
# extraer los bytes, aplicar XOR 0x96 y probar la contraseña
ssh root@<IP>
```

## Variantes

- Módulos que enganchan `auth_password`.
- Descarga de un binario desde un dominio externo.
- Backdoor en PAM o en un servicio systemd.

## Limitaciones

- El módulo puede estar oculto o sin nombre.
- El binario puede estar parcheado de forma diferente.
- La contraseña puede requerir orden de bytes.

## Mitigación

- Verificar paquetes y módulos con el gestor de paquetes.
- Monitorizar cambios en `/usr/lib/apache2` y `/usr/sbin/sshd`.
- Aplicar integridad de archivos y alertas.

## Detección

- Módulos nuevos o fuera de paquete.
- Descargas desde Apache.
- Hashes de `sshd` distintos del paquete.

## Referencias

- [0xdf — Undetected](https://0xdf.gitlab.io/2022/07/02/htb-undetected.html)
- [Apache — modules](https://httpd.apache.org/docs/2.4/mod/)
- [MITRE — T1543](https://attack.mitre.org/techniques/T1543/)
