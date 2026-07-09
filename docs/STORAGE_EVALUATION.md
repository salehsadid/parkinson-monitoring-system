# Storage Evaluation

## Current Architecture

One `SensorRecord` row per packet at declared 50 Hz.

## Measured Data

From real database:
- 4521 rows
- 1.16 MB database size
- ~200 bytes per row average
- Real observed rate ≈ 50 Hz

## Projections at 50 Hz

| Metric | Value |
|--------|-------|
| Rows/second | 50 |
| Rows/minute | 3,000 |
| Rows/hour | 180,000 |
| Rows/day | 4,320,000 |
| Rows/72 hours | 12,960,000 |
| Size/72 hours (estimated) | ~2.5 GB |

## Storage Options

### OPTION A: Keep Every Sample (Current)

**Pros**: Full fidelity, no information loss
**Cons**: Large database, slow queries at scale

**Verdict**: Works for 72 hours on modern hardware. SQLite handles millions of rows.

### OPTION B: Batch Inserts + Retention

**Pros**: Same as A, with automatic cleanup
**Cons**: Still large

**Verdict**: Already implemented via `retention.py` (72-hour cleanup).

### OPTION C: Raw Session Files + Summary DB

**Pros**: Database stays small, raw data preserved in CSV/Parquet
**Cons**: Two storage systems to manage

**Verdict**: Good for ML experiments. Raw sessions in `data/raw/`, summary in DB.

### OPTION D: Downsampled History

**Pros**: Very small database
**Cons**: Information loss

**Verdict**: Not recommended for Stage 2.1. Keep raw data.

### OPTION E: Event-Centered Retention

**Pros**: Only stores FOG events and surrounding context
**Cons**: Loses continuous monitoring data

**Verdict**: Not suitable. Caregiver needs continuous history.

### OPTION F: Hybrid (Recommended)

**Pros**: Best of both worlds
**Cons**: More complex

**Structure**:
```
data/
├── raw/           # Exported session CSVs (full 50 Hz)
│   └── session_*.csv
├── interim/       # Cleaned/resampled data
├── sessions/      # Session metadata JSON
└── parkinson_monitoring.db  # Recent data + events
```

**Database**: Keep 72 hours of raw data (auto-cleanup).
**Raw exports**: Permanent archive of selected sessions.
**Session metadata**: JSON sidecar files for reproducibility.

## Recommendation

**For Stage 2.1**: Keep current architecture (Option A/F hybrid).

- SQLite with 72-hour retention is sufficient
- Export important sessions to CSV for permanent storage
- Session metadata in JSON files
- No schema changes needed

**For production**: Consider Option F with separate raw archive and summary database.

## 72-Hour Feasibility

At 50 Hz continuous:
- ~13 million rows
- ~2.5 GB storage
- SQLite handles this with proper indexes
- WAL mode already enabled
- Queries with LIMIT and time filters remain fast

**Conclusion**: 72-hour raw storage is feasible on any modern laptop.
