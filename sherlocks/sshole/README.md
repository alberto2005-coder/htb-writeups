---
sherlock: SSHole
domain: DFIR / Unix
difficulty: Very Easy
platform: Hack The Box
evidence: Evidencias de un jumpbox Linux comprometido
tools: [grep, journalctl, auth.log, tcpdump]
---

# SSHole — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> Investigación defensiva. Sin respuestas literales de la plataforma.

## Escenario

Un *jumpbox* mal configurado empieza a generar tráfico hacia un dominio sospechoso. Se entrega la evidencia recogida del propio servidor: hay que averiguar **cómo entraron** y **qué hicieron después**.

## Evidencia

- Archivos del jumpbox (logs de autenticación, historial, configuraciones) empaquetados en un ZIP con la contraseña habitual de los Sherlocks.

## Método

1. **¿Cómo entraron?** El servicio SSH de la caja es antiguo y vulnerable: se revisa la versión y los intentos de conexión anómalos.

```bash
grep -i 'sshd' auth.log | less
grep -c 'Failed password' auth.log
```

Un acceso exitoso sin fase de autenticación previa (ni *password* ni *publickey*) apunta a un **bypass** del servidor SSH, no a fuerza bruta.

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

4. **Reconocimiento interno**: el jumpbox se usa para escanear la red detrás; en los logs y en el tráfico se ven barridos de puertos hacia rangos internos.

5. **Persistencia**: revisar `~/.ssh/authorized_keys`, `cron` y unidades de systemd añadidas.

## Qué enseña

- Un servidor SSH vulnerable se compromete **sin credenciales**: el patrón de log es distinto al de una fuerza bruta.
- Un jumpbox es una plataforma de pivote: el valor forense está en el tráfico *saliente* posterior.
- Comparar `auth.log` con `last` y el historial reconstruye la sesión.

## Tropiezos

- **Ruido de escaneos**: filtrar por IP y por ventana temporal antes de sacar conclusiones.
- **Logs rotados**: si falta el rango, mirar `.1` y `journalctl`.
- **Zona horaria**: `auth.log` suele ir en UTC; el resto de artefactos puede no.
