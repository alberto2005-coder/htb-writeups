---
challenge: The Suspicious Reviewer
type: OSINT
difficulty: Very Easy
platform: Hack The Box
state: Retired
tags: [osint, github, email, metadata, profiling]
---

# The Suspicious Reviewer — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; no jugada en este perfil.
> La respuesta es una dirección de correo; **no se publica** el valor real.

## TL;DR

El reto pide localizar el correo de una persona a partir de su perfil público de revisor. El dato está en la sección **About** del perfil y se confirma con los metadatos de sus commits. La flag es el correo, con el formato `HTB{<email>}`.

## 1. Del alias al perfil

Se parte del nombre o alias que da el enunciado. Se buscan coincidencias en GitHub, GitLab, X/Twitter y un blog personal. La clave es no quedarse con el primer resultado: se valida que la actividad (revisiones, repos, enlaces) corresponda a la persona descrita.

```bash
# API pública, sin autenticación para perfiles públicos
curl -s https://api.github.com/users/<USER> | jq '{login,name,bio,blog,email,created_at}'
```

El campo `email` suele ser `null`; el dato puede estar en la biografía, en el README del perfil o en un enlace `mailto:`.

## 2. La sección About

En el perfil, **About** agrupa bio, ubicación, empresa, sitio web y redes. Se revisan:

- La bio y el README del perfil (`<USER>/<USER>`).
- El enlace a la web personal; en ella, `Contact`, `About` o el pie.
- El HTML crudo, no solo el texto renderizado:

```bash
curl -sL https://<PERSONAL_SITE>/ | grep -oiE 'mailto:[^"<> ]+'
curl -sL https://github.com/<USER> | grep -oiE '[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}'
```

- El `whois` del dominio personal, si es propio y no está privado.
- Claves PGP publicadas: el UID suele incluir el correo.

## 3. Confirmar con commits

Los commits de Git incluyen el correo del autor. Es una segunda fuente independiente del perfil:

```bash
git clone --filter=blob:none https://github.com/<USER>/<REPO>.git
git -C <REPO> log --format='%an <%ae>' | sort -u
```

Si el correo de los commits coincide con el del About, la respuesta está confirmada. También se revisan las releases, los parches y los `Signed-off-by`.

## 4. Descartar señuelos

- Correos `noreply@github.com` o `users.noreply.github.com`: no son la respuesta.
- Direcciones de empresas o de un proyecto open source: pueden ser genéricas.
- Perfiles homónimos: se comparan foto, enlaces y actividad.
- Datos de terceros que aparecen en el mismo repositorio: no son la persona buscada.

## 5. Respuesta

La flag se construye con el correo exacto, respetando mayúsculas y dominio:

```text
HTB{<email>}
```

No se incluye el valor real en esta ficha. En un reto de OSINT, la respuesta es información personal: se documenta el método, no el dato.

## Lecciones aprendidas

- El About de un perfil público es la primera fuente, pero no la única.
- Los metadatos de Git son una fuente independiente y difícil de falsificar.
- Un `mailto:` en el HTML puede no verse en la página renderizada.
- Hay que distinguir el correo personal del `noreply` de la plataforma.
- No se publican datos personales aunque el reto los pida: la ficha explica cómo llegar, no el resultado.

## Mitigaciones (para el perfil analizado)

- Usar el correo `noreply` de GitHub en los commits.
- No publicar direcciones personales en bio, README o web.
- Revisar qué metadatos exponen los repositorios y las claves PGP.
- Separar la identidad profesional de la personal.

MITRE: T1593.003, T1589.002.

## Referencias

- <https://thehacksparrow.com/the-suspicious-reviewer/>
- <https://docs.github.com/en/account-and-profile/setting-up-and-managing-your-github-profile/customizing-your-profile/about-your-profile>
- <https://attack.mitre.org/techniques/T1589/002/>
