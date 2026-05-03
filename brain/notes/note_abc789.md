---
confidence: 0.9
created_at: '2026-05-03T09:08:57.482035Z'
freshness_score: 1.0
id: note_abc789
last_verified_at: '2026-05-03T09:08:57.482035Z'
related_notes: []
source_modality: text
tags:
- pgvector
- FAISS
title: pgvector chosen for similarity search
topics:
- topic_similarity_search
type: decision
updated_at: '2026-05-03T09:08:57.482035Z'
---

## TL;DR
pgvector selected for similarity search despite FAISS usage elsewhere.

## Context
Need for consistent similarity search across services.

## Content
- Decision made to use pgvector for similarity search.
- Another team uses FAISS, potentially causing inconsistent results.

## Watch out for
Inconsistent results across services due to different vector search libraries.
