---
name: disk-doctor
description: Entry point for disk-space problems on macOS and Linux. Detects the OS and disk pressure, then guides the user through the full pipeline automatically - audit (disk-audit skill), interactive choice of what to delete, safe cleanup (disk-clean skill), and a final report - with optional recurring re-audits. Use when the user says the disk is full, asks to free up or clean disk space, or wants a disk checkup, without them needing to know the underlying skills.
---

# Disk doctor

One command from "my disk is full" to "here's what I reclaimed". This skill orchestrates; the real work is defined in the companion skills **disk-audit** (analysis, read-only) and **disk-clean** (deletion, gated). If either companion is missing, say so and follow its principles manually rather than improvising a different process.

## Pipeline

Run the whole pipeline in one flow — the **only mandatory stop is step 3**, where the user chooses what to delete. Don't ask permission to analyze; do ask before deleting.

### 1. Diagnose (30 seconds)

- OS: `uname` → determines catalogs and cleaners used downstream.
- Pressure: `df -h /` → "You have X free of Y (Z%)."
- Quick triage with the audit's scanner to size the opportunity: `disk-audit/scripts/scan.sh hotspots | head -15`.

Open with one honest sentence: how bad it is, and roughly how much looks reclaimable. If the disk is nearly full (<5 GB free), warn that the machine may misbehave and prioritize the fastest wins first.

### 2. Audit

Invoke the **disk-audit** skill and follow it fully: deep scans, orphan and version-stack detection, recency checks, tier classification, and the visual report. Don't shortcut it — the report is what makes step 3 an informed choice.

### 3. Choose — the gate

Present the tiers with a recommendation (Tiers 1+2 are the zero-risk default; Tier 3 adds re-download cost) and let the user pick tiers or individual items. Nothing is deleted before this answer. If the user already gave explicit standing instructions ("delete everything safe without asking"), treat that as a Tier 1+2 selection — Tier 3 and anything ambiguous still gets asked.

### 4. Clean

Invoke the **disk-clean** skill with the confirmed selection. It handles app-running checks, native cleaners, safe `rm` batches, and retries.

### 5. Report and prevent

- Headline: before → after free space, total reclaimed.
- What was skipped and why (e.g. browser running); offer to finish those when ready.
- One or two prevention tips matched to what was actually found (version-stacking IDEs → their built-in leftover cleaner; unbounded dep caches → periodic purge).

### 6. Offer automation (optional, ask — never set up silently)

If the environment supports scheduled/recurring tasks (cron-style scheduling, scheduled agents, or a recurring-prompt feature), offer **one** of:

- a monthly *read-only* re-audit that reports findings without deleting, or
- a reminder to run this skill again.

Automated runs must never delete anything — an unattended run stops after step 2 and leaves the report for the user. If no scheduling mechanism exists, suggest the user simply re-run this skill periodically.

## Tone

Be a good doctor: lead with the diagnosis in plain words, keep numbers honest (measured, not estimated, wherever possible), never touch what wasn't consented to, and leave the patient knowing what was done and how to stay healthy.
