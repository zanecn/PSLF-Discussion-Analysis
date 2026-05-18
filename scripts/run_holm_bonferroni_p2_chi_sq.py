"""
run_holm_bonferroni_p2_chi_sq.py
================================
R17++ Agent 5 M5 fix: apply Holm-Bonferroni step-down adjustment to the
Paper 2 §5.4 per-event 5-stance × 2-window chi-sq family (8 events).

Pulls p-values from intention_results.txt:121-128 and computes adjusted
p-values + flags which events remain significant after family-wise α=0.05
correction across the 8-event family.

Output: paper2_holm_bonferroni_p2_chi_sq_results.txt
"""
import sys
from pathlib import Path

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

PROJECT = Path("C:/Users/zanen/PSLF_2026/PSLF-Discussion-Analysis")


def holm_bonferroni(p_values_dict, alpha=0.05):
    """
    Apply Holm-Bonferroni step-down adjustment.

    Returns dict mapping event -> {
        raw_p, rank, threshold (alpha/(m-rank+1)), significant
    }
    where m = number of tests in family.
    """
    items = sorted(p_values_dict.items(), key=lambda kv: kv[1])
    m = len(items)
    results = {}
    # Step-down: reject as long as raw p < alpha/(m-rank+1)
    # Once a test fails, all higher-ranked also fail
    still_reject = True
    for rank, (event, p) in enumerate(items, start=1):
        threshold = alpha / (m - rank + 1)
        if still_reject and p < threshold:
            significant = True
        else:
            significant = False
            still_reject = False
        # Adjusted p (Holm): p_adj = max over k=1..rank of (m-k+1) * p_k
        # but report each step's threshold and significance directly
        results[event] = {
            "raw_p": p,
            "rank": rank,
            "threshold": threshold,
            "significant": significant,
        }
    return results


def main():
    # P-values from intention_results.txt:121-128 (per-event 5-stance chi-sq, 90d or 60d windows)
    p_values = {
        "Limited PSLF Waiver":       0.00001,   # reported as 0.0000 in source; using small value
        "IDR Account Adjustment":    0.00001,
        "Biden Mass Forgiveness":    0.0001,
        "Biden v. Nebraska SCOTUS":  0.4435,
        "Payments Restart":          0.3665,
        "SAVE Admin Forbearance":    0.0003,
        "Trump PSLF EO":             0.0071,
        "Final Trump PSLF Rule":     0.00001,
    }

    print("=" * 90)
    print("PAPER 2 §5.4 HOLM-BONFERRONI ADJUSTMENT (R17++ Agent 5 M5 fix)")
    print("=" * 90)
    print()
    print("Per-event chi-sq family: 5-stance × 2-window distribution test, 8 events")
    print("Source: intention_results.txt:121-128")
    print("Family-wise α = 0.05")
    print()

    results = holm_bonferroni(p_values, alpha=0.05)

    out_lines = []
    out_lines.append("=" * 90)
    out_lines.append("PAPER 2 §5.4 HOLM-BONFERRONI ADJUSTMENT (R17++ Agent 5 M5 fix)")
    out_lines.append("=" * 90)
    out_lines.append("")
    out_lines.append("This script formalizes the Holm-Bonferroni step-down adjustment for the")
    out_lines.append("Paper 2 §5.4 per-event 5-stance × 2-window chi-sq family.")
    out_lines.append("")
    out_lines.append("Per Agent 5 M5 audit finding: §5.4 reports raw chi-sq p-values without")
    out_lines.append("family-wise multiple-comparison correction. With 8 events in the family,")
    out_lines.append("Holm-Bonferroni at α=0.05 sets per-test thresholds α/(m-rank+1) = 0.00625,")
    out_lines.append("0.00714, ..., 0.05.")
    out_lines.append("")
    out_lines.append("Source: intention_results.txt:121-128 (per-event chi-sq on 5-stance dist)")
    out_lines.append("")
    out_lines.append(f"{'Event':32} {'raw p':>10} {'rank':>5} {'threshold':>10} {'significant?':>15}")
    out_lines.append("-" * 80)
    # Sort by rank for output
    sorted_items = sorted(results.items(), key=lambda kv: kv[1]["rank"])
    for event, info in sorted_items:
        p_str = f"{info['raw_p']:.4f}" if info["raw_p"] > 0.0001 else "<0.0001"
        sig_str = "✓ SIG" if info["significant"] else "✗ NS"
        out_lines.append(
            f"  {event:30} {p_str:>10} {info['rank']:>5}   {info['threshold']:.5f}     {sig_str:>15}"
        )

    n_sig = sum(1 for v in results.values() if v["significant"])
    out_lines.append("")
    out_lines.append(f"RESULT: {n_sig} of 8 events significant after Holm-Bonferroni at family-wise α=0.05.")
    out_lines.append("")
    out_lines.append("Events significant after Holm-Bonferroni:")
    for event, info in sorted_items:
        if info["significant"]:
            p_disp = f"{info['raw_p']:.4f}" if info['raw_p'] > 0.0001 else "<0.0001"
            out_lines.append(f"  ✓ {event} (raw p={p_disp}, threshold {info['threshold']:.5f})")
    out_lines.append("")
    out_lines.append("Events NOT significant after Holm-Bonferroni:")
    for event, info in sorted_items:
        if not info["significant"]:
            out_lines.append(f"  ✗ {event} (raw p={info['raw_p']:.4f}, threshold {info['threshold']:.5f})")
    out_lines.append("")
    out_lines.append("INTERPRETATION:")
    out_lines.append("-" * 90)
    out_lines.append("Same conclusion as raw-p comparison: 6 of 8 events show significant pre/post")
    out_lines.append("stance-distribution shifts, 2 of 8 do not (Biden v. Nebraska SCOTUS and")
    out_lines.append("Payments Restart). The Holm-Bonferroni correction does NOT demote any event")
    out_lines.append("that was significant at raw α=0.05; all 6 raw-significant events remain")
    out_lines.append("significant after family-wise adjustment.")
    out_lines.append("")
    out_lines.append("This confirms the R17 correction to Paper 2 §5.4 (which had previously claimed")
    out_lines.append("'all 8 events p<10⁻⁴' — actually 6 of 8 significant at raw or Holm-Bonferroni")
    out_lines.append("α=0.05; Biden v. Nebraska SCOTUS and Payments Restart are NS at either level).")
    out_lines.append("")
    out_lines.append("Note: this addresses ONLY the 5-stance distribution chi-sq family (8 events).")
    out_lines.append("The per-event × per-cohort × per-topic family (intention_results.txt:404+) is")
    out_lines.append("larger and was not corrected here; that family-wise correction is recommended")
    out_lines.append("if the per-event × per-cohort topic table is presented in the main paper.")

    out_text = "\n".join(out_lines)
    out_path = PROJECT / "paper2_holm_bonferroni_p2_chi_sq_results.txt"
    out_path.write_text(out_text, encoding="utf-8")
    print(out_text)
    print(f"\nSaved: {out_path}")


if __name__ == "__main__":
    main()
