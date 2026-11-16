---
topic: Bash — unquoted comparison and glob leak
tags: [linux, bash, glob, wildcard, secret-leak, privesc]
---

# Bash — unquoted comparison and glob leak

**English** | [🌐 Español](bash-unquoted-glob-leak.md)

## Concept

In `[[ $secret == $input ]]`, if `$input` is unquoted, Bash treats it as a pattern. A trailing `*` checks prefixes and leaks a secret character by character without reading it directly.

## When it applies

- A privileged script compares a secret with controlled input.
- The input variable is unquoted.
- The script returns a different message based on the match.

## Procedure

1. Locate the comparison and success message.
2. Try a known prefix plus `*`.
3. Iterate over the alphabet and keep the character that changes the response.
4. Repeat until the secret is rebuilt.

## Commands

```bash
# input file with the prefix and a wildcard
printf '%s*' "$PREFIX" > /dev/shm/file
sudo /opt/check.sh /dev/shm/file
# repeat per character and check the success message
```

## Variants

- `?` patterns for one character.
- `[a-z]` classes.
- Comparisons with `=`, `==` or `!=`.

## Limitations

- The variable may be quoted.
- The script may not reveal the result.
- Modern Bash keeps globbing inside `[[ ]]`.

## Mitigation

- Always quote variables in comparisons.
- Use `case` or literal comparisons.
- Do not compare secrets in accessible scripts.

## Detection

- Repeated script calls with input files.
- `*` or `?` in arguments.
- Reads of the CA or keys from `/dev/shm`.

## References

- [0xdf — Resource](https://0xdf.gitlab.io/2024/11/23/htb-resource.html)
- [Bash — pattern matching](https://www.gnu.org/software/bash/manual/html_node/Pattern-Matching.html)
- [CWE-697 — Incorrect Comparison](https://cwe.mitre.org/data/definitions/697.html)
