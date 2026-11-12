---
sherlock: Kuber
domain: DFIR
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [dfir, kubernetes, yaml, secrets, container]
---

# Kuber — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de investigación; sin respuestas literales de la plataforma.

## Escenario

Se entrega un volcado de recursos de un clúster Kubernetes. Hay que identificar cómo estaba expuesto un servicio SSH, qué secretos quedaban legibles y qué pod ejecutaba una reverse shell. El caso enseña a leer manifiestos YAML como evidencia: Service, ConfigMap, Secret y Pod cuentan la historia sin necesidad de logs del API server.

## Evidencias

- `evidence/kube-system/*.yaml`, un fichero por tipo de recurso.
- `service.yaml`, `configmaps.yaml`, `secrets.yaml`, `pods.yaml`.
- Manifiestos de deployment, daemonset, job, serviceaccount y namespace.
- Valores de `Secret` codificados en base64 (no cifrados).

```bash
sha256sum evidence/kube-system/*.yaml
grep -R "kind:" evidence/kube-system | sort | uniq -c
```

## Investigación

### 1. Inventario y triaje

Se identifica el espacio de nombres y los objetos que no pertenecen a la línea base. `kube-system` debería contener componentes del plano de control, no cargas de trabajo arbitrarias.

```bash
grep -nE "^(kind|  name|  namespace):" evidence/kube-system/*.yaml
```

### 2. Línea temporal

Los manifiestos no siempre conservan timestamps. La secuencia se reconstruye por referencias: qué Service selecciona qué Pod, qué ConfigMap/Secret consume y qué imagen aparece en el Pod. Si el volcado incluye `metadata.creationTimestamp`, se usa como fuente principal; si no, se documenta la limitación.

### 3. Artefacto clave

El Service revela el `nodePort` que expone SSH al exterior. El ConfigMap `ssh-config` contiene valores en claro; el Secret `ssh-secret` contiene `USER_PASSWORD` en base64. El Pod malicioso imita el nombre de `metrics-server`, usa la imagen `alpine` y ejecuta `nc` contra una IP externa.

```bash
grep -n -B8 -A8 "nodePort" evidence/kube-system/service.yaml
grep -n -A12 "name: ssh-config" evidence/kube-system/configmaps.yaml
grep -n "USER_PASSWORD" evidence/kube-system/secrets.yaml
grep -n -E "name:|image:|nc " evidence/kube-system/pods.yaml
```

Base64 es codificación, no cifrado:

```bash
echo '<BASE64_VALUE>' | base64 -d
```

El nombre del Pod imita al componente legítimo, pero su `command` no tiene relación con las métricas. Esa discrepancia entre nombre y comportamiento es la evidencia de enmascaramiento.

## Conclusiones

- El servicio SSH estaba publicado fuera del clúster mediante un NodePort.
- Las credenciales estaban en un ConfigMap y en un Secret solo codificado en base64.
- El atacante creó un Pod en `kube-system` con una imagen mínima y una reverse shell.
- El Pod se llamó como `metrics-server` para pasar desapercibido.

## Lecciones

- No exponer SSH con un NodePort; usar bastión, VPN o `kubectl port-forward`.
- Los ConfigMaps no son un almacén de secretos; los Secrets necesitan RBAC, cifrado en reposo y un gestor externo.
- Alertar de Pods nuevos en `kube-system` que no pertenecen a un controlador conocido.
- Una política de admisión que restrinja imágenes y comandos habría bloqueado el Pod.
