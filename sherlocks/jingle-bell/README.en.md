---
sherlock: Jingle Bell
domain: DFIR / Windows
difficulty: Easy
platform: Hack The Box
evidence: Windows notification database from a workstation
tools: [DB Browser for SQLite, strings, SQLite]
---

# Jingle Bell — Hack The Box

**English** | [🇪🇸 Español](README.md)

> Defensive investigation. No platform answers copied.

## Scenario

Torrin is suspected of leaking Forela data and installing unauthorised software. The forensic team found nothing in the usual artifacts, so the evidence left is the host's **notification database**.

## Evidence

- A profile copy: `AppData\Local\Microsoft\Windows\Notifications\` (the `WPNDatabase.db` file plus its companions).

## Method

1. **Open it with SQLite**: it is a plain SQLite database.

```bash
sqlite3 WPNDatabase.db '.tables'
sqlite3 WPNDatabase.db '.schema Notification'
```

2. **Read the `Notification` table**: each row is a toast with its source app, payload and time. That is where the conversation survives.

```sql
SELECT Id, HandlerId, Payload, ArrivalTime FROM Notification;
```

3. **Parse the payload**: the inner XML carries sender, text and sometimes attachments. Two parties emerge: the Forela user and an external contact.

4. **Unauthorised software**: `HandlerId`/`Handler` shows which app produced each notification; a messaging or file-transfer app that is not corporate answers what he used to leak.

5. **Timeline**: sort by `ArrivalTime` and line up the exchange (who offers, who accepts, how much is paid).

## What it teaches

- Windows notifications store **message content** the user already saw: evidence of communications.
- A messaging app leaves traces even after uninstalling: the notification DB stays in the profile.
- `HandlerId` identifies the application without running it.

## Pitfalls

- **Locked database**: copy `WPNDatabase.db` together with its `-wal`/`-shm` files to keep recent rows.
- **XML payload**: text is escaped; format it before reading.
- **Multiple accounts**: filter by the investigated user's SID.
