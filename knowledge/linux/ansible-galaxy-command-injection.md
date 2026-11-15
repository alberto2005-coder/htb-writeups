---
topic: Ansible — inyección en ansible-galaxy
tags: [linux, ansible, ansible-galaxy, command-injection, privesc]
---

# Ansible — inyección en ansible-galaxy

[🌐 English](ansible-galaxy-command-injection.en.md) | **Español**

## Concepto

Un wrapper que construye una orden `ansible-galaxy role install` con un nombre controlado puede permitir inyección de comandos si no usa `execve` con argumentos separados. El nombre del rol se convierte en parte de una cadena de shell.

## Cuándo aplica

- Un binario o script root recibe un nombre de rol/JSON.
- La orden se construye como string y se ejecuta con `system`/`shell`.
- Se controla el nombre o la ruta.

## Procedimiento

1. Revisar el wrapper y el JSON esperado.
2. Probar `; id` en el nombre.
3. Convertirlo en una shell interactiva.
4. Leer el flag o escribir una clave.

## Comandos

```bash
echo '{"role": "x; bash"}' > /tmp/r.json
sudo /opt/runner2/runner2 /tmp/r.json
```

## Variantes

- Inyección en la ruta del rol.
- `ansible-galaxy` con `--role-file` controlado.
- Symlinks en el directorio de instalación.

## Limitaciones

- El wrapper puede validar el nombre.
- Puede usar `subprocess` con lista.
- El rol debe existir o fallar después de la inyección.

## Mitigación

- Usar `subprocess` con lista y sin shell.
- Validar nombres de rol con regex.
- No ejecutar wrappers como root.

## Detección

- Caracteres `;`, `$()` o `|` en nombres de rol.
- Procesos `ansible-galaxy` con shells hijas.
- Escrituras en `/root` desde el wrapper.

## Referencias

- [0xdf — Intuition](https://0xdf.gitlab.io/2024/09/14/htb-intuition.html)
- [Ansible — galaxy CLI](https://docs.ansible.com/ansible/latest/cli/ansible-galaxy.html)
- [CWE-78 — OS Command Injection](https://cwe.mitre.org/data/definitions/78.html)
