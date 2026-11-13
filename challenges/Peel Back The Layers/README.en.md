---
challenge: Peel Back The Layers
type: Forensics
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [forensics, docker, image-layers, shared-library, elf]
---

# Peel Back The Layers — Hack The Box (Challenge)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference writeup; no real flag.

## TL;DR

A public Docker image was modified to include a malicious shared library and then deleted in a later layer. The layer history preserves the file and `LD_PRELOAD` explains its execution. The flag is embedded in the library.

## Prompt and surface

- Forensics, Medium, retired.
- The image is `steammaintainer/gearrepairimage`.
- Recover the inserted and deleted backdoor.

```bash
docker pull steammaintainer/gearrepairimage:latest
docker image save steammaintainer/gearrepairimage -o image.tar
```

## Reconnaissance

- `image.tar` contains `manifest.json`, `repositories` and layers.
- Only some layers have content; the rest are metadata.
- The history shows `rm -rf /usr/share/lib/` in a later layer.

```bash
7z l image.tar
cat manifest.json
```

## Analysis

1. Find the layer that copies files into `/usr/share/lib`.
2. Extract its `layer.tar`.
3. Inspect `.wh..wh..opq`, which marks an opaque directory.
4. Extract `librs.so`.
5. Analyse the library with `file`, `strings` and Ghidra.

```bash
7z l <LAYER>/layer.tar
tar xvf <LAYER>/layer.tar
file usr/share/lib/librs.so
```

## Root cause

The attacker abused a public image's history to distribute a backdoor and then tried to hide it by deleting the directory. Docker keeps old layers: deleting a file in a new layer does not remove it from earlier ones.

`LD_PRELOAD` pointed to `librs.so`, so the dynamic loader ran the library before the others.

## Local reproduction

- Load the image or TAR in an isolated environment.
- Inspect history with `docker history --no-trunc`.
- Extract layers and compare paths.
- Analyse `librs.so` without executing it.

```bash
docker history --no-trunc steammaintainer/gearrepairimage:latest
strings -a usr/share/lib/librs.so | grep -Ei 'HTB|http|connect|LD_PRELOAD'
```

## Evidence

- Layers and sizes.
- Path `usr/share/lib/librs.so`.
- Constants or strings forming the flag, redacted.
- `LD_PRELOAD` configuration.

## Lessons learned

- Docker layers are immutable and cumulative.
- Deleting in a later layer does not remove earlier content.
- A shared library can run in every process inheriting `LD_PRELOAD`.

## Mitigations and detection

- Sign images and verify provenance.
- Scan every layer, not just the final filesystem.
- Restrict `LD_PRELOAD` and environment variables in containers.
- Audit public images before deployment.

## References

- <https://www.hackthebox.com/challenges/Peel%20Back%20The%20Layers>
- <https://docs.docker.com/build/cache/>
- <https://attack.mitre.org/techniques/T1543/006/>
