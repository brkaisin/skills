---
name: disk-doctor
description: Disk-space checkup and safe cleanup for macOS and Linux. Detects the OS and disk pressure, analyzes what is taking space (caches, app data, logs, leftovers of uninstalled apps), presents a tiered report, lets the user choose what to delete, then cleans safely and reports the space reclaimed. Use when the user says the disk is full, asks what is taking or eating disk space, what can be cleaned or deleted, or wants to free up space or get a disk audit or checkup. Analysis is read-only; nothing is deleted without the user's explicit selection.
---

# Disk doctor

One flow from "my disk is full" to "here's what I reclaimed". The two working phases live in this folder and are loaded when their step starts:

- **`AUDIT.md`** — the analysis phase: scanning, leftover detection, tier classification, visual report. Strictly read-only.
- **`CLEAN.md`** — the deletion phase: safety protocol, native cleaners, hard limits, verification.

Follow the pipeline below; the **only mandatory stop is step 3**, where the user chooses what to delete. Don't ask permission to analyze; never delete before the user has chosen.

## Pipeline

### 1. Diagnose (30 seconds)

- OS: `uname` → determines catalogs and cleaners used downstream.
- Pressure: `df -h /` → "You have X free of Y (Z%)."
- Quick triage to size the opportunity: `scripts/scan.sh hotspots | head -15`.

Open with one honest sentence: how bad it is, and roughly how much looks reclaimable. If the disk is nearly full (<5 GB free), warn that the machine may misbehave and prioritize the fastest wins first.

### 2. Audit

Read `AUDIT.md` and follow it fully: deep scans, orphan and version-stack detection, recency checks, tier classification, and the visual report. Don't shortcut it — the report is what makes step 3 an informed choice. This phase never deletes anything.

### 3. Choose — the gate

Present the tiers with a recommendation (Tiers 1+2 are the zero-risk default; Tier 3 adds re-download cost) and let the user pick tiers or individual items. Nothing is deleted before this answer. If the user already gave explicit standing instructions ("delete everything safe without asking"), treat that as a Tier 1+2 selection — Tier 3 and anything ambiguous still gets asked.

### 4. Clean

Read `CLEAN.md` and execute the confirmed selection under its rules: app-running checks, native cleaners, safe `rm` batches, retries, hard no-touch limits.

### 5. Report and prevent

- Headline: before → after free space, total reclaimed.
- What was skipped and why (e.g. browser running); offer to finish those when ready.
- One or two prevention tips matched to what was actually found (version-stacking IDEs → their built-in leftover cleaner; unbounded dep caches → periodic purge).

### 6. Offer automation (optional, ask — never set up silently)

If the environment supports scheduled/recurring tasks, offer **one** of: a monthly *read-only* re-audit that reports findings without deleting, or a reminder to run this skill again. Automated runs must never delete anything — an unattended run stops after step 2 and leaves the report for the user. If no scheduling mechanism exists, suggest the user simply re-run this skill periodically.

## Tone

Be a good doctor: lead with the diagnosis in plain words, keep numbers honest (measured, not estimated, wherever possible), never touch what wasn't consented to, and leave the patient knowing what was done and how to stay healthy.
