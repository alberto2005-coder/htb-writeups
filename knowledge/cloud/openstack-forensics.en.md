---
topic: Forense de tráfico OpenStack
tags: [cloud, openstack, pcap, keystone, swift, forensics]
---

# OpenStack Traffic Forensics

**English** | [🇪🇸 Español](openstack-forensics.md)

## Concept

OpenStack separates identity (Keystone), compute (Nova), networking (Neutron) and objects (Swift). A PCAP can reconstruct authentication, tokens and container operations when traffic is unencrypted or keys are available.

## When it applies

- An incident in a private cloud.
- A capture between a client and OpenStack endpoints.
- Suspected token abuse or object downloads.

## Procedure

1. Identify hosts and API versions.
2. Isolate `/v3/auth/tokens` and 201/401 responses.
3. Extract tokens and map them to users/projects.
4. List Swift operations (`/v1/AUTH_*`).
5. Correlate with Nova/Neutron logs.

```bash
tshark -r capture.pcap -Y 'http.request' -T fields -e http.host -e http.request.uri
```

## Variants

- TLS traffic with session keys.
- Internal APIs without authentication.
- Service-token abuse.

## Limitations

- TLS without keys hides paths and tokens.
- Logs may live on another node.
- Tokens expire and rotate.

## Mitigation

- TLS on every endpoint.
- Short-lived, least-scope tokens.
- Audit Swift access and rotate credentials.

## Detection

- Bulk object downloads.
- Tokens used from new IPs.
- Repeated 401s followed by 201.

## References

- <https://docs.openstack.org/keystone/latest/>
- <https://docs.openstack.org/swift/latest/>
- <https://attack.mitre.org/techniques/T1078/>
