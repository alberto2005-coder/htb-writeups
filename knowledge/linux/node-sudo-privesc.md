---
topic: Node.js — ejecución arbitraria con sudo
tags: [linux, nodejs, sudo, child-process, privesc]
---

# Node.js — ejecución arbitraria con sudo

[🌐 English](node-sudo-privesc.en.md) | **Español**

## Concepto

Una regla sudo que permite ejecutar Node.js sobre un script concreto puede ser insuficiente si el script carga módulos desde una ruta controlable o si se puede pasar `-e`. Node.js es un intérprete completo: `child_process` ejecuta comandos con el UID efectivo de sudo, es decir, root.

## Cuándo aplica

- `sudo -l` muestra `node` o un wrapper de Node.js.
- El script importa módulos de un directorio escribible.
- Se permite `-e`, `--eval` o argumentos no validados.

## Procedimiento

1. Revisar la regla sudo y el script.
2. Comprobar si se puede inyectar `-e` o un módulo.
3. Ejecutar `child_process` para lanzar una shell.
4. Verificar el UID y la elevación.

## Comandos

```bash
sudo -l
sudo node -e 'require("child_process").spawn("/bin/sh",{stdio:"inherit"})'
# Si solo permite un script
ls -la /opt/app/node_modules
echo 'require("child_process").execSync("id")' > /opt/app/node_modules/local/index.js
sudo /usr/bin/node /opt/app/script.js
```

## Variantes

- Envenenar `node_modules` o `NODE_PATH`.
- Aprovechar un `require` de una ruta relativa.
- Usar `--inspect` para adjuntar un depurador.

## Limitaciones

- La regla puede limitar los argumentos.
- El script puede usar rutas absolutas.
- El directorio puede ser de solo lectura.

## Mitigación

- No permitir intérpretes completos en sudo.
- Fijar argumentos y rutas absolutas.
- Ejecutar scripts con un usuario dedicado.

## Detección

- `sudo node` desde cuentas no administrativas.
- Módulos nuevos en `node_modules`.
- Procesos hijos de Node.js con `/bin/sh`.

## Referencias

- [Node.js — child_process](https://nodejs.org/api/child_process.html)
- [0xdf — Stocker](https://0xdf.gitlab.io/2023/06/24/htb-stocker.html)
- [CWE-269 — Improper Privilege Management](https://cwe.mitre.org/data/definitions/269.html)
