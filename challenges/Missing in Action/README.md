---
challenge: Missing in Action
type: OSINT
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [osint, social-media, google-dorks, geolocation]
---

# Missing in Action — Hack The Box (Challenge)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Reto documentado; sin datos personales reales.
> Los nombres y perfiles del enunciado son ficticios. No se enlazan cuentas ni se publican identificadores.

## TL;DR

El enunciado da un nombre y una ciudad: una persona desapareció durante un viaje de negocios. Buscando el nombre en LinkedIn se llega a la empresa; la cuenta de la empresa en Twitter lleva a un perfil de Foursquare con reseñas y ubicaciones. Un dork sobre el nombre y la empresa encuentra una publicación con la flag.

## Enunciado y superficie

- OSINT, Easy, retirado.
- No se entrega ningún fichero: solo una descripción con nombre, ciudad y contexto.
- El objetivo es localizar actividad pública de la persona.

## Reconocimiento

Se trabaja con el navegador y con buscadores, no con herramientas de escaneo. La primera consulta combina el nombre y la ciudad:

```text
"<nombre>" "<ciudad>"
```

El resultado principal es un perfil de LinkedIn. La empresa indicada en el perfil es la pista para el siguiente salto.

## Análisis

La empresa tiene presencia en Twitter. Sus publicaciones enlazan a Foursquare, donde aparecen reseñas y lugares visitados. Esa combinación permite reconstruir el itinerario del viaje.

```text
site:twitter.com "<empresa>"
site:foursquare.com "<empresa>"
```

Con la empresa y el nombre se prueban dorks más específicos:

```text
"<nombre>" "<empresa>" site:*
"<nombre>" "<ciudad>" "flag"
```

La flag está en una publicación pública asociada al perfil; no hace falta autenticarse ni interactuar con nadie.

## Explicación del fallo

La persona usó el mismo nombre y la misma empresa en varias redes, y publicó actividad de viaje sin restringir la audiencia. La correlación de identidad entre LinkedIn, Twitter y Foursquare es suficiente para llegar al contenido. El reto demuestra que la huella digital se construye por acumulación de pequeñas publicaciones.

## Reproducción local

No hay un exploit que ejecutar. Se documenta la secuencia de consultas y se guarda una captura redactada de cada salto. Se recomienda usar un navegador aislado y no iniciar sesión con cuentas personales.

```text
1. nombre + ciudad -> LinkedIn -> empresa
2. empresa -> Twitter -> enlace a Foursquare
3. nombre + empresa + dork -> publicación con la flag
```

## Explotación

La "explotación" es OSINT pasivo: no se envía ningún mensaje, no se sigue a la persona y no se accede a contenido privado. La flag se copia de la publicación y se verifica en la plataforma.

## Evidencia

- Captura del perfil de LinkedIn con datos personales difuminados.
- Captura de la cuenta de la empresa y del enlace a Foursquare.
- Publicación con la flag redactada.

## Lecciones aprendidas

- La correlación de identidad entre redes es más potente que una sola búsqueda.
- Los dorks con empresa y nombre reducen el ruido.
- La geolocalización pública puede reconstruir un itinerario.
- El OSINT ético se limita a información pública y no interactúa con la persona.

## Mitigaciones y detección

- Revisar la privacidad de las cuentas y separar identidad personal y profesional.
- No publicar ubicaciones en tiempo real ni detalles de viajes.
- Usar alias distintos por comunidad cuando sea posible.
- Detección: alertas de búsqueda del propio nombre y auditoría periódica de la huella pública.

## Referencias

- <https://7rocky.github.io/en/ctf/htb-challenges/osint/missing-in-action/>
- <https://www.google.com/search?q=Google+advanced+search+operators>
- <https://osintframework.com/>
