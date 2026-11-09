---
sherlock: Lockpick 3.0
domain: Análisis de malware
difficulty: Medium
platform: Hack The Box
evidence: Binario de Linux, volcado de memoria y estado de la VM
tools: [Volatility 3, Ghidra, strings, CyberChef]
---

# Lockpick 3.0 — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> Investigación defensiva. Sin respuestas literales de la plataforma.

## Escenario

El grupo detrás de **Lockpick** ha mejorado: esta vez sólo alcanzó un servidor de desarrollo, sin acceso remoto evidente —posible amenaza interna—. Piden ingeniería inversa del binario y análisis de los artefactos de la máquina.

## Evidencia

- `ubuntu-client`: el malware.
- `ubuntu-client-Snapshot2.vmem`: volcado de memoria.
- `ubuntu-client-Snapshot2.vmsn`: estado de la VM.

## Método

1. **Identidad**: hash del binario y tipo.

```bash
md5sum ubuntu-client; file ubuntu-client
strings -n 6 ubuntu-client | head -40
```

2. **Ofuscación**: las cadenas están **cifradas con XOR**; buscar el bucle y la clave en el desensamblado o probar XOR de un byte en CyberChef hasta que aparezca texto legible.

3. **Comunicación**: el binario monta peticiones a un endpoint (`/connect`) que devuelve **clave, IV y client_id** en JSON; otro endpoint sube ficheros. Eso es el esquema de cifrado.

4. **Memoria**: con **Volatility 3** sobre el `.vmem`, listar procesos y líneas de comandos (`windows.pslist`/`linux.bash` según perfil) para ver cómo se lanzó y qué servicios creó.

5. **Persistencia**: el malware crea y habilita una unidad de systemd (`ubuntu_running.service`): técnica **T1543.002**. El `.vmsn` confirma el estado del servicio.

## Qué enseña

- Un XOR de un byte se detecta por la entropía de las cadenas y se rompe probando claves.
- Un `client_id` junto a clave e IV indica cifrado simétrico con material entregado por el C2.
- El volcado de memoria conserva la línea de comandos y los servicios creados.
- Comparar `.vmem` y `.vmsn` distingue lo que estaba en RAM de lo que quedó configurado.

## Tropiezos

- **Perfil de memoria**: sin el símbolo correcto, Volatility devuelve vacío; comprobar versión del kernel.
- **Cadenas cifradas**: `strings` no basta; hay que descifrar o buscar en el desensamblado.
- **No ejecutar**: el binario se analiza estáticamente o en VM aislada.
