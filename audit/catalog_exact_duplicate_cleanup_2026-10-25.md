# Exact duplicate catalog-row cleanup

During the 2026-10-25 metadata refresh, the tracked wave-field candidate catalog contained 16 exact duplicate metadata rows. Every column matched within each duplicate pair; the repeated keys were nine 2011 phenotype rows, five 2015 rows (three phenotype and two parent-context exposure rows), and two 2018 phenotype rows. These were duplicate catalog records, not distinct response options or source mappings.

Added `scripts/deduplicate_exact_catalog_rows.py` to remove only fully identical rows from the candidate CSV/JSON and public master catalog before role shards are generated. It preserves the first occurrence and all fields, and is idempotent. The cleanup reduced the displayed metadata row counts by 2 E and 14 P entries; it did not remove any unique wave-field mapping or alter any association result. A regression test protects uniqueness.
