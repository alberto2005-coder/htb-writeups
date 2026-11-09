# Infraestructura de phishing: del correo al dominio

[🇬🇧 English](phishing-infrastructure.en.md) | **Español**

Método para identificar la infraestructura detrás de un correo de suplantación sin tocar el servidor del atacante.

## 1. Del correo a la cabecera

```text
From:        <nombre visible> <cuenta@dominio>
Return-Path: <bounce@otro-dominio>
Received:    from <host> (<IP>) by <mx>
Message-ID:  <id@dominio>
Authentication-Results: spf=... dkim=... dmarc=...
```

- `From` es trivialmente falsificable; `Return-Path` y `Received` no.
- Leer `Received` **de abajo arriba**: el primero es el servidor del atacante.
- `Authentication-Results` dice qué falló: SPF, DKIM o DMARC.
- Un `Message-ID` con dominio ajeno al `From` delata el panel usado.

## 2. Del dominio a los registros

```bash
dig +short A <dominio>
dig +short MX <dominio>
dig +short TXT <dominio>
dig +short NS <dominio>
whois <dominio> | grep -E "Creation|Registrar|Name Server"
```

Señales de infraestructura montada para el ataque:

- MX propio (`mail.<dominio>`) en lugar de un proveedor conocido.
- `TXT "v=spf1 a mx ip4:<IP> ~all"` con la IP del propio servidor.
- `TXT "v=DMARC1; p=none;"` → monitorización sin bloqueo.
- Dominio registrado hace días y `NS` del mismo proveedor barato.

## 3. Descubrir variantes

```bash
dnstwist --registered <empresa>.com
dnstwist --geo <empresa>.com
```

Variantes típicas: cambio de TLD, guion (`empresa-seguridad`), doble letra, homoglifos (`rn` por `m`), subdominio engañoso (`empresa.com.login-x.tld`).

## 4. Certificados y reputación

- `crt.sh`: `https://crt.sh/?q=%25.<dominio>` lista subdominios por Certificate Transparency, incluso antes de indexarse.
- VirusTotal y URLScan: primera vez visto, IPs históricas, capturas.
- Shodan/Censys sobre la IP: panel de correo, puerto 25/587/993 abierto, certificado autofirmado.

## 5. Página de aterrizaje

```bash
curl -sI https://<dominio>/
curl -s https://<dominio>/ | grep -E "form|action|password"
```

- Formularios que envían a otro dominio o a un bot de Telegram.
- Clon exacto de un login legítimo (comparar hash del HTML).
- Ofuscación JavaScript que monta el formulario en runtime.

## 6.Respuesta

- Bloquear dominio e IP en el filtro de correo y en el DNS.
- Avisar a los usuarios que recibieron el mensaje.
- Reportar al registrar y al hosting (abuso) con las cabeceras.
- Rotar credenciales de quien haya introducido datos.

## Errores típicos

- Analizar el HTML antes que las cabeceras: el HTML se copia, las cabeceras no.
- Confundir el dominio del `From` con el del enlace.
- Dar por bueno un SPF `pass` cuando el atacante controla el dominio.

MITRE: T1566.002, T1583.001, T1596.002.
