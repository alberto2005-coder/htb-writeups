# HTB Writeups — alberto2005coder

[Español](README.md) | **English**

Personal repository of **Hack The Box** writeups, technical notes and methodology. The goal is to document reasoning, evidence and mitigations—not just commands.

> Active machines, challenges and Sherlocks remain unpublished. Only authorized lab content is published, in accordance with HTB rules.

## Contents

<!-- BEGIN AUTO-GENERATED STATS -->
- **Writeups:** 309 (133 machines, 98 challenges and 78 Sherlocks; ES/EN writeups).
- **Knowledge:** 81 topics with ES/EN notes.
<!-- END AUTO-GENERATED STATS -->

| Section | Index |
|---|---|
| Machines | [Catalogue](machines/catalog.en.md) · [Generated index](machines/INDEX.generated.en.md) |
| Challenges | [Curated index](challenges/README.en.md) · [Generated index](challenges/INDEX.generated.en.md) |
| Sherlocks | [Curated index](sherlocks/README.en.md) · [Generated index](sherlocks/INDEX.generated.en.md) |
| Knowledge | [Topic index](knowledge/README.en.md) |
| Templates | [Templates](templates/) |

## Methodology

1. **Reconnaissance and enumeration:** identify the attack surface and exposed services.
2. **Initial access:** document vulnerabilities, hypotheses and evidence.
3. **Lateral movement and privilege escalation:** explain permissions, paths and prerequisites.
4. **Validation:** preserve reproducible evidence and distinguish facts from assumptions.
5. **Mitigation and detection:** explain how to prevent and detect the technique.

## Development and validation

Requirements: Git and Python 3.8 or later. No third-party Python dependencies are required.

```bash
python tools/generate_indexes.py
python tools/repo_check.py
python tools/audit-indices.py
```

Install local Git hooks:

```bash
sh .githooks/install.sh
```

Generated indexes must not be edited manually. Run the generator after adding or removing writeups. CI checks that generated files are up to date.

## Responsible use

All content relates to authorized lab environments. Do not publish credentials, private keys, real flags or sensitive evidence. Active machine writeups remain private until HTB retires them.

## Licensing

Original source code and scripts are licensed under MIT (see [LICENSE](LICENSE)). Original documentation is licensed under [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/) (see [LICENSE-DOCS](LICENSE-DOCS)). Third-party materials retain their own licenses and attributions.

## Profile

- Hack The Box: [alberto2005coder](https://app.hackthebox.com/users/4187928)
- Study areas: web pentesting, Linux, Active Directory and cloud.
