# Support Leakage Makes Rapid Quantum Maintenance Singular

This repository is the reproducibility package for the paper

> **Support Leakage Makes Rapid Quantum Maintenance Singular**  
> *Soft Spectral Filters and Exponent Transmutation in Dual-Rail SSH Codes*  
> Lluis Eriksson (2026)

The paper proves that first-order leakage out of the support of a rank-deficient target produces a universal
`t log(1/t)` free-energy loss and hence logarithmically divergent rapid exact-refresh power. It then combines this
boundary singularity with exact dual-rail SSH sum rules to obtain the membrane exponent
`min{4m, 2m+q}` under the explicitly stated Davies spectral-envelope assumptions.

## Authoritative files

- `paper/main.tex` — authoritative manuscript source.
- `paper/main.pdf` — release PDF built from that source.
- `paper/support_leakage_phase_diagram.png` — figure used by the manuscript.
- `claims/CLAIM_MAP.md` — claim-by-claim proof, assumption, and verification map.
- `verification/verify.py` — deterministic numerical diagnostics.
- `verification/make_figure.py` — deterministic figure generator.

## Reproduce locally

```bash
python -m pip install -r requirements.txt
python verification/verify.py
python verification/make_figure.py --output paper/support_leakage_phase_diagram.png
tectonic -X compile paper/main.tex --outdir paper --keep-logs
python verification/check_release.py
```

The GitHub Actions workflow performs these checks, rebuilds the figure, compiles the paper with a fixed
`SOURCE_DATE_EPOCH`, checks the LaTeX/PDF invariants, and rejects drift between the committed PDF and a fresh build.

## Epistemic status

The mathematical proofs are in `paper/main.tex`. The Python suite is diagnostic evidence, not a replacement for those
proofs. The microscopic rate theorem is conditional on the stated Davies construction and two-sided spectral envelope;
the repository does not claim a uniform pre-Davies weak-coupling limit, an optimal autonomous controller, or a Lean
formalization. The manuscript and supporting package were prepared with AI assistance and reviewed by the author, who
is responsible for the claims.

## License and citation

Code is released under the MIT License. The paper and documentation are released under CC BY 4.0. Citation metadata
is provided in `CITATION.cff`.
