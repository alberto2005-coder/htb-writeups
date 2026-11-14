---
topic: Kubernetes — escape con cr8escape
tags: [cloud, kubernetes, cri-o, container-escape, cve-2022-0811]
---

# Kubernetes — escape con cr8escape

[🌐 English](kubernetes-cr8escape.en.md) | **Español**

## Concepto

CVE-2022-0811 (cr8escape) permite inyectar valores en `kernel.core_pattern` mediante el campo `sysctls` de un pod. Con CRI-O vulnerable, el patrón se aplica en el host y puede ejecutar un binario cuando un proceso falla.

## Cuándo aplica

- Clúster con CRI-O vulnerable a CVE-2022-0811.
- Permiso para crear pods con `securityContext.sysctls`.
- Nodo con `core_pattern` escribible por el runtime.

## Procedimiento

1. Confirmar el runtime y la versión de Kubernetes/CRI-O.
2. Crear un pod que inyecte `kernel.core_pattern`.
3. Preparar un binario o script en el host.
4. Provocar un core dump para disparar el patrón.
5. Ejecutar comandos en el nodo.

## Comandos

```yaml
securityContext:
  sysctls:
  - name: kernel.core_pattern
    value: "|/tmp/payload"
```

## Variantes

- Inyección mediante `kernel.modprobe`.
- Pods con `privileged: true` y montajes del host.
- Abuso de `hostPath` para escribir el payload.

## Limitaciones

- El clúster debe usar CRI-O vulnerable.
- El pod necesita permisos para definir `sysctls`.
- La explotación requiere un core dump.

## Mitigación

- Actualizar CRI-O y Kubernetes.
- Aplicar Pod Security Standards y restringir `sysctls`.
- Evitar `privileged` y `hostPath`.

## Detección

- Pods con `kernel.core_pattern` o `sysctls` inusuales.
- Core dumps y ejecuciones desde `/tmp` en el nodo.

## Referencias

- <https://kubernetes.io/docs/tasks/administer-cluster/sysctl-cluster/>
- <https://nvd.nist.gov/vuln/detail/CVE-2022-0811>
