# Contract Fixtures (Task 853)

## Fixture files

### `ECsample.pdf`
- Source: Hong Kong Labour Department - https://www.labour.gov.hk/eng/public/pdf/wcp/ECsample.pdf
- **Why interesting**: short, simple employment contract - baseline "easy" case

### `ECsample-scan.pdf`
- Source: scanned rendition of `ECsample.pdf` (same source document, no separate publisher link)
- **Why interesting**: scanned PDF with no text layer - 5 full-page images, 0 extractable chars (pdfplumber-verified: empty `extract_text()` and 0 `chars` on every page). Exists purely to test the "not supported yet" / OCR-required error path

### `Example-Mutual-Non-Disclosure-Agreement.pdf`
- Source: UK Government - https://assets.publishing.service.gov.uk/media/5a8188fd40f0b62302697d5e/Example-Mutual-Non-Disclosure-Agreement.pdf
- **Why interesting**: short, simple NDA - baseline "easy" case

### `NDA__contractors__draft.pdf`
- Source: Highways England - https://assets.publishing.service.gov.uk/media/5b06caf940f0b639f56b8aa2/NDA__contractors__draft.pdf
- **Why interesting**: tests extraction on a more legally complex NDA structure (nested definitions, multi-level sub-clauses)

### `g-cloud-8-framework-agreement.pdf`
- Source: Crown Commercial Service / UK Government - https://www.gov.uk/government/publications/g-cloud-8-framework-agreement
- **Why interesting**: long, complex framework agreement - structured/tabular content (Direct Award Criteria and KPI tables), deeply nested numbering (e.g. `9.2.2.1`), and schedules. Covers both required awkward cases. 31 pages

### `scottish-government-model-private-residential-tenancy-agreement-private-rented-sector.pdf`
- Source: Scottish Government - https://www.gov.scot/publications/private-residential-tenancy-model-agreement/documents/
- **Why interesting**: 32 pages - large eviction-ground list and structured guarantor/signature blocks. Only lease in the set

### `dz-agreement-037-nara-dickinson-signed.pdf`
- Source: U.S. National Archives (NARA) - https://www.archives.gov/files/digitization/pdf/dz-agreement-037-nara-dickinson-signed.pdf
- **Why interesting**: real signed agreement, not a blank template - numbered clauses and real signatures from organizational representatives, including digital signatures


## Coverage

7 files total. Categories: NDA x2, service agreement x2, lease x1,
employment x2 (1 digital, 1 scanned). Complexity ranges from a 2-page NDA to
a 32-page tenancy agreement. All fixtures are publicly available documents;
no confidential material is included.


## Questions

The 15 plain-language retrieval evaluation questions and expected answers
are stored in `questions.md` in this directory.