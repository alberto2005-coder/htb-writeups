---
machine: DevArea
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, web, ftp, cxf, ssrf, cve-2022-46364, cve-2025-54123, privesc]
---

# DevArea — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

Un FTP anónimo entrega el JAR de un servicio de empleados. El servicio SOAP usa Apache CXF 3.2.14 y es vulnerable a CVE-2022-46364: un `xop:Include` con `href="file://..."` dentro de una petición `multipart/related` lee archivos del servidor. La lectura expone las credenciales del panel Hoverfly, cuya inyección de comandos en el middleware (CVE-2025-54123) da una shell como `dev_ryan`. Una cookie de SysWatch forjada con un secreto legible y un filtro débil permite llegar a `syswatch`, y el doble symlink de `syswatch.sh` lee la clave privada de root.

## Reconocimiento

```bash
nmap -Pn -sCV -p21,22,80,8080,8500,8888 <IP>
```

- `21` FTP anónimo, `22` OpenSSH y `80`/`8080` aplicaciones web.
- `8500` es el proxy de Hoverfly y `8888` su panel de control.
- El FTP contiene `employee-service.jar`; el WSDL está en `8080`.

## Enumeración

Se descompila el JAR y se revisa el WSDL en `http://<IP>:8080/employeeservice?wsdl`. La operación `submitReport` recibe un objeto `report` con `confidential`, `content`, `department` y `employeeName`. La línea de proceso (`ps`) y `/etc/systemd/system/hoverfly.service` exponen el usuario y la contraseña del panel, y el dashboard responde en `8888`.

## Foothold

El servicio usa CXF 3.2.14, anterior a 3.4.10/3.5.5. Para que CXF procese XOP hay que enviar el sobre como parte raíz de un `multipart/related` con tipo `application/xop+xml`. El `href` acepta `file:///etc/passwd` y el contenido aparece en la respuesta.

```bash
curl -s http://<IP>:8080/employeeservice \
  -H 'Content-Type: multipart/related; type="application/xop+xml"; boundary="MIME_boundary"' \
  --data-binary @poc.xml
```

## Movimiento lateral

Las credenciales del panel Hoverfly permiten autenticarse en `8888`. Hoverfly 1.11.3 y anteriores ejecuta el comando del middleware sin validarlo (CVE-2025-54123); el payload en `/api/v2/hoverfly/middleware` da una shell como `dev_ryan`. Después, SysWatch: el secreto de sesión está en un archivo de entorno legible, se forja la cookie y se inyecta un `service` que esquiva el filtro, lo que da acceso como `syswatch`.

```bash
ps auxww | grep -i hoverfly
curl -s http://<IP>:8888/
```

## Escalada de privilegios

El directorio `logs/` es escribible y `dev_ryan` puede ejecutar `syswatch.sh logs` con sudo. `syswatch.sh logs <fichero>` resuelve los symlinks con `ls -l | awk '{print $NF}'`, que solo mira un salto. Un enlace `flag.log -> redirect` y `redirect -> /root/.ssh/id_ed25519` pasa la validación y muestra la clave privada, con la que se entra como root.

```bash
ln -s redirect flag.log
ln -s /root/.ssh/id_ed25519 redirect
sudo /opt/syswatch/syswatch.sh logs flag.log
```

## Evidencia

- JAR descargado por FTP anónimo.
- Respuesta SOAP con `/etc/passwd`.
- Credenciales de Hoverfly en la línea de proceso.
- Lectura de la clave de root a través del doble symlink.

## Lecciones aprendidas

- Los artefactos de build y los FTP anónimos filtran código y secretos.
- MTOM/XOP solo se procesa con el `Content-Type` correcto.
- Validar un symlink con `ls` no resuelve la cadena completa; hay que usar `realpath`.
- Un script con sudo que acepta nombres de archivo es una frontera de confianza.

## Mitigación y detección

- Actualizar CXF a 3.4.10/3.5.5 o superior y deshabilitar `file://` en `xop:Include`.
- Cerrar el FTP anónimo y rotar las credenciales expuestas.
- Resolver rutas con `realpath -e` y comprobar que quedan dentro del directorio permitido.
- Auditar ejecuciones de `syswatch.sh` y lecturas de claves SSH.

## Referencias

- [0xdf — DevArea](https://0xdf.gitlab.io/2026/07/04/htb-devarea.html)
- [IppSec — DevArea](https://www.youtube.com/watch?v=Unsgv70jpA4)
- [Hack The Box — DevArea](https://app.hackthebox.com/machines/devarea)
