---
confidence: 0.9
created_at: '2026-05-03T05:08:53.921688Z'
freshness_score: 1.0
id: note_abc123
last_verified_at: '2026-05-03T05:08:53.921688Z'
related_notes: []
source_modality: text
tags:
- deployment
- fly.io
- docker
title: Fly.io is the canonical deployment target
topics:
- topic_deployment
type: decision
updated_at: '2026-05-03T05:08:53.921688Z'
---

## TL;DR
Deployment target is Fly.io; use `fly deploy` for shipping.

## Context
Migrated from Railway due to cost increases with monorepo projects.

## Content
- Platform: Fly.io
- Deploy command: `fly deploy`
- Dockerfile-based builds
- Railway deployment is deprecated
