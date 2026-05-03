---
confidence: 0.9
created_at: '2026-05-03T05:12:43.869349Z'
freshness_score: 1.0
id: note_abc456
last_verified_at: '2026-05-03T05:12:43.869349Z'
related_notes: []
source_modality: text
tags:
- security
- compliance
title: 'Token lifetimes: 25 min access, 7 day refresh'
topics:
- topic_authentication
type: decision
updated_at: '2026-05-03T05:12:43.869349Z'
---

## TL;DR
Access tokens expire in 25 minutes; refresh tokens expire in 7 days.

## Context
Access token lifetime increased from 15 to 25 minutes for a client proposal. Refresh token lifetime remains 7 days, aligned with legal's session compliance requirement.

## Content
- Access token TTL: 25 minutes
- Refresh token TTL: 7 days
- Pending: confirm 25 min still satisfies legal's session compliance bound (originally sized around 15 min).
- Change driven by client proposal — revisit after proposal outcome.

## Watch out for
The previous 15-minute value was explicitly tied to legal's compliance requirement. Verify 25 minutes is still within that bound before shipping.
