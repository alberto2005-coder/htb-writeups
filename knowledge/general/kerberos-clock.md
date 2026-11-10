---
title: Reloj y Kerberos — el desfase de 5 minutos
tags: [kerberos, windows, active-directory, troubleshooting, lab]
---

# Kerberos y el reloj: `KRB_AP_ERR_SKEW`

[🇬🇧 English](kerberos-clock.en.md) | **Español**

## 1. Por qué importa

Kerberos rechaza cualquier ticket con más de **5 minutos** de desfase respecto al KDC. El error es explícito:

```text
KRB_AP_ERR_SKEW(Clock skew too great)
```

o en herramientas que lo envuelven:

```text
Clock skew too great while getting initial credentials
```

No es un fallo de credenciales: la contraseña, el hash o el certificado pueden ser correctos. Antes de tocar nada más, comprueba la hora.

## 2. Comprobar

```bash
date -u
timedatectl
```

Contra el KDC o cualquier servicio con cabecera `Date`:

```bash
curl -sI https://<host> | grep -i '^date'
```

Diferencia en segundos:

```bash
python3 - <<'PY'
from datetime import datetime, timezone
import email.utils, urllib.request
srv = urllib.request.urlopen('https://<host>').headers['Date']
print((email.utils.parsedate_to_datetime(srv) - datetime.now(timezone.utc)).total_seconds())
PY
```

## 3. Corregir en el laboratorio

Con NTP disponible:

```bash
sudo timedatectl set-ntp true
sudo systemctl restart systemd-timesyncd
```

En HTB la VPN bloquea NTP (UDP/123), así que se ajusta a mano:

```bash
sudo date -s "$(curl -sI https://www.google.com | awk -F': ' '/^[Dd]ate/{print $2}')"
```

Para un solo comando, sin cambiar la hora del sistema:

```bash
faketime '+8 hours' kinit '<user>@<DOMAIN>'
faketime -f '+8h' certipy req -u '<user>@<domain>' -p '<password>' -ca '<CA>' -template '<T>' -dc-ip <DC_IP>
```

## 4. El reloj que se revierte solo

Si `timedatectl` muestra la hora correcta y a los segundos vuelve a estar mal, hay un servicio sincronizando con otra fuente. En una VM de VirtualBox el culpable habitual es **`VBoxService`** (servicio `vboxadd-service`, Guest Additions), que ajusta la hora con el host cada pocos segundos:

```bash
systemctl status vboxadd-service      # LSB: VirtualBox Additions service
ps aux | grep -i VBoxService
sudo systemctl mask vboxadd-service
sudo service vboxadd-service stop
```

`systemd-timesyncd` suele estar `inactive` y no es el problema: comprobarlo y descartarlo evita perder tiempo.

Otras causas: `chronyd`/`ntpd` con un servidor inalcanzable, o el propio hipervisor (VMware Tools) con sincronización activada.

## 5. Síntomas relacionados

- **`KRB_AP_ERR_MODIFIED`** → no es reloj, pero aparece junto a PAC obsoletos; tras cambiar grupos pide ticket nuevo (`kvno`).
- **`Pre-authentication failed`** con contraseña correcta → revisa mayúsculas y el realm, no la hora.
- **Tickets que caducan al instante** → reloj muy adelantado: el ticket nace caducado.
- **`Cannot contact any KDC`** → DNS o puerto 88, no reloj.

## 6. Detección y mitigación (lado defensivo)

- Mantener `w32time`/`chronyd` con fuentes internas y monitorizar el desfase de los DC (`w32tm /monitor`).
- Alertar de `KRB_AP_ERR_SKEW` repetidos: pueden indicar un host comprometido o una VM mal configurada.
- En el laboratorio, dejar constancia del ajuste en las notas para no repetir el diagnóstico.

No es una técnica de ataque; no aplica MITRE.
