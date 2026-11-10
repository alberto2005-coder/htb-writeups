---
sherlock: SSHole
domain: DFIR / Unix
difficulty: Very Easy
platform: Hack The Box
evidence: Evidencias de un jumpbox Linux comprometido
tools: [grep, journalctl, auth.log, tcpdump]
state: Retired
tags: [dfir, dfir-/-unix]
---


# SSHole — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> Investigación defensiva. Sin respuestas literales de la plataforma.

## Escenario

Un *jumpbox* mal configurado empieza a generar tráfico hacia un dominio sospechoso. Se entrega la evidencia recogida del propio servidor: hay que averiguar **cómo entraron** y **qué hicieron después**.

## Evidencias

- Archivos del jumpbox (logs de autenticación, historial, configuraciones) empaquetados en un ZIP con la contraseña habitual de los Sherlocks.

## Investigación

1. **¿Cómo entraron?** El jumpbox es **Alpine Linux** y su `sshd` acepta un *bypass* de autenticación (CVE-2026-123158): un `crypt()` de Alpine devuelve `*` cuando la contraseña supera 256 bytes, y en `/etc/shadow` una cuenta sin contraseña también guarda `*`. El servidor compara `*` con `*` y **acepta el login** sin conocer la contraseña.

```bash
grep -i 'sshd' auth.log | less
grep -c 'Failed password' auth.log
```

Un acceso exitoso sin fase de autenticación previa (ni *password* ni *publickey*) apunta a un **bypass** del servidor SSH, no a fuerza bruta. El usuario es la cuenta de servicio `adminsvc`, sin contraseña válida, y el log no registra el valor enviado: el bypass se **infiere**, no se lee.

2. **Sesión del atacante**: correlacionar la IP de origen con el resto de artefactos.

```bash
last -ai | head
grep '<IP>' auth.log
```

3. **Qué hicieron**: historial, ficheros nuevos en `/tmp` y descargas.

```bash
cat ~/.bash_history
ls -la /tmp /var/tmp /dev/shm
```

4. **Reconocimiento interno**: el jumpbox se usa para escanear la red detrás. En los artefactos aparece un barrido de `192.168.18.0/24`, un script ejecutado y una subida a un dominio externo (`devv.coding.eu`): el jumpbox era el pivote, no el objetivo.

5. **Persistencia**: revisar `~/.ssh/authorized_keys`, `cron` y unidades de systemd añadidas.

## Conclusiones

- Entrada: bypass de autenticación de `sshd` en Alpine, sin fuerza bruta y sin credencial válida.
- La cuenta `adminsvc` no tenía contraseña: el fallo de `crypt()` la convirtió en puerta abierta.
- Uso posterior: escaneo de `192.168.18.0/24`, ejecución de un script y exfiltración a un dominio externo.

## Lecciones

- Un jumpbox es el peor sitio para una versión sin parchear: multiplica el alcance del atacante.
- Comparar `*` con `*` es una autenticación rota por diseño; conviene revisar cómo trata `crypt()` los errores.
- Si el log no guarda la contraseña, la conclusión se sostiene con la **ausencia** de `password`/`publickey` y el éxito de la sesión.

- Sin el parche, una cuenta con `*` en `/etc/shadow` sigue siendo una puerta abierta: el fallo no está en la contraseña, está en cómo se compara.

## Qué enseña

- Un servidor SSH vulnerable se compromete **sin credenciales**: el patrón de log es distinto al de una fuerza bruta.
- Un jumpbox es una plataforma de pivote: el valor forense está en el tráfico *saliente* posterior.
- Comparar `auth.log` con `last` y el historial reconstruye la sesión.

## Tropiezos

- **Ruido de escaneos**: filtrar por IP y por ventana temporal antes de sacar conclusiones.
- **Logs rotados**: si falta el rango, mirar `.1` y `journalctl`.
- **Zona horaria**: `auth.log` suele ir en UTC; el resto de artefactos puede no.
