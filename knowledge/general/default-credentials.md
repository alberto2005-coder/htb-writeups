---
topic: Credenciales por defecto
tags: [general, credentials, default-password, hydra, iot, enumeration]
---

# Credenciales por defecto

[🌐 English](default-credentials.en.md) | **Español**

## Concepto

Muchos servicios y dispositivos se despliegan con cuentas y contraseñas conocidas que nunca se cambian. Un panel de administración, una base de datos o un dispositivo IoT puede aceptar credenciales de fábrica y dar acceso total.

## Cuándo aplica

- Paneles web de dispositivos (routers, cámaras, NAS, impresoras).
- Servicios como SSH, FTP, SMB, RDP o bases de datos.
- Aplicaciones con cuentas de demostración.
- Contenedores y plantillas sin configuración inicial.

## Procedimiento

1. Identificar el producto y la versión.
2. Buscar credenciales por defecto del fabricante.
3. Probar un número pequeño de combinaciones, respetando el lockout.
4. Verificar el acceso y los privilegios.
5. Documentar la cuenta sin publicar la contraseña.

```bash
curl -s -I http://<IP>/
hydra -L users.txt -P passwords.txt -t 4 ssh://<IP>
```

## Variantes

- `admin:admin`, `root:root` o `pi:raspberry`.
- Contraseña impresa en la etiqueta del dispositivo.
- API con token de demostración.
- Base de datos sin contraseña o con `sa` vacío.

## Limitaciones

- El servicio debe aceptar autenticación remota.
- Los sistemas modernos fuerzan cambio en el primer login.
- El bloqueo por intentos puede interrumpir la prueba.
- Algunos paneles limitan el acceso por IP.

## Mitigación y detección

- Cambiar credenciales antes de exponer el servicio.
- Forzar contraseñas únicas y MFA cuando sea posible.
- Inventariar dispositivos y aplicar configuración base.
- Alertar de logins exitosos desde IP nuevas y de cuentas de fábrica.

## Referencias

- <https://attack.mitre.org/techniques/T1078/001/>
- <https://attack.mitre.org/techniques/T1110/001/>
- <https://www.cisa.gov/known-exploited-vulnerabilities-catalog>
- <https://owasp.org/www-community/vulnerabilities/Use_of_hard-coded_password>
