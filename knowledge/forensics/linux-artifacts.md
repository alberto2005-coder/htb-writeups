---
topic: Linux forensic artifacts
tags: [forensics, linux, auth-log, bash-history, cron, git, incident-response]
---

# Linux forensic artifacts

[🌐 English](linux-artifacts.en.md) | **Español**

## Concepto

En Linux, el acceso y la actividad quedan en `auth.log`, `syslog`, logs del servicio web, `.bash_history`, cron y el historial de Git. La correlación de hora, usuario, IP y comando permite reconstruir una intrusión sin depender de un único archivo.

## Cuándo aplica

- Servidor Linux con actividad sospechosa.
- Repositorio Git con cambios no explicados.
- Acceso SSH y escalada de privilegios.
- Persistencia mediante cron o servicios.

## Procedimiento

1. Fijar la zona horaria y hashear la evidencia.
2. Revisar accesos SSH, `sudo` y creación de usuarios.
3. Leer `.bash_history` y logs del servicio web.
4. Inspeccionar cron, systemd y procesos.
5. Revisar Git: `log`, `reflog`, `diff` y ramas.

```bash
grep -Ei 'accepted|failed|new user|sudo' auth.log
cat /home/<USER>/.bash_history
crontab -l; ls -la /etc/cron.*
git log --all --oneline --decorate
git reflog --date=iso
```

## Variantes

- Historial borrado o enlazado a `/dev/null`.
- Comandos ejecutados sin shell interactiva.
- Cambios en un repositorio con `git commit --amend`.
- Persistencia en `systemd`, cron o `.profile`.

## Limitaciones

- El historial puede estar deshabilitado o manipulado.
- Los logs rotan y pueden faltar.
- Un atacante con root puede alterar timestamps.
- Git no registra cambios no confirmados.

## Mitigación y detección

- Centralizar logs y proteger su integridad.
- Auditar `sudo`, SSH y creación de usuarios.
- Monitorizar cron, systemd y cambios en repositorios.
- Alertar de historiales vacíos, IPs nuevas y commits fuera de horario.

## Referencias

- <https://attack.mitre.org/techniques/T1070/003/>
- <https://git-scm.com/docs/git-reflog>
- <https://www.sans.org/white-papers/linux-forensics/>
