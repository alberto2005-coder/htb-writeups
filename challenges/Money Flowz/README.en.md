---
challenge: Money Flowz
type: OSINT
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [osint, reddit, ethereum, ropsten, blockchain, transaction]
---

# Money Flowz — Hack The Box (Challenge)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference writeup; no real flag.

## TL;DR

The description gives a name, "Frank Vitalik". Searching social media leads to a Reddit profile and a scam with an Ethereum wallet on the Ropsten testnet. The flag is in the `input data` of an outgoing transaction.

## Prompt and surface

- OSINT, Medium, retired.
- Only a description and a name.
- No files or instance.

```text
Frank Vitalik is a hustler, can you figure out where the money flows?
```

## Reconnaissance

Search name variants and public profiles:

```text
"Frank Vitalik" reddit
"Frank Vitalik" ethereum
"Frank Vitalik" free coinz
```

A Reddit post and a Steemit article promoting "free coinz" share a wallet address.

## Analysis

1. Identify the address and network (Ropsten, an Ethereum testnet).
2. Query the block explorer and filter outgoing (`OUT`) transactions.
3. Review each output's details and the `Input Data` field.
4. Switch the view from hex to UTF-8.
5. The text contains the flag, which is redacted.

```text
# Ropsten is deprecated; use the web archive or a historical explorer
https://ropsten.etherscan.io/address/<address>
```

## Root cause

The information is deliberately published on social media and the blockchain. Pseudonymity does not prevent correlating identity, wallet and transactions.

## Local reproduction

1. Repeat the name searches.
2. Document the Reddit → Steemit → wallet pivot.
3. Query outgoing transactions.
4. Decode the input as UTF-8.
5. Keep screenshots with the flag redacted.

## Evidence

- Screenshots of profiles and the post.
- Address and transaction (redacted).
- Input decoding.
- Redacted flag.

## Lessons learned

- A name and a social network are enough to start a pivot.
- The blockchain is a permanent public record.
- `input data` can carry messages.
- Testnets disappear; archive evidence.

## Mitigation and detection

- Do not publish addresses linked to real identity.
- Avoid messages in transactions.
- Use separate wallets per context.
- Train on digital footprint and OSINT.

## References

- <https://7rocky.github.io/en/ctf/htb-challenges/osint/money-flowz/>
- <https://ethereum.org/>
- <https://en.wikipedia.org/wiki/Open-source_intelligence>
