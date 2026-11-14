---
sherlock: Lockpick 4.0
category: Malware Analysis
difficulty: Insane
platform: Hack The Box
state: Retired
tags: [malware-analysis, ransomware, reverse-engineering, c2, iocs]
---

# Lockpick 4.0 — Hack The Box (Sherlock)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha metodológica; sin respuestas literales ni datos reales.

## Escenario

Forela.org sufre un ataque de ransomware. Los usuarios no pueden abrir archivos y aparece una nota de rescate. Se entrega una muestra del binario y artefactos de uno de los equipos. El objetivo es entender el cifrado, extraer la configuración y documentar los IOC.

## Evidencias

- Muestra del ransomware y nota de rescate.
- Volcado de memoria o triaje del equipo afectado.
- Archivos cifrados y extensiones modificadas.

```bash
file sample.exe
sha256sum sample.exe
strings -el sample.exe | head
```

## Investigación

### 1. Inventario y triaje

Se aísla la muestra, se calcula su hash y se revisan imports, secciones y firma. `PEStudio`, `capa` y `floss` identifican capacidades y cadenas ofuscadas. La nota de rescate se conserva como evidencia.

```bash
capa -v sample.exe
floss sample.exe
```

### 2. Línea temporal

El binario enumera unidades, detiene servicios y cifra archivos por extensiones. La configuración incluye la lista de extensiones, la clave pública y la URL del panel de pago. Se correlaciona con los eventos del equipo para fijar el orden.

```bash
vol -f memory.raw windows.netscan
vol -f memory.raw windows.malfind
```

### 3. Artefacto clave

La rutina de inicialización contiene la configuración cifrada. Al desofuscarla aparecen las extensiones objetivo, el nombre del mutex y el dominio del C2. La clave simétrica se protege con RSA; sin la clave privada no se puede descifrar, pero la configuración basta para detectar y contener.

## Conclusiones

- El ransomware usa cifrado híbrido y una configuración embebida.
- La nota y la extensión son IOC de alta confianza.
- El C2 y el panel de pago permiten bloquear la infraestructura.
- La recuperación requiere restaurar copias, no pagar.

## Lecciones

- La configuración del ransomware es tan valiosa como la muestra.
- `floss` y `capa` aceleran el triaje de binarios ofuscados.
- Los mutex y extensiones ayudan a detectar variantes.
- Documentar IOC sin publicar claves ni datos de víctimas.

## Referencias

- <https://www.hackthebox.com/sherlocks>
- <https://blog.w4nders.sg/writeups/sherlockLockpick4>
- <https://attack.mitre.org/techniques/T1486/>
