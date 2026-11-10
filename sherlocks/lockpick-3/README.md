---
sherlock: Lockpick 3.0
domain: Análisis de malware
difficulty: Hard
platform: Hack The Box
evidence: ELF de Linux, volcado de memoria y estado de la VM
tools: [Volatility 3, Ghidra, strings, CyberChef]
state: Retired
tags: [dfir, malware, ransomware, linux, xor, systemd, memoria]
---

# Lockpick 3.0 — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> Investigación defensiva. Sin respuestas literales de la plataforma.

## Escenario

El grupo de **Lockpick** ha mejorado: esta vez sólo alcanzó un servidor de desarrollo, sin acceso remoto evidente —posible amenaza interna—. Piden ingeniería inversa del binario y análisis de los artefactos de la máquina.

## Evidencias

- `ubuntu-client`: el malware (ELF, MD5 `a2444b61b65be96fc2e65924dee8febd`).
- `ubuntu-client-Snapshot2.vmem`: volcado de memoria.
- `ubuntu-client-Snapshot2.vmsn`: estado de la VM.

## Investigación

1. **Identidad**: `md5sum` y `file`; es un ELF de Linux, así que se analiza con `objdump -d`/Ghidra, no con herramientas de Windows.

2. **Cadenas cifradas**: el binario guarda su configuración con un **XOR repetido**. La clave **no está en el fichero**: se pasa por línea de comandos (`./ubuntu-client <clave>`). Por eso `strings` del binario no basta y hay que mirar el `.vmem`, donde la línea de comandos del proceso conserva la clave.

```bash
strings -n 8 ubuntu-client-Snapshot2.vmem | grep ubuntu-client
```

3. **Descifrar**: con la clave del comando se invierte el XOR sobre la sección de datos y aparecen la URL base del C2, los endpoints (`/connect` para clave/IV/`client_id` y `/uploads/` para exfiltración) y una unidad de systemd completa.

4. **Comunicación**: `_cJSON_GetObjectItem` confirma que la respuesta de `/connect` es JSON con el material criptográfico; el `client_id` identifica la víctima.

5. **Persistencia**: el malware escribe y habilita `ubuntu_running.service` en `/etc/systemd/system` (técnica **T1543.002**). El `.vmsn` confirma el estado del servicio y el `.vmem` el proceso en ejecución.

## Hallazgos

- C2 alojado en PaaS (`*.ondigitalocean.app`), lo que complica el bloqueo por IP.
- Cadena de claves entregada por el servidor: cifrado simétrico con material remoto.
- Persistencia por unidad systemd creada por el propio binario.

## Lecciones

- Si la clave va por argumento, el binario no la delata: la memoria sí.
- Un XOR repetido se rompe en cuanto se conoce la clave; el reto es encontrarla, no el algoritmo.
- Comparar `.vmem` y `.vmsn` separa lo que estaba en RAM de lo que quedó configurado en disco.

## Tropiezos

- **Perfil de memoria**: es Linux; usar `linux.bash`/`linux.pslist`, no los plugins de Windows.
- **Cadenas ofuscadas**: `strings` sobre el ELF no muestra la config; hay que descifrar.
- **No ejecutar**: análisis estático o VM aislada.
