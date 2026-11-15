---
topic: Docker — secrets in image layers
tags: [linux, docker, layers, secrets, forensics]
---

# Docker — secrets in image layers

**English** | [🌐 Español](docker-layer-secret-recovery.md)

## Concept

A Docker image is a stack of immutable layers. Deleting a file in a later layer does not remove it from earlier ones, and `docker save` preserves the full history. A backup or accessible registry allows extracting `.env`, keys and source code thought to be deleted.

## When it applies

- There is access to a backup, registry or application image.
- Code ships in layers and secrets are deleted in later steps.
- Configuration, credentials or source code are needed.

## Procedure

1. Obtain the image or backup and run `docker save`.
2. Extract the tar and inspect `manifest.json` and layers.
3. Search for `.env`, keys, history and deleted files.
4. Reuse the secrets in the application or over SSH.

## Commands

```bash
docker save <IMAGE> -o image.tar
mkdir image && tar -xf image.tar -C image
find image -name ".env" -o -name "*.pem" -o -name "*.key"
docker history --no-trunc <IMAGE>
```

## Variants

- Inspect layers with `dive`.
- Search `layer.tar` files with `tar -tvf`.
- Recover environment variables from `config.json`.

## Limitations

- The image may use multi-stage builds and omit build layers.
- Secrets may be in a volume, not the image.
- The registry may require authentication.

## Mitigation

- Use multi-stage builds and `.dockerignore`.
- Do not copy secrets into the image; use runtime secrets.
- Scan images and restrict registry access.

## Detection

- Images with `.env` or keys in layers.
- Anomalous registry or backup access.
- Sensitive environment variables in `config.json`.

## References

- [0xdf — Bolt](https://0xdf.gitlab.io/2022/02/19/htb-bolt.html)
- [Docker — Image layers](https://docs.docker.com/storage/storagedriver/)
- [CWE-312 — Cleartext Storage of Sensitive Information](https://cwe.mitre.org/data/definitions/312.html)
