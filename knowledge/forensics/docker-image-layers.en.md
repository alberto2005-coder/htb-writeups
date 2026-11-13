---
topic: Docker image layers
tags: [forensics, docker, containers, layers, supply-chain]
---

# Docker image layers

**English** | [🇪🇸 Español](docker-image-layers.md)

## Concept

A Docker image is a stack of immutable layers. Each Dockerfile instruction adds a layer, and `docker image save` preserves all of them in a TAR with `manifest.json`, `repositories` and one `layer.tar` per layer. Deleting a file in a later layer does not remove it from earlier ones.

## When it applies

- Investigating public images or a compromised registry.
- Looking for secrets deleted in a later layer.
- Analysing an image before deployment.
- Challenges with an image TAR or suspicious history.

## Requirements and conditions

- A local image or exported TAR.
- Tools to list and extract TAR archives.
- An isolated environment; do not run unknown binaries.
- Knowledge of `.wh.` and `.wh..wh..opq`.

## Procedure

1. Export the image with `docker image save`.
2. List the TAR and manifest.
3. Review `docker history --no-trunc`.
4. Extract each `layer.tar` and compare paths.
5. Analyse deleted or opaque files.
6. Verify hashes and strings before opening binaries.

```bash
docker image save <IMAGE> -o image.tar
7z l image.tar
docker history --no-trunc <IMAGE>
tar xvf <LAYER>/layer.tar
```

## Variants

- Multi-stage images with discarded layers.
- Registries retaining old manifests.
- Base layers with unexpected secrets or binaries.
- Images signed and verified with Cosign.

## Limitations

- The final layer does not show what was deleted.
- `.wh.` files do not contain the deleted content.
- Public image provenance does not guarantee safety.
- Binary analysis requires a controlled environment.

## Mitigation

- Sign and verify images.
- Scan every layer, not only the final result.
- Never include secrets in any layer.
- Use minimal, reproducible bases.
- Review history before deployment.

## Detection

- Alert on images whose layers delete sensitive directories.
- Compare history with the expected Dockerfile.
- Look for `LD_PRELOAD`, binaries in `/usr/share` and opaque files.
- Monitor pulls of unsigned images.

## References

- <https://docs.docker.com/build/cache/>
- <https://docs.docker.com/reference/cli/docker/image/save/>
- <https://attack.mitre.org/techniques/T1543/006/>
