---
sherlock: Cookie Consumption
category: SOC
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [soc, kubernetes, secrets, service-account, cloud]
---

# Cookie Consumption — Hack The Box (Sherlock)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha metodológica; sin respuestas literales ni datos reales.

## Escenario

El scheduler de galletas de Santa corre en Kubernetes. Se exporta un namespace y se sospecha que un atacante creó recursos, leyó secretos o alteró el cronjob. Hay que reconstruir la actividad.

## Evidencias

- Exportación YAML/JSON del namespace.
- Manifiestos de pods, deployments, service accounts, secrets y cronjobs.
- No se entrega el clúster en vivo.

```bash
kubectl get all,secrets,serviceaccounts -n <NAMESPACE> -o yaml
```

## Investigación

### 1. Inventario y triaje

Se listan los objetos y se buscan nombres y fechas anómalas. Los `serviceaccounts` con permisos amplios y los `secrets` montados son los objetivos probables.

```bash
yq '.items[] | [.kind,.metadata.name,.metadata.creationTimestamp]' dump.yaml
```

### 2. Línea temporal

Se ordenan por `creationTimestamp` y se comparan con el despliegue legítimo. Un pod nuevo que monta el token de otro servicio o un cronjob que ejecuta una imagen externa destaca.

### 3. Artefacto clave

El `serviceaccount` y su `RoleBinding` muestran el alcance. El `secret` indica qué credenciales quedaron expuestas; el `cronjob` revela persistencia.

```bash
yq '.items[] | select(.kind=="CronJob") | .spec.jobTemplate.spec.template.spec.containers[].image' dump.yaml
```

## Conclusiones

- El atacante creó o modificó recursos dentro del namespace.
- Un token de servicio permitió leer secretos.
- El cronjob o pod malicioso dio persistencia.
- La rotación de credenciales es obligatoria.

## Lecciones

- Kubernetes requiere revisar RBAC y tokens montados.
- Un dump estático basta para reconstruir objetos.
- Los secretos de aplicación no deben estar en variables de entorno.

## Referencias

- <https://www.hackthebox.com/sherlocks/Cookie%20Consumption>
- <https://kubernetes.io/docs/concepts/security/service-accounts/>
- <https://attack.mitre.org/techniques/T1552/007/>
