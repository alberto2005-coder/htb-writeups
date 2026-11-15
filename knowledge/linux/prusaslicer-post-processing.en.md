---
topic: PrusaSlicer — post-processing scripts as root
tags: [linux, prusaslicer, 3mf, cve-2023-47268, privesc]
---

# PrusaSlicer — post-processing scripts as root

**English** | [🌐 Español](prusaslicer-post-processing.md)

## Concept

A `.3mf` file can embed a post-processing script. If PrusaSlicer runs as root and processes the model, the script executes with those privileges. CVE-2023-47268 describes this arbitrary execution.

## When it applies

- The user can run PrusaSlicer as root.
- A `.3mf` can be supplied or modified.
- Expert mode allows post-processing scripts.

## Procedure

1. Copy the `.3mf` and open it in expert mode.
2. Add a script that copies `/bin/bash` and sets SUID.
3. Run PrusaSlicer as root with `-s`.
4. Launch the SUID shell.

## Commands

```bash
cp /bin/bash /tmp/rootbash; chmod 6777 /tmp/rootbash
prusaslicer -s malicious.3mf
/tmp/rootbash -p
```

## Variants

- Script in `print_host` or `post_processing`.
- Add the script to an existing profile.
- Chain with a shared project file.

## Limitations

- The `.3mf` must be accepted by the version.
- Root execution is required to escalate.
- The script may need an absolute path.

## Mitigation

- Never run PrusaSlicer as root.
- Disable post-processing scripts.
- Treat `.3mf` files as untrusted.

## Detection

- PrusaSlicer running as root.
- SUID shells created after slicing.
- `.3mf` scripts with suspicious paths.

## References

- [NVD — CVE-2023-47268](https://nvd.nist.gov/vuln/detail/CVE-2023-47268)
- [0xdf — Trickster](https://0xdf.gitlab.io/2025/02/01/htb-trickster.html)
- [PrusaSlicer — post-processing](https://help.prusa3d.com/article/post-processing-scripts_283913)
