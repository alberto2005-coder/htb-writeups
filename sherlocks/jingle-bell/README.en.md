---
sherlock: Jingle Bell
domain: DFIR / Windows
difficulty: Easy
platform: Hack The Box
evidence: Windows notification database from a workstation
tools: [DB Browser for SQLite, strings, SQLite]
state: Retired
tags: [dfir, windows, notifications, wpndatabase, slack, insider-threat]
---

# Jingle Bell — Hack The Box

**English** | [🇪🇸 Español](README.md)

> Defensive investigation. No platform answers copied.

## Scenario

Torrin is suspected of leaking Forela data and installing unauthorised software. The forensic team found nothing in the usual artifacts, so the evidence left is the host's **notification database**.

## Evidence

- `Torrincase/C/Users/<user>/AppData/Local/Microsoft/Windows/Notifications/wpndatabase.db` plus its `-wal` and `-shm` companions.

## Investigation

1. **Open it**: it is a plain SQLite database; copy the three files together so the WAL is merged.

```bash
sqlite3 wpndatabase.db '.tables'
sqlite3 wpndatabase.db '.schema Notification'
```

2. **The `Notification` table**: each row is a toast with `Payload` (the XML that was displayed), `ArrivalTime` (a Windows FILETIME) and `HandlerId`, which points at `NotificationHandler` to say which app produced it.

```sql
SELECT Id, HandlerId, ArrivalTime, Payload FROM Notification;
```

3. **The application**: `NotificationHandler` identifies **Slack** as the source of the toasts. That is the non-corporate software used for the leak, and it explains why the classic artifacts had nothing.

4. **The conversation**: the `Payload` XML carries sender and text. Sorted by time, the whole exchange with the other party appears — an external company — including the offer, the handover and the payment.

5. **Mind the clock**: `ArrivalTime` is when Windows displayed the toast, not when the message was sent. If the question asks for the message time, take it from the toast's launch link, not from that column.

## Findings

Torrin leaked Forela information over **Slack**. The notification database kept the content of messages already shown on screen, even without the app or its logs.

## Lessons

- Windows notifications store **message content** the user already saw: evidence of communications.
- A messaging app leaves traces even after uninstalling: the notification DB stays in the profile.
- `HandlerId` identifies the application without running it.
- `Payload` is escaped XML: format it before reading.

## What it teaches

- "Minor" profile artifacts (notifications, Jump Lists, Activity) solve cases that mail and disk do not explain.
- `ArrivalTime` and the message time are different things; mixing them ruins the timeline.
- An insider may leave no email at all: the chat notification still remains.

## Pitfalls

- **Locked database**: copy `wpndatabase.db` with `-wal`/`-shm`; without them recent rows are lost.
- **Multiple accounts**: filter by the investigated user's SID.
- **XML**: the text is escaped and wrapped in app tags; extract only the body.
