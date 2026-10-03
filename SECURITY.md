# Security policy

## Supported version

Security fixes are provided for the latest 2.x release.

## Privacy and threat model

Sofoste Medical Center is a local educational tool. It protects a small record from someone who obtains only the QR packet by requiring a separately transferred key. AES-GCM detects a modified packet, and failed decryption attempts are limited in memory.

The application does not provide user accounts, audit trails, server authentication, durable storage, backups or TLS. Anyone who obtains both the QR and its transfer key can read the record. LAN mode exposes the app over plain HTTP to the current network and must be used only on a trusted private network. For regulated or remote medical use, choose an audited clinical system with identity, access control and encrypted transport.

## Reporting a vulnerability

Please use GitHub's private vulnerability reporting for this repository. Do not include real patient information in a report or test case.
