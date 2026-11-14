---
topic: SRUM y bases ESE en Windows
tags: [forensics, windows, srum, ese, network, edb]
---

# SRUM and ESE Databases on Windows

**English** | [🇪🇸 Español](srum-ese.md)

## Concept

System Resource Usage Monitor (SRUM) records CPU, network and application usage per process in `SRUDB.dat`. It is an ESE database; `SrumECmd` processes it and helps estimate which process sent data and when.

## When it applies

- Firewall or proxy logs are missing.
- The process responsible for outbound traffic is unknown.
- A time window of execution is needed.

## Procedure

1. Copy `SRUDB.dat` and the associated registry.
2. Process with `SrumECmd`.
3. Filter by process and bytes sent/received.
4. Cross-check with prefetch and MFT.
5. Estimate volume and window.

```bash
SrumECmd.exe -f SRUDB.dat --csv srum
```

## Variants

- `Windows.edb` for searches and indexes.
- `SRUDB.dat` from servers and workstations.
- Correlation with event 5156.

## Limitations

- SRUM stores no content or destinations.
- The database may be locked; use a copy.
- Counters are cumulative and may round.

## Mitigation

- Centralise network logs.
- Protect and retain ESE databases.
- Monitor processes with anomalous traffic.

## Detection

- Byte spikes per process.
- User processes with high traffic.
- Correlation with C2 connections.

## References

- <https://github.com/EricZimmerman/Srum>
- <https://attack.mitre.org/techniques/T1053/005/>
- <https://www.hackthebox.com/sherlocks>
