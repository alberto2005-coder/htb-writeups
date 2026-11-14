---
machine: PikaTwoo
os: Linux
difficulty: Insane
platform: Hack The Box
state: Retired
tags: [linux, openstack, apisix, kubernetes, cr8escape]
---

# PikaTwoo — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

La API tiene SQLi y filtra un correo válido. Una versión antigua de APISIX permite saltarse el bloqueo de `/private` con `//`, resetear la contraseña y autenticarse. Después, una regla de ModSecurity se evade para conseguir LFI y RCE en el pod de la API. El token de Kubernetes filtra la clave de APISIX, que da RCE en su pod; credenciales en un archivo permiten SSH y `cr8escape` (CVE-2022-0811) da root.

## Reconocimiento

```bash
nmap -Pn -p- --min-rate 10000 <IP>
nmap -Pn -sCV -p<PORTS> <IP>
```

```text
22/tcp    ssh
80/tcp    http    nginx
443/tcp   https   APISIX 2.10.1
4369/tcp  epmd
5000/tcp  keystone
5672/tcp  amqp
8080/tcp  swift
25672/tcp rabbitmq
35357/tcp keystone admin
```

## Enumeración

- El APK de Android y la API de Pokedex se anuncian en el sitio.
- La API tiene SQLi; se filtra un correo registrado.
- APISIX 2.10.1 bloquea `/private` con `uri-block`.
- El pod de la API monta un token de service account de Kubernetes.

## Foothold

La SQLi de la API se explota para obtener un correo válido. Con APISIX 2.10.1, `//private/` evita la regla que bloquea `/private`; se accede a la documentación privada y se resetea la contraseña del correo.

Tras autenticarse, una regla de ModSecurity/CRS se evade para conseguir LFI. Se abusa de archivos temporales de nginx para escribir y ejecutar una reverse shell en el pod.

```bash
curl -k https://<IP>/%70rivate/login
curl -k -X POST https://<IP>/%70rivate/login -d 'email=<EMAIL>&password=<PASSWORD>'
```

## Movimiento lateral

El pod de la API tiene un token de service account. Se consulta la API de Kubernetes y se leen los secretos del namespace, incluida la clave de administración de APISIX.

Con esa clave se usa `CVE-2022-24112` en `batch-requests` para crear una ruta con `filter_func` y ejecutar comandos en el pod de APISIX. Un archivo de configuración contiene credenciales de `andrew`, que permiten SSH al host.

```bash
curl --cacert ca.crt -H "Authorization: Bearer $TOKEN"   https://kubernetes.default.svc/api/v1/namespaces/$NS/secrets
```

## Escalada de privilegios

`andrew` puede usar `kubectl` con la configuración de otro usuario, pero no listar pods. La versión de CRI-O es vulnerable a `cr8escape` (CVE-2022-0811): se crea un pod que inyecta `kernel.core_pattern` y se provoca un crash para ejecutar un script en el host como root.

```bash
kubectl --kubeconfig /home/<USER>/.kube/config get pods
# crear pod con sysctl malicioso y provocar SIGSEGV
```

## Evidencia

- Salidas recortadas de los comandos clave; sin flags, credenciales ni tokens.
- Los valores reales, si existen, viven en `private/` y no se publican.

## Lecciones aprendidas

- Una SQLi puede ser el primer paso de una cadena cloud compleja.
- Normalizar la URL antes de aplicar reglas de bloqueo es crítico.
- Los tokens de service account deben tener permisos mínimos.
- CRI-O sin parche permite escapar del contenedor con `core_pattern`.

## Mitigaciones y detección

- Parametrizar SQL y validar la entrada de la API.
- Actualizar APISIX y normalizar rutas antes de `uri-block`.
- Restringir secretos y RBAC de las service accounts.
- Actualizar CRI-O y bloquear sysctls peligrosos.

## Referencias

- [0xdf — PikaTwoo](https://0xdf.gitlab.io/2023/09/09/htb-pikatwoo.html)
- [Búsqueda de vídeos (CSV)](https://www.youtube.com/results?search_query=ippsec+pikatwoo)
- [Búsqueda de writeups (CSV)](https://medium.com/search?q=hackthebox+pikatwoo+writeup)
