---
id: parallel-run-rollback
type: decision
title: Parallel-run keeps the source authoritative until acceptance
trigger: migration, rollback, cutover
source-demand: 001-migracao-x
date: 2026-07-15
scope: sigla
---

## What
Chose parallel-run over strangler; the source stays authoritative until
reconciliation signs off.

## Source (the truth)
`iniciativa-001/001-migracao-x/02-design/006-decisions.md`
