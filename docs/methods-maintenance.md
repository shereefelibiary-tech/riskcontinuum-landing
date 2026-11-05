# Methods and evidence: maintenance

Version 1.2 describes merged application revision
`2d6923ddd2619e4f55bb8791f1306fd60646ed5e`. Its Git tree matches tested
application head `789d38284d3e103959613dea8ad7bde11e5c469f`.

The current methods include the Intermediate PREVENT minimum of Level 3A,
the broader 3A description, and provenance-checked unrounded classification
at 3%, 5% and 10%. The complete base-rule table is followed by the minimum
and the separate 3C modifier. The probability-first UI proposal in PR #79
remains unmerged and appears only in the downloadable pending-change metadata.

## Editorial approach

Lead with the clinical workflow, implementation and completed verification.
Keep the equations, counters, weights and assumptions available in the technical
sections. Consolidate clinical-evaluation maturity in the evaluation section
and practical use guidance in the scope section. State limitations plainly,
without repeating disclaimers throughout the page.

## Files

- `methods.html`, `methods.css`, `methods.js`: the public page; technical
  details remain available without JavaScript.
- `downloads/rcckm-methods-data-v1.json`: canonical RSS export, exact intervals,
  current Level rule identifiers, source fingerprints and change metadata.
- `downloads/rcckm-evidence-register-v1.json`: source-specific records,
  workflow receipts, historical semantic evidence and clinical-evaluation scope.
- `downloads/RCCKM_Methods_and_Evidence_v1.pdf`: the full page, including
  expanded technical appendices, exported for download.

The download filenames remain stable across document versions.

## Rebuild and check

Use the clean, pinned engine checkout:

```sh
python scripts/refresh-methods-data.py /absolute/path/to/rcckm-nextjs-preview
python scripts/build-methods-pdf.py
```

The exporter evaluates only the RSS documentation dataclass/constants and pure
helpers. It does not import or assess patients through the clinical application.
A read-only source snapshot must match retained file fingerprints. When updating
the implementation reference, first verify its files against that exact Git
revision and regenerate the export from those files. Do not retag old generated
data as a new source.

The PDF builder needs Beautiful Soup, ReportLab and the DejaVu Sans fonts in
`/usr/share/fonts/truetype/dejavu`. Render and inspect the final pages. Keep
the page, JSON downloads and PDF consistent in the same change. Check local
anchors, links, Level rule coverage and the RSS export before publication.

## Evidence records

The November 4, 2026 Eastern Time CI run `41950817613` passed all four jobs.
Each platform's ordinary suite passed 7,277 tests with 160 skipped. The Critic
harness passed 379 with 15 skipped; the provider-free 600 compared MATCH with
zero changed journeys; FHIR/paste parity passed 500 journeys. The Next.js build
and browser-regression job also passed. Counts describe checks and synthetic
journeys, not study participants.

The independent numerical reference is reused unchanged after a complete
source/input/model/endpoint equivalence proof: 535 direct matches, five governed
boundary projections and 60 clinically ineligible journeys. All 600 records and
two published examples reproduce with zero differences. The approved baseline is
`e4fdda338cd0c61c1a77e0f8284547d9b9ae8aa947de70e726c4cd7f62f270f0`.

The completed browser/AI semantic record is for revision `933e1f6` on
October 31, 2026, through the retained Streamlit driver. The physician owner
waived a new semantic gate for the November 5 merge in PR #80. Record that
decision as a waiver, while preserving the earlier source-bound evidence,
original findings and adjudications. Independent clinical evaluation remains
separate from software and model-assisted checks.

Inspect job steps and receipt text when refreshing results. Preserve skipped
counts, distinguish test dates from verification/merge dates, and keep the
tested source separate from the implementation reference and deployment status.
Source revision alone does not establish which version is being served.
