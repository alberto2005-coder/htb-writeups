---
sherlock: Vantage
domain: DFIR / Red
difficulty: Very Easy
platform: Hack The Box
evidence: Dos capturas: servidor web y controlador de una nube privada
tools: [Wireshark, tshark, CyberChef]
---

# Vantage — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> Investigación defensiva. Sin respuestas literales de la plataforma.

## Escenario

Una empresa pequeña movió recursos a una **nube privada**; el servidor web de desarrollo quedó con la redirección al *dashboard*. Un supuesto atacante escribe diciendo que los datos se filtraron. Hay dos capturas: la del servidor web y la del controlador de la nube.

## Evidencia

- `web-server_2025-07-01.pcap` y `controller_2025-07-01.pcap`.

## Método

1. **Fase de descubrimiento**: miles de `GET /` con un `Host` distinto cada vez, recorriendo una wordlist en orden alfabético. Es **enumeración de subdominios**, no navegación.

```bash
tshark -r web-server_2025-07-01.pcap -Y 'http.request' -T fields -e http.host | sort | uniq -c | sort -rn | head
```

2. **Fase de explotación**: el `Host` se fija en un subdominio concreto y empiezan `POST` a un login y navegación normal. Ahí está la entrada.

3. **Correlacionar las dos capturas**: lo que se descarga en la web aparece después en la del controlador; sin cruzar ambas no se entiende el impacto.

```bash
tshark -r controller_2025-07-01.pcap -q -z conv,ip
```

4. **Servicios implicados**: en el controlador se ven llamadas a la API de la nube; identificar cuál gestiona autenticación (Keystone en OpenStack) ayuda a explicar el acceso.

5. **Cronología**: ordenar los dos ficheros por `frame.time` y marcar enumeración, login y primera descarga.

## Qué enseña

- Enumeración y explotación tienen firmas distintas: volumen y diversidad frente a repetición sobre un objetivo.
- Dos capturas valen más que una: la web muestra la entrada, el controlador muestra el alcance.
- Un `Host` que cambia en cada petición es la forma más clara de detectar *vhost fuzzing*.

## Tropiezos

- **Ruido TLS**: sin claves, sólo metadatos; centrarse en HTTP y en los flujos internos.
- **Zonas horarias**: los dos ficheros pueden no coincidir; normalizar antes de cruzar.
- **Subdominios comodín**: si todo responde 200, el código de estado no distingue; comparar tamaño de respuesta.
