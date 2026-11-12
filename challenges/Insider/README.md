---
challenge: Insider
type: Forensics
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [forensics, firefox, credentials, sqlite, firepwd]
---

# Insider — Hack The Box (Challenge)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Reto documentado; sin flags reales.

## TL;DR

Se entrega una carpeta `Mozilla` con el perfil de Firefox de un empleado. `logins.json` contiene credenciales cifradas y `key4.db` la clave que las protege. Con el perfil completo, `firepwd` descifra el usuario y la contraseña de un Tomcat Manager; esa contraseña es la flag.

## Enunciado y superficie

- Forensics, Easy, retirado.
- Se entrega una carpeta con el perfil de Firefox (`Mozilla/Firefox/...`).
- El objetivo es recuperar la credencial almacenada.

```bash
find Mozilla -type f | head -40
```

## Reconocimiento

Los ficheros relevantes son:

```text
Mozilla/Firefox/Profiles/<profile>/logins.json
Mozilla/Firefox/Profiles/<profile>/key4.db
Mozilla/Firefox/Profiles/<profile>/pkcs11.txt
Mozilla/Firefox/Profiles/<profile>/cert9.db
```

`logins.json` es JSON y se puede leer directamente:

```bash
jq '.logins[] | {hostname, encryptedUsername, encryptedPassword}' logins.json
```

Los campos `encryptedUsername` y `encryptedPassword` están cifrados; no son base64 del texto claro.

## Análisis del código

Firefox deriva una clave a partir de `key4.db` (NSS) y del `globalSalt`. En perfiles antiguos, `key4.db` contiene la entrada `password-check`; `firepwd` reconstruye la clave, comprueba el check y descifra cada login con 3DES/AES según la versión.

```bash
sqlite3 key4.db '.tables'
sqlite3 key4.db 'select * from metaData;'
```

No hace falta atacar Firefox: el perfil está completo y la clave de usuario no está protegida por una contraseña maestra.

## Explicación del fallo

La contraseña maestra de Firefox está vacía. Sin ella, la clave que cifra el almacén se obtiene de `key4.db` y del perfil; el cifrado solo protege contra lectura casual, no contra un analista con los ficheros. La credencial de Tomcat queda recuperable.

## Reproducción local

```bash
git clone https://github.com/lclevy/firepwd
python3 firepwd/firepwd.py -d Mozilla/Firefox/Profiles/<profile>
```

La herramienta imprime el `hostname`, el usuario y la contraseña en claro. Se comprueba que el host corresponde a un panel de administración y que la contraseña tiene el formato de flag.

## Explotación

No hay servidor en este reto: la explotación es el descifrado.

```bash
python3 firepwd/firepwd.py -d Mozilla/Firefox/Profiles/<profile> | tee firepwd.txt
```

La salida correcta incluye una línea con el par usuario/contraseña; la contraseña es la flag. Se redacta en la evidencia.

## Evidencia

- `jq` mostrando el hostname y los campos cifrados.
- `key4.db` con las tablas `metaData` y `nssPrivate`.
- Ejecución de `firepwd` con la contraseña redactada.

## Lecciones aprendidas

- El perfil de Firefox es un artefacto forense completo: historial, sesiones, addons y credenciales.
- `logins.json` sin `key4.db` no basta; ambos forman el par.
- Una contraseña maestra vacía deja las credenciales recuperables.
- `firepwd` automatiza NSS, pero conviene saber qué ficheros necesita.

## Mitigaciones y detección

- Configurar una contraseña maestra fuerte y bloquear el perfil al cerrar sesión.
- No guardar credenciales de administración en el navegador.
- Cifrar el disco y proteger el perfil con permisos restrictivos.
- Detección: acceso anómalo a `logins.json`/`key4.db` y ejecución de herramientas de recuperación de credenciales.

## Referencias

- <https://7rocky.github.io/en/ctf/htb-challenges/forensics/insider/>
- <https://github.com/lclevy/firepwd>
- <https://support.mozilla.org/en-US/kb/secure-firefox-primary-password>
