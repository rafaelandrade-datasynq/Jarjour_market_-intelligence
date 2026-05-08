# Excel Export Contract

The Carol Excel export is a professional XLSX report for review and executive use. It is not an import of old spreadsheets and it does not claim historical Jarjour data.

The workbook must contain exactly these tabs:

1. `Pesquisa Carol`
2. `Oportunidades`
3. `Revisar`
4. `Links`
5. `Resumo da Coleta`

## Main Listing Headers

The tabs `Pesquisa Carol`, `Oportunidades` and `Revisar` use this header order:

- ENDEREÇO
- TIPO
- M²
- LOCALIZAÇÃO
- ALUGUEL
- ALUGUEL R$/M²
- COND.
- COND. R$/M²
- CONTATO
- TELEFONE
- OBSERVAÇÕES
- LINK
- STATUS
- DATA DA CAPTURA
- FONTE

The first 12 columns preserve Carol's expected model. `STATUS`, `DATA DA CAPTURA` and `FONTE` are system traceability additions.

## Tab Rules

- `Pesquisa Carol`: all normalized `Listing` rows except `DISCARDED`.
- `Oportunidades`: only rows with `is_opportunity=True`.
- `Revisar`: rows with `confidence_status` of `REVIEW`, `INCOMPLETE` or `PROBABLE_DUPLICATE`, plus rows whose review status indicates review is needed.
- `Links`: source traceability with headers `FONTE`, `BAIRRO`, `TIPO`, `LINK`, `STATUS`; links must be clickable when URL exists.
- `Resumo da Coleta`: executive collection summary with generated date, raw totals, normalized totals, raw rows without normalization, status totals, opportunities, neighborhoods, property types and sources.

## Data Visibility Rule

The export must not hide raw data. `RawListing` rows without `Listing` do not appear as normalized properties, but `Resumo da Coleta` must show them in `Brutos sem normalização`.

This preserves:

`Coletado != Validado != Oportunidade`

No tab or header may be removed or reordered without updating this contract and the export tests.
