---
topic: LocalStack — Lambda y socket Docker
tags: [cloud, localstack, aws, lambda, docker, privesc]
---

# LocalStack — Lambda y socket Docker

[🇬🇧 English](localstack-lambda-rce.en.md) | **Español**

## Concepto

LocalStack simula servicios AWS y a menudo se ejecuta con credenciales y contenedores privilegiados. Si un atacante obtiene credenciales de la API, puede crear una función Lambda con código propio y ejecutarlo en el contenedor; si el socket de Docker está montado, el salto al host es directo.

## Cuándo aplica

- El puerto 4566 o un vhost de LocalStack es accesible.
- Hay credenciales en una aplicación, un buzón o variables de entorno.
- El contenedor monta `/var/run/docker.sock`.

## Procedimiento

1. Configurar `awslocal` con las credenciales encontradas.
2. Empaquetar una Lambda con una reverse shell.
3. Crear e invocar la función.
4. Enumerar el contenedor y el socket.

```bash
awslocal lambda create-function --function-name pwn --runtime python3.9 --handler lambda_function.handler --zip-file fileb://payload.zip --role arn:aws:iam::000000000000:role/lambda-role
awslocal lambda invoke --function-name pwn out.json
```

## Variantes

- `_localstack/init` para inyección de comandos.
- SSRF contra el endpoint de metadatos de LocalStack.
- Contenedor privilegiado con el filesystem del host.

## Limitaciones

- La API puede requerir credenciales válidas.
- Lambda puede estar deshabilitado.
- Sin socket Docker el salto requiere otra vía.

## Mitigación

- No usar credenciales reales en LocalStack.
- Aislar el contenedor y no montar el socket.
- Restringir la API a localhost y autenticarla.

## Detección

- Creación de Lambdas fuera de despliegues.
- Procesos hijos inusuales en el contenedor.
- Acceso al socket Docker desde servicios de aplicación.

## Referencias

- [LocalStack — Lambda](https://docs.localstack.cloud/user-guide/aws/lambda/)
- [0xdf — Stacked](https://0xdf.gitlab.io/2022/03/19/htb-stacked.html)
- [Docker — socket security](https://docs.docker.com/engine/security/)
