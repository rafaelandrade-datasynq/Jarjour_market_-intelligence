# Source Registry

Planned sources for future tickets:

- DF Imoveis
- Wimoveis
- Net Imoveis
- Lugar Certo

Ticket 5 includes an offline DF Imoveis parser against the official fixture only. It is not live portal integration. The fixture must remain fake/local and contain at least 8 representative candidates.

Allowed current source names:

- `demo`: demo seed data.
- `dfimoveis`: offline fixture parser output.

Wimoveis, Net Imoveis and Lugar Certo remain future sources.

DF Imoveis live preflight is permitted only behind `ENABLE_LIVE_SCRAPING=true`, with one page, at most 20 candidates, dry-run by default and evidence required. It is not a complete integration or seasonal collection.
