# Methods & evidence: maintenance

The public page is `methods.html`. It is a documentation surface; it does not
change clinical calculations, rules, recommendations or application behavior.
The first methods version describes engine revision
`18baf7a8651b10cb4f047072590a5c8699e293c5` from `rcckm-nextjs-preview`.

Version 1.1 is a review draft. It separately identifies application PR #79
(`63a9606c283d67d45adff4b3f41db9f54b4eef01`) for probability-first clinical
profile presentation and PR #80 (`8040420bd8c5d6e45ef95b2951a9948d33681e4c`)
for provenance-checked unrounded classification at 10%. The physician owner
subsequently agreed to an Intermediate-risk minimum of 3A; that local
refinement and the broader 3A description are committed to the draft PR and
unreleased. The physician owner approved the exact clinical differences and
baseline proposal `f08e8a234a0ca61024122e8edf3314bf3712dbc6ed3c3affebf028a4d13a158c`
on November 4, 2026. The installed baseline is
`e0b6b858c8ca9cf73e3092c20e3177fa09fa31ee0e8d137dd4fa9493c435180a`.
The pinned rule table continues to describe the released source, while the
pending-change section describes this separate proposed minimum. Neither proposal changes
the released-engine reference or the RSS export fingerprints. Confirm their
actual merge, validation and deployment status before describing them as live.
The numerical PR has a fresh pinned independent reference accepted by the
physician owner for baseline preparation. That acceptance does not approve
the earlier baseline proposal. The separate later clinical approval covers
the reviewed Level refinement and revised baseline. Preserve
the exact numerical reference and verify source/input equivalence before reuse;
final clinical-difference and release review remain required. Never transfer a
historical semantic PASS to either draft.

## Files

- `methods.html`, `methods.css`, `methods.js`: readable overview and expandable
  technical appendices, available without JavaScript.
- `downloads/rcckm-methods-data-v1.json`: canonical RSS methodology, exact
  numeric intervals, Level rule IDs and reviewed source SHA-256 fingerprints.
- `downloads/rcckm-evidence-register-v1.json`: dated developer-maintained
  evidence receipts and explicit scope limits.
- `downloads/RCCKM_Methods_and_Evidence_v1.pdf`: the full HTML content, including
  expanded technical appendices, exported for download.

## Rebuild

The RSS tables come from the engine's pure methodology export. Do not maintain
a second hand-edited point table. Use a clean engine checkout at the documented
revision, then run:

```sh
python scripts/refresh-methods-data.py /absolute/path/to/rcckm-nextjs-preview
```

The exporter evaluates the RSS dataclass/constants and pure documentation
helpers in isolation; it does not import or execute the clinical application.
A Git checkout must match the pinned revision with unchanged reviewed files.
A retained read-only reference snapshot must match the existing source
fingerprints. New clinical source requires review, an updated engine reference,
and the appropriate methods document version before regeneration.

The PDF is generated from the page, including its technical details:

```sh
python -m pip install beautifulsoup4 reportlab
python scripts/build-methods-pdf.py
```

The PDF builder uses DejaVu Sans regular and bold from
`/usr/share/fonts/truetype/dejavu`. An absent italic face falls back to regular.
Use an environment with these fonts when rebuilding. Render the PDF and check
all pages after content changes. The web page, JSON and PDF should travel
together in the same change.

## Evidence scope

The routine suite and deterministic replay are for revision `18baf7a` on
November 3, 2026 Eastern Time. The completed browser/AI semantic QA is for the
earlier frozen revision `933e1f6` on October 31, 2026 Eastern Time, through the
retained Streamlit driver. The source job logs use UTC timestamps. Never carry
the semantic PASS forward to another revision or imply it covers a full Next.js
clinical journey review. Software tests and AI QA do not establish independent
human clinical validity or prospective clinical benefit.

When refreshing results, inspect completed job steps and actual output; a
workflow title or green badge alone is insufficient. Report skipped tests
separately. Preserve adverse findings and adjudications in the underlying
development record. Update the checked date and downloadable register with
verified revision/run identities and scope.

## Review before publication

Confirm the clinical rule descriptions with the physician owner, especially
the Level 3B-to-3C modifier, source-specific signal counters, qualitative plaque
handling, and simulator endpoint/horizon assumptions. Check that all Level rule
IDs are represented, RSS rows match the export, local links and downloads
resolve, and the page remains usable at narrow widths and without JavaScript.
Source documents and private implementation code remain access-controlled;
this page publishes methodology summaries and scoring weights.
