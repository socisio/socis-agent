---
title: "Configuring Certificate Authority With Openssl — Build a two-tier PKI Certificate Authority hierarchy"
sidebar_label: "Configuring Certificate Authority With Openssl"
description: "Build a two-tier PKI Certificate Authority hierarchy"
---

{/* This page is auto-generated from the skill's SKILL.md by website/scripts/generate-skill-docs.py. Edit the source SKILL.md, not this page. */}

# Configuring Certificate Authority With Openssl

Build a two-tier PKI Certificate Authority hierarchy

## Skill metadata

| | |
|---|---|
| Source | Optional — install with `socis skills install official/security/configuring-certificate-authority-with-openssl` |
| Path | `optional-skills/security/configuring-certificate-authority-with-openssl` |
| Version | `1.0` |
| Author | mahipal (vendored by SOCIS) |
| License | Apache-2.0 |
| Platforms | linux, macos, windows |
| Tags | `cryptography`, `pki`, `certificate-authority`, `openssl`, `x509` |

## Reference: full SKILL.md

:::info
The following is the complete skill definition that SOCIS loads when this skill is triggered. This is what the agent sees as instructions when the skill is active.
:::

# Configuring Certificate Authority with OpenSSL

## Overview

A Certificate Authority (CA) is the trust anchor in a PKI hierarchy, responsible for issuing, signing, and revoking digital certificates. This skill covers building a two-tier CA hierarchy (Root CA + Intermediate CA) using OpenSSL and the Python cryptography library, including CRL distribution, OCSP responder configuration, and certificate policy management.


## When to Use

- When deploying or configuring configuring certificate authority with openssl capabilities in your environment
- When establishing security controls aligned to compliance requirements
- When building or improving security architecture for this domain
- When conducting security assessments that require this implementation

## Prerequisites

- Familiarity with cryptography concepts and tools
- Access to a test or lab environment for safe execution
- Python 3.8+ with required dependencies installed
- Appropriate authorization for any testing activities

## Objectives

- Create a Root CA with self-signed certificate
- Create an Intermediate CA signed by the Root CA
- Issue server and client certificates from the Intermediate CA
- Configure Certificate Revocation Lists (CRLs)
- Implement certificate policies and constraints
- Build a complete PKI hierarchy programmatically

## Key Concepts

### CA Hierarchy

```
Root CA (offline, air-gapped)
  |
  +-- Intermediate CA (online, operational)
        |
        +-- Server Certificates
        +-- Client Certificates
        +-- Code Signing Certificates
```

### Certificate Extensions

| Extension | Purpose | Critical |
|-----------|---------|----------|
| basicConstraints | CA:TRUE/FALSE, pathLenConstraint | Yes |
| keyUsage | keyCertSign, cRLSign, digitalSignature | Yes |
| extendedKeyUsage | serverAuth, clientAuth, codeSigning | No |
| subjectKeyIdentifier | Hash of public key | No |
| authorityKeyIdentifier | Issuer's key identifier | No |
| crlDistributionPoints | URL to CRL | No |
| authorityInfoAccess | OCSP responder URL | No |

## Security Considerations

- Root CA private key must be stored offline (air-gapped HSM)
- Use minimum 4096-bit RSA or P-384 ECDSA for CA keys
- Set path length constraints on intermediate CAs
- Implement certificate policies (OIDs)
- Enable CRL and OCSP for revocation checking
- Audit all certificate issuance operations

## Validation Criteria

- [ ] Root CA self-signed certificate is valid
- [ ] Intermediate CA certificate chains to Root CA
- [ ] Issued certificates chain to Intermediate -> Root
- [ ] Path length constraints are enforced
- [ ] CRL is generated and accessible
- [ ] Revoked certificates appear in CRL
- [ ] Certificate policies are correctly embedded
