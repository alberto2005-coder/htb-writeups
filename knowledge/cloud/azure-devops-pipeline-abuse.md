---
topic: Abuso de pipelines en Azure DevOps
tags: [cloud, azure-devops, cicd, pipeline, service-connection, privesc]
---

# Abuso de pipelines en Azure DevOps

[🌐 English](azure-devops-pipeline-abuse.en.md) | **Español**

## Concepto

Un pipeline de Azure DevOps ejecuta código definido en el repositorio con las credenciales de un agente y, a menudo, con acceso a service connections. Si un atacante puede modificar el YAML o una tarea, puede ejecutar comandos en el agente, leer secretos y desplegar en producción.

## Cuándo aplica

- Repositorios con pipelines editables por el usuario comprometido.
- Agentes autoalojados que ejecutan como cuentas privilegiadas.
- Variables de pipeline con secretos.
- Service connections con permisos amplios.

## Procedimiento

1. Enumerar repositorios y archivos `azure-pipelines.yml`.
2. Revisar variables, tareas y agentes.
3. Identificar una rama o PR que dispare el pipeline.
4. Añadir un paso que lea el entorno o las credenciales.
5. Ejecutar y revisar los logs/artefactos.

```yaml
- script: |
    whoami
    env | sort
  displayName: diagnostics
```

## Variantes

- Modificación del YAML en una rama propia.
- Script inline en una tarea existente.
- Abuso de una service connection para desplegar.
- Agente autoalojado con acceso al host.
- Artefacto envenenado consumido por otro pipeline.

## Limitaciones

- Se necesita permiso para editar el pipeline o la rama.
- Las aprobaciones y entornos protegen los despliegues.
- Los secretos pueden estar enmascarados en logs.
- Los agentes efímeros reducen la persistencia.

## Mitigación y detección

- Separar pipelines de PR y de producción con aprobaciones.
- Usar agentes efímeros y cuentas de mínimo privilegio.
- Restringir service connections y variables secretas.
- Auditar cambios de YAML, ejecuciones manuales y despliegues fuera de horario.

## Referencias

- <https://learn.microsoft.com/en-us/azure/devops/pipelines/security/overview>
- <https://attack.mitre.org/techniques/T1195/>
- <https://attack.mitre.org/techniques/T1078/004/>
- <https://owasp.org/www-project-top-ten/2017/A8_2017-Insecure_Deserialization>
