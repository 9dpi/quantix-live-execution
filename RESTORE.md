# RESTORE.md

## Purpose

This document defines the **official full-restore procedure** for the Quantix / SignalGenius AI project.

A **full restore** means reconstructing the system **exactly as it existed at the time of a verified snapshot**, without regeneration, reinterpretation, or modification.

This procedure exists to ensure:

* Auditability
* Reproducibility
* Historical integrity

---

## Core Principle

> **Snapshots are frozen historical anchors.**
> They are restored, not replayed.

No component may be regenerated or recalculated during a restore.

---

## What Can Be Restored

A snapshot is considered **fully restorable** if the following components are available:

1. Frozen snapshot documentation
2. Tagged source code
3. Append-only execution logs
4. Snapshot configuration state
5. UI build reference

All five are mandatory.

---

## Required Components

### 1. Snapshot Anchor (Read-only)

File example:

```
MPV_VERIFIED_SNAPSHOT_20260121.md
```

Status:

* Frozen
* Read-only

This file defines:

* The verified system behavior
* The reference timestamps
* The evidence scope

It must never be edited.

---

### 2. Source Code (Tagged)

The codebase must be restored using a **git tag or commit hash** corresponding to the snapshot.

Example:

```
git checkout snapshot-mpv-20260121
```

or

```
git checkout a7f3c9e
```

> Restoring from an untagged branch is not permitted.

---

### 3. Immutable Logs (Append-only)

The following log files must be restored **as-is**:

```
logs/
├── auto_execution_log.jsonl
├── daily_gate_log.jsonl
└── signal_log.jsonl (if present)
```

Rules:

* Logs are read-only
* No entries may be deleted
* No new entries may be appended during restore

---

### 4. Snapshot Configuration State

Environment configuration must match the snapshot exactly.

Recommended format:

```
.env.snapshot_20260121
```

Typical variables include:

* EXECUTION_MODE
* DAILY_EXECUTION_CAP
* TIMEZONE
* AUTO_ENABLED

Runtime configuration must not be inferred or guessed.

---

### 5. UI Build Reference

The UI must be restored from the **same build or commit** used at snapshot time.

Examples:

* GitHub Pages commit hash
* Static build artifact

The UI must not be rebuilt using newer code or copy.

---

## Full Restore Procedure

Follow the steps below **in order**.

### Step 1 — Checkout Frozen Code

```
git checkout snapshot-mpv-20260121
```

---

### Step 2 — Load Snapshot Configuration

```
cp .env.snapshot_20260121 .env
```

---

### Step 3 — Restore Logs

Place the immutable log files into their original paths.

No services should be running while this is done.

---

### Step 4 — Deploy Snapshot UI

Deploy or serve the UI using the exact commit or artifact referenced by the snapshot.

Do not rebuild the UI.

---

### Step 5 — Verification Check

Cross-check the restored system against the snapshot:

* Signal timestamps
* Signal identifiers
* Execution order
* UI wording
* Log contents

All elements must match exactly.

If any discrepancy exists, the restore is invalid.

---

## Prohibited Actions

During restore, the following actions are strictly forbidden:

* Regenerating signals
* Re-running AUTO to recreate logs
* Editing snapshot files
* Updating UI copy
* Adding explanatory annotations

A restore must reflect history, not reinterpret it.

---

## Restore Guarantee Statement

> **This snapshot is fully restorable.**
> Given the frozen code, configuration, and append-only logs, the system state can be reconstructed exactly as verified.

---

## One-line Explanation (External Use)

> "We do not replay history. We restore it from frozen code, logs, and configuration."

---

## Status

This document is authoritative.
Any future snapshot must provide the same restore guarantees to be considered valid.
