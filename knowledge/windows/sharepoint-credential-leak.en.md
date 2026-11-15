---
topic: Credenciales expuestas en SharePoint
tags: [windows, sharepoint, credentials, enumeration, ftp]
---

# Credenciales expuestas en SharePoint

**English** | [🇪🇸 Español](sharepoint-credential-leak.md)

## Concept

SharePoint indexes lists, pages, wikis and documents that sometimes contain credentials for other services. Site enumeration and string searches collect usernames, passwords and internal paths.

## When it applies

- SharePoint reachable with broad read permissions.
- Inventory lists, guides or project pages.
- Documents referencing FTP, SMB or databases.

## Procedure

1. Enumerate accessible sites, lists and libraries.
2. Search for terms such as `password`, `ftp`, `connectionString` or `creds`.
3. Download documents and review metadata and comments.
4. Test the credentials against the indicated service.

```bash
curl -s http://<HOST>/_api/web/webs
curl -s 'http://<HOST>/_api/search/query?querytext=%27password%27'
# Download accessible lists or libraries and grep for strings
curl -s http://<HOST>/sites/<SITE>/Shared%20Documents/
```

## Variants

- Custom lists with hidden columns.
- Previous document versions.
- Comments and Office metadata.
- Guest permissions exposing internal sites.

## Limitations

- Read access to the site is required.
- Search may be disabled.
- Credentials may be expired.

## Mitigation and detection

- Review permissions and enforce least privilege in SharePoint.
- Never store secrets in lists, pages or documents.
- Rotate credentials and monitor searches and bulk downloads.

## References

- <https://learn.microsoft.com/en-us/sharepoint/security-for-sharepoint-server/security-for-sharepoint-server>
- <https://attack.mitre.org/techniques/T1552/001/>
- <https://learn.microsoft.com/en-us/sharepoint/dev/general-development/sharepoint-search-rest-api-overview>
