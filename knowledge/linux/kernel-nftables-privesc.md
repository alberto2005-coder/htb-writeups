---
topic: nftables kernel privilege escalation
tags: [linux, kernel, nftables, cve-2023-35001, privesc, uaf]
---

# nftables kernel privilege escalation

[🌐 English](kernel-nftables-privesc.en.md) | **Español**

## Concepto

CVE-2023-35001 es una escritura fuera de límites en `nf_tables` que permite a un usuario local manipular memoria del kernel y elevar privilegios. Afecta a determinados kernels 5.19 y derivados; el exploit público de Synacktiv encadena la corrupción con una escalada a root.

## Cuándo aplica

- Kernel dentro del rango vulnerable.
- Usuario local sin privilegios.
- `nf_tables` disponible.
- Capacidad de ejecutar un exploit compilado.

## Procedimiento

1. Confirmar la versión del kernel.
2. Comprobar si `nf_tables` está cargado.
3. Verificar que el exploit corresponde a la arquitectura.
4. Ejecutarlo y comprobar la identidad.
5. Leer archivos privilegiados o estabilizar el acceso.

```bash
uname -a
lsmod | grep nf_tables
gcc exploit.c -o exploit
./exploit
id
```

## Variantes

- Adaptación del exploit a otra versión o distribución.
- Uso de `unshare` para preparar namespaces.
- Encadenamiento con una shell SUID o `setuid(0)`.
- Aprovechamiento de otras CVEs de nf_tables del mismo periodo.

## Limitaciones

- El kernel debe estar dentro del rango afectado.
- KASLR y mitigaciones pueden requerir ajustes.
- El exploit puede ser inestable y provocar un panic.
- Un kernel parcheado invalida la técnica.

## Mitigación y detección

- Actualizar el kernel.
- Restringir `unshare` y namespaces de usuario.
- Aplicar protecciones de memoria y módulos firmados.
- Alertar de compilaciones, ejecutables nuevos y fallos del kernel.

## Referencias

- <https://nvd.nist.gov/vuln/detail/CVE-2023-35001>
- <https://github.com/synacktiv/CVE-2023-35001>
- <https://attack.mitre.org/techniques/T1068/>
