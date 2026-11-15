---
topic: Docker Registry — enumeration and layer extraction
tags: [linux, docker, registry, image, secrets]
---

# Docker Registry — enumeration and layer extraction

**English** | [🌐 Español](docker-registry-enumeration.md)

## Concept

A private Docker registry with weak credentials allows listing repositories, downloading manifests and extracting layers. Images often contain SSH keys, passwords and deployment configuration.

## When it applies

- The registry answers on `/v2/`.
- Credentials are weak or default.
- The manifest and blobs can be downloaded.

## Procedure

1. List `/v2/_catalog`.
2. List tags and download the manifest.
3. Extract layers and search for secrets.
4. Use the recovered credentials.

## Commands

```bash
curl -k --user <USER>:<PASS> https://registry/v2/_catalog
curl -k --user <USER>:<PASS> https://registry/v2/<REPO>/tags/list
curl -k --user <USER>:<PASS> https://registry/v2/<REPO>/manifests/latest
```

## Variants

- `docker pull` with `--tls-verify=false`.
- Blobs cached in `/var/lib/registry`.
- Basic auth at the proxy.

## Limitations

- The catalog may be disabled.
- Layers may be encrypted or signed.
- Credentials may be read-only.

## Mitigation

- Strong authentication and verified TLS.
- Keep secrets out of images.
- Restrict the catalog and audit pulls.

## Detection

- Requests to `/v2/_catalog` from unusual hosts.
- Bulk blob downloads.
- Registry credentials used outside CI.

## References

- [0xdf — Registry](https://0xdf.gitlab.io/2020/04/04/htb-registry.html)
- [Docker — Registry API](https://distribution.github.io/distribution/spec/api/)
- [Docker — security](https://docs.docker.com/engine/security/)
