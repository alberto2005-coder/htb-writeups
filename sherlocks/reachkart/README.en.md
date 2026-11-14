---
sherlock: ReachKart
category: DFIR
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [dfir, pcap, access-log, path-traversal, jwt, websocket, blockchain, hardhat]
---

# ReachKart — Hack The Box (Sherlock)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Methodology writeup; no literal answers or real data.

## Scenario

ReachKart is a storefront whose development environment mirrors production. Sellers report missing Ether from their wallets. The web access log and a network capture from the development server are provided to reconstruct the intrusion and the theft.

## Evidence

- Web server `access.log`.
- `network-traffic.pcap` with HTTP, WebSocket and Hardhat JSON-RPC.
- Time note: the capture has a +11-hour offset; the log is UTC.

```bash
sha256sum access.log network-traffic.pcap
head -n 5 access.log
capinfos network-traffic.pcap
```

## Investigation

### 1. Inventory and triage

Compare log and capture times before answering any temporal question. The log shows requests to `/user/getOrderBill` with `../` chains, pointing to path traversal.

```bash
grep -F 'template=../' access.log | awk '{print $7}' | sort | uniq -c | sort -rn
```

The first exploitation with a `200` response reads `/etc/passwd`; earlier attempts fail.

### 2. Discovery and credentials

The capture keeps the `package.json` response, revealing Express and the Hardhat version. It also contains the server source, including `rk-logging.js`, where the JWT signing key sits.

```bash
tshark -r network-traffic.pcap -q -z follow,tcp,ascii,53 | grep -i secret
```

With `<JWT_SECRET>`, a token with `account_type: admin` is signed. The token is presented on `GET /admin`; the server accepts it.

### 3. Execution and exfiltration

The admin panel includes a WebSocket terminal on port 8888. The attacker runs commands, starts `python3 -m http.server 6969`, serves `reachkart.db` and downloads it with `wget`.

```bash
tshark -r network-traffic.pcap -Y websocket -T fields -e tcp.dstport -e websocket.payload.text
tshark -r network-traffic.pcap -Y 'tcp.port==6969 && http.request' -T fields -e frame.time -e http.request.uri
```

The SQLite database contains sellers and wallets. Count users with the `seller` role.

### 4. Blockchain impact

Hardhat listens on 8545 without authentication. The capture shows `eth_sendRawTransaction` calls from seller wallets to a single address. Sum the `value` fields and exclude the gas-funding transaction.

```bash
tshark -r network-traffic.pcap -Y 'tcp.port==8545 && json' -T json > rpc.json
grep -n 'eth_sendRawTransaction' rpc.json | head
```

## Conclusions

- Initial access was path traversal in `/user/getOrderBill`.
- Source disclosure exposed the JWT key and allowed forging an admin token.
- The WebSocket terminal provided execution and served the database.
- The development Hardhat node held real wallets and enabled the drain.
- The capture's time offset is a critical error source.

## Lessons

- A development environment with real data is production.
- Secrets must not live in source or in files reachable by traversal.
- An admin panel with a terminal and an unauthenticated blockchain node multiply impact.
- Normalize time zones before correlating sources.

## References

- <https://www.hackthebox.com/sherlocks/ReachKart>
- <https://owasp.org/www-community/attacks/Path_Traversal>
- <https://attack.mitre.org/techniques/T1606/001/>
- <https://hardhat.org/hardhat-network/docs/overview>
