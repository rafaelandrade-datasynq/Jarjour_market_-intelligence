# Evidence Policy

Future collection should keep enough evidence to explain where a record came from. Evidence can include source URL, captured raw fields, raw payload JSON, screenshots or saved HTML snippets when legally and operationally appropriate.

Evidence supports review; it does not replace the requirement to save `RawListing`.

For offline-first scraping, evidence is the saved local HTML fixture plus raw payload fields. Evidence files live under `data/evidence/` and should never be used as a substitute for persisted `RawListing` rows.

Offline fixture evidence must use this structure:

```text
data/evidence/dfimoveis/YYYYMMDD-HHMMSS/
├── page.html
└── meta.json
```

`meta.json` must include `source_name`, `fixture_name`, `collected_at`, `candidate_count` and `mode: offline_fixture`.

Live preflight evidence must also be saved whenever a page is opened:

```text
data/evidence/dfimoveis/YYYYMMDD-HHMMSS/
├── page.html
├── meta.json
└── screenshot.png
```

`screenshot.png` is best-effort. `meta.json` must include source, target URL, collected timestamp, candidate count, mode, status and whether a block/CAPTCHA/login wall was detected. Evidence records blocks; it must not be used to justify bypassing them.
