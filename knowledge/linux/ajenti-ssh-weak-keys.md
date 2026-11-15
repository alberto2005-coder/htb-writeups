---
topic: Ajenti — claves SSH débiles y whitelist
tags: [linux, ajenti, ssh, cve-2008-0166, privesc]
---

# Ajenti — claves SSH débiles y whitelist

[🌐 English](ajenti-ssh-weak-keys.en.md) | **Español**

## Concepto

Ajenti es un panel de administración que puede exponer claves SSH y reglas de acceso. Las claves generadas por Debian con OpenSSL vulnerable (CVE-2008-0166) tienen un espacio de entropía reducido y se pueden regenerar. Si además el panel permite editar `/etc/hosts.allow`, se habilita la IP del atacante y se entra con la clave.

## Cuándo aplica

- Ajenti es accesible con credenciales débiles o reutilizadas.
- El panel muestra o descarga claves SSH.
- TCP wrappers limita SSH y el panel edita la whitelist.

## Procedimiento

1. Acceder a Ajenti y revisar usuarios y claves.
2. Descargar la clave y comprobar si es débil.
3. Añadir la IP atacante a la whitelist de SSH.
4. Conectarse con la clave y escapar del shell restringido.

## Comandos

```bash
curl -k https://<HOST>:8000/
# Descargar clave desde Ajenti
ssh-keygen -y -f key
ssh -i key <USER>@<HOST>
# Whitelist
curl -k -X POST https://<HOST>:8000/api/hosts.allow -d "ip=<IP>"
```

## Variantes

- Regenerar claves débiles con `g0tmi1k/debian-ssh`.
- Editar la whitelist desde un panel alternativo.
- Usar la clave para otro usuario con la misma clave.

## Limitaciones

- El panel puede exigir 2FA.
- La clave puede no ser débil.
- El servicio SSH puede filtrar por otro mecanismo.

## Mitigación

- Regenerar claves SSH y usar Ed25519.
- Restringir Ajenti y no exponer claves.
- Gestionar el acceso con un bastión, no con listas editables.

## Detección

- Descargas de claves desde el panel.
- Cambios en `hosts.allow` fuera de cambios.
- Accesos SSH con claves antiguas.

## Referencias

- [Ajenti — Documentation](https://docs.ajenti.org/)
- [0xdf — FluJab](https://0xdf.gitlab.io/2019/06/15/htb-flujab.html)
- [CVE-2008-0166 — Debian OpenSSL](https://nvd.nist.gov/vuln/detail/CVE-2008-0166)
