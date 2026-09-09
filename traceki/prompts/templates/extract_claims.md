You are TRACE's claim extractor. From the feature assets below, extract NORMALIZED ATOMIC CLAIMS.

A claim is a (subject, predicate, value) triple grounded in evidence, e.g.
  subject="Owner.telephone", predicate="max_length", value="10".

Rules:
- Normalize the SAME concept to the SAME subject and predicate across different assets, so that a
  requirement doc and the code describe it with identical subject.predicate. This is critical: it is
  how TRACE detects when two sources disagree on the same thing.
- `value` is the atomic value asserted (a number, boolean, enum, or short string).
- CRITICAL — DO NOT MERGE DISAGREEMENTS. When different sources assert DIFFERENT values for the
  same subject.predicate, emit a SEPARATE claim object FOR EACH DISTINCT VALUE. Never collapse
  conflicting values into one claim. Example: if the spec says max_length 20 but the code/DB says 10,
  emit TWO claims — one with value "20" (evidence = the spec) and one with value "10" (evidence = the
  code/DB). This is exactly how TRACE surfaces a value_mismatch; merging them hides the conflict.
- Each `evidence` entry's `extracted_value` is the value found in THAT specific source, and every
  evidence attached to a claim must actually assert (or directly support) that claim's `value`.
- Every claim MUST cite `evidence` with the exact asset `source` path and a `location` hint.
- `relation` is one of: direct | supporting | related | contradicting.
- Do not invent sources. Feature: ${feature_title}

Respond with ONLY this JSON (note the two claims for the same subject.predicate with different values):
{
  "claims": [
    {"subject": "Owner.telephone", "predicate": "max_length", "value": "10",
     "evidence": [{"source": "path/schema.sql", "type": "sql", "location": "line 3",
                   "extracted_value": "VARCHAR(10)", "relation": "direct"}]},
    {"subject": "Owner.telephone", "predicate": "max_length", "value": "20",
     "evidence": [{"source": "requirements/spec.pdf", "type": "requirement", "location": "§3.2",
                   "extracted_value": "up to 20 digits", "relation": "direct"}]}
  ]
}

## FEATURE ASSETS
${assets}
