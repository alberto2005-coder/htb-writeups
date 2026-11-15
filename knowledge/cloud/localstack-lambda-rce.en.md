---
topic: LocalStack — Lambda and Docker socket
tags: [cloud, localstack, aws, lambda, docker, privesc]
---

# LocalStack — Lambda and Docker socket

[🇪🇸 Español](localstack-lambda-rce.md) | **English**

## Concept

LocalStack emulates AWS services and often runs with credentials and privileged containers. If an attacker obtains API credentials, they can create a Lambda with their own code and run it in the container; if the Docker socket is mounted, the jump to the host is direct.

## When it applies

- Port 4566 or a LocalStack vhost is reachable.
- Credentials exist in an application, mailbox or environment variables.
- The container mounts `/var/run/docker.sock`.

## Procedure

1. Configure `awslocal` with the found credentials.
2. Package a Lambda with a reverse shell.
3. Create and invoke the function.
4. Enumerate the container and the socket.

```bash
awslocal lambda create-function --function-name pwn --runtime python3.9 --handler lambda_function.handler --zip-file fileb://payload.zip --role arn:aws:iam::000000000000:role/lambda-role
awslocal lambda invoke --function-name pwn out.json
```

## Variants

- `_localstack/init` for command injection.
- SSRF against the LocalStack metadata endpoint.
- Privileged container with the host filesystem.

## Limitations

- The API may require valid credentials.
- Lambda may be disabled.
- Without the Docker socket the jump needs another path.

## Mitigation

- Do not use real credentials in LocalStack.
- Isolate the container and do not mount the socket.
- Restrict the API to localhost and authenticate it.

## Detection

- Lambda creation outside deployments.
- Unusual child processes in the container.
- Docker socket access from application services.

## References

- [LocalStack — Lambda](https://docs.localstack.cloud/user-guide/aws/lambda/)
- [0xdf — Stacked](https://0xdf.gitlab.io/2022/03/19/htb-stacked.html)
- [Docker — socket security](https://docs.docker.com/engine/security/)
