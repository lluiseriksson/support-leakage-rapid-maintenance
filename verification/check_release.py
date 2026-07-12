"""Check manuscript, figure, build log, and release-PDF invariants."""

from __future__ import annotations

import argparse
import re
from pathlib import Path

from PIL import Image, ImageChops, ImageStat
from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[1]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--generated-figure", type=Path)
    args = parser.parse_args()

    tex_path = ROOT / "paper" / "main.tex"
    pdf_path = ROOT / "paper" / "main.pdf"
    log_path = ROOT / "paper" / "main.log"
    figure_path = ROOT / "paper" / "support_leakage_phase_diagram.png"
    tex = tex_path.read_text(encoding="utf-8")

    required = [
        "Support Leakage Makes Rapid Quantum",
        r"k_{\mathrm B} T a t \log(1/t)",
        r"w_x(1-w_x)",
        r"\min\{4m,2m+q\}",
        r"\lim_{\ell\to \infty} \lim_{\tau\downarrow 0}",
        r"\frac{1}{2}\{L^{\dagger} L,\rho\}",
        r"\begin{theorem}[Soft-filter exponent transmutation]",
    ]
    for token in required:
        require(token in tex, f"missing source invariant: {token}")

    require(tex.count(r"\begin{proof}") == tex.count(r"\end{proof}"), "unbalanced proof environments")
    require(tex.count(r"\begin{document}") == 1 and tex.count(r"\end{document}") == 1, "document boundary error")
    require("QED." not in tex, "literal QED duplicates the proof symbol")
    require("Figure 1: Figure 1" not in tex, "duplicated figure label")

    if log_path.exists():
        log = log_path.read_text(encoding="utf-8", errors="replace")
        forbidden = ["LaTeX Error", "Undefined control sequence", "Overfull \\hbox", "Overfull \\vbox"]
        for phrase in forbidden:
            require(phrase not in log, f"build-log failure: {phrase}")

    reader = PdfReader(str(pdf_path))
    require(len(reader.pages) == 14, f"expected 14 pages, found {len(reader.pages)}")
    metadata = reader.metadata or {}
    require("Support Leakage Makes Rapid Quantum Maintenance Singular" in str(metadata.get("/Title", "")), "PDF title metadata")
    require("Lluis Eriksson" in str(metadata.get("/Author", "")), "PDF author metadata")
    for index, page in enumerate(reader.pages, start=1):
        require((page.extract_text() or "").strip(), f"empty PDF page {index}")

    with Image.open(figure_path) as figure:
        require(figure.width >= 2000 and figure.height >= 600, "release figure resolution is too small")

    if args.generated_figure:
        with Image.open(figure_path).convert("RGB") as expected, Image.open(args.generated_figure).convert("RGB") as generated:
            require(expected.size == generated.size, "regenerated figure dimensions differ")
            diff = ImageChops.difference(expected, generated)
            mae = sum(ImageStat.Stat(diff).mean) / 3.0
            require(mae < 2.0, f"regenerated figure drift is too large: MAE={mae:.4f}")
            print(f"figure mean absolute pixel drift = {mae:.6f}")

    proof_count = tex.count(r"\begin{proof}")
    print(f"release checks passed: {len(reader.pages)} pages, {proof_count} proofs")


if __name__ == "__main__":
    main()
