---
machine: Artificial
os: Linux
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [linux, tensorflow, keras, deserialization, backrest]
---

# Artificial — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

La aplicación carga modelos TensorFlow para hacer predicciones. Un modelo `.h5` con una capa Lambda maliciosa se deserializa en el servidor y da ejecución en el contenedor; un backup de Backrest expone credenciales y permite ejecutar hooks como root.

## Reconocimiento

```bash
nmap -Pn -p- --min-rate 10000 <IP>
nmap -Pn -sCV -p22,80 <IP>
ffuf -u http://<IP>/ -H "Host: FUZZ.artificial.htb" -w subdomains.txt
curl -s http://app.artificial.htb/ | head
# Subida de un modelo con una capa Lambda maliciosa
curl -F "model=@malicious.h5" http://app.artificial.htb/upload
# Tras el acceso
restic snapshots -r <REPO>
sudo -l
```

## Enumeración

- El sitio principal es una landing; el flujo real vive en un vhost de la aplicación.
- La subida de modelos acepta `.h5` y devuelve el resultado de la predicción.
- El contenedor guarda un backup de Backrest y la configuración de la base de datos.

## Acceso inicial

`tf.keras.models.load_model` no trata el archivo como datos inertes: al reconstruir una capa `Lambda` ejecuta la función serializada. Se sube un modelo con una Lambda que lanza una reverse shell y se obtiene una sesión como el usuario del servicio.

## Escalada de privilegios

El backup contiene la configuración de Backrest y credenciales reutilizables. Con acceso SSH se revisa el servicio; Backrest corre como root y permite definir hooks de backup, que se ejecutan con sus privilegios.

## Evidencia

- Respuesta de la subida con la predicción y errores de TensorFlow.
- Shell en el contenedor tras cargar el modelo.
- Hook de Backrest ejecutado como root.

## Lecciones aprendidas

- Los formatos de modelos de ML pueden contener código ejecutable.
- Un backup no es solo datos: incluye secretos y configuración de servicios.
- Los hooks de backups privilegiados son una vía directa a root.

## Mitigación y detección

- Cargar modelos con `safe_mode=True` o en un entorno aislado sin secretos.
- Firmar y validar los artefactos antes de deserializarlos.
- Ejecutar Backrest sin root y restringir sus hooks.

## Referencias

- [0xdf — Artificial](https://0xdf.gitlab.io/2025/10/25/htb-artificial.html)
- [Hack The Box — Artificial](https://app.hackthebox.com/machines/artificial)
- [TensorFlow — Security](https://www.tensorflow.org/responsible_ai)
