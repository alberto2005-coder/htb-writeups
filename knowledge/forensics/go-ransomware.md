---
topic: Ransomware escrito en Go
tags: [forensics, malware, go, ransomware, aes-gcm, static-analysis]
---

# Ransomware escrito en Go

[🌐 English](go-ransomware.en.md) | **Español**

## Concept

Los binarios de Go incluyen el runtime, numerosas cadenas y, a menudo, información de compilación. Un ransomware en Go suele usar bibliotecas estándar de cifrado, claves embebidas y recorridos de directorios. El análisis estático permite recuperar la clave sin ejecutar la muestra.

## Cuándo aplica

- Binarios grandes con cadenas de Go (`runtime.main`, `go.buildid`).
- Archivos cifrados con extensión añadida.
- Notas de rescate con instrucciones de pago.
- Muestras con C2 HTTP o webhooks.

## Procedimiento

1. Calcular hashes y identificar el binario.
2. Extraer cadenas y la versión de Go.
3. Localizar la función de cifrado y la clave.
4. Revisar el algoritmo y el formato del archivo.
5. Descifrar una copia y verificar el resultado.

```bash
file sample.exe
strings -n 8 sample.exe | grep -iE 'go1\.|AES|GCM|encrypt'
go version -m sample.exe
```

## Variantes

- AES-GCM con clave y nonce embebidos.
- ChaCha20 o XOR con clave derivada.
- Cifrado por archivo con nonce aleatorio.
- Clave enviada a un C2 antes de cifrar.
- Ransomware con propagación por unidades de red.

## Limitaciones

- La clave puede estar cifrada por un loader.
- El binario puede estar empaquetado o ofuscado con garble.
- Sin muestra original no se puede verificar el descifrado.
- Algunas variantes borran la clave tras cifrar.

## Mitigación y detección

- Copias de seguridad inmutables y pruebas de restauración.
- Bloquear ejecución desde rutas de usuario y correo.
- Monitorizar creación masiva de archivos y extensiones anómalas.
- Alertar de procesos que recorren muchos directorios y de conexiones a webhooks.

## Referencias

- <https://attack.mitre.org/techniques/T1486/>
- <https://go.dev/doc/build-info>
- <https://pkg.go.dev/crypto/cipher>
- <https://www.cisa.gov/stopransomware>
