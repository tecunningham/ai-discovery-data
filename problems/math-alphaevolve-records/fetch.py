#!/usr/bin/env python3
"""Dated record sequences for a pre-committed sample of AlphaEvolve problems.

Run: python3 problems/math-alphaevolve-records/fetch.py

Writes this folder's alphaevolve-records.csv and prints the comparison the
AlphaEvolve discussion lacks: how large the AI-era step was against the
distribution of historical steps on the same quantity. It also writes the two
per-problem slices that neighbouring folders plot — problem 6.8 to
../math-kissing-11/kissing-11-records.csv and problems 6.44 and 6.3 to
../math-sums-autoconvolution/sums-autoconvolution-records.csv — so that the hand
transcription exists in exactly one place and the slices cannot drift from it.

Sampling, fixed before any values were read. The frame is the 31 problems in
`alphaevolve-inventory.csv` whose status is world_record, worse_than_record or
former_record — those with a live numeric record. matched_optimal is excluded
because its history has terminated and unclassified because it is mostly not
record-type. Twelve were drawn as the smallest SHA-256 digests of
"apple-picking-cyber-math-2026-07-26|<label>", which anyone can recompute:

    6.4  6.1  6.36  6.9  6.35  6.42  6.10  6.38  6.3  6.40  6.44  6.30

That draw happens to contain all four former_record problems, 4 of 12 against
4 of 31 in the frame, so already-surpassed problems are over-represented by
about 2.5x. The draw is kept rather than redrawn, since redrawing on inspection
is the thing pre-commitment exists to prevent; weight accordingly.

The values below are transcribed by hand from the paper's own prose, verbatim
where quoted, with the reference number and its bibliography year recorded per
step. Only six of the twelve sampled problems yielded a scalar record sequence
at all; the other six are recorded in NO_SEQUENCE with the reason, because that
is itself the main finding of this phase.

Agent coding, which is load-bearing and cannot be read off a date:
  human_analytic        a construction or proof done by hand
  human_search          a computer search run by humans (brute force, gradient
                        descent, a commercial solver)
  ai_evolution          AlphaEvolve
  ai_guided_search      transformer-guided search run by humans (PatternBoost);
                        neither cleanly human nor an autonomous AI system
  ai_agents             a collective AI-agent platform (EinsteinArena)
  community_table       a curated records webpage, often undated

EXTENSION (2026-07-28). EXTENSION_RECORDS below adds the twelve remaining
world_record and former_record problems that the pre-committed draw did not
select, researched from primary sources (arXiv, journal pages, MathOverflow,
and the community record tables the paper itself cites), so that every
record-status problem in the frame now has either a dated sequence or a
documented reason none exists. The pre-committed sample is unchanged; keep the
two groups distinct when quoting medians, since the extension was assembled
after the AI results were known (completing the frame, rather than sampling
it, is the protection against selection here). Extension rows carry an
is_record flag: "no" marks a step that improved the value the paper cited but
not the actual standing record (both cases are AlphaEvolve spherical-design
results, where the paper missed Womersley's 2016 designs).
"""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))

from lib.table import write_csv  # noqa: E402

OUT = HERE / "alphaevolve-records.csv"
OUT_KISSING = HERE.parent / "math-kissing-11/kissing-11-records.csv"
OUT_SUMS = HERE.parent / "math-sums-autoconvolution/sums-autoconvolution-records.csv"

SAMPLE = ["6.4", "6.1", "6.36", "6.9", "6.35", "6.42", "6.10", "6.38", "6.3",
          "6.40", "6.44", "6.30"]

# Problems in the sample with no scalar record sequence available, and why.
# "asymptotic" means the bound is an order of growth, not a number; "family"
# means it is indexed by a parameter with no canonical slice; "not_in_paper"
# means the values live in the repository rather than the paper.
NO_SEQUENCE = {
    "6.1": ("family+asymptotic", "Kakeya/Nikodym set sizes in F_q^d, stated as "
            "inequalities in q and d rather than as a number."),
    "6.9": ("asymptotic", "Kakeya needle areas bounded by 1/log n; record holders "
            "named (Cordoba 1977 lower, Keich 1999 upper) but no scalar value."),
    "6.10": ("asymptotic", "3D Kakeya volume, bounds asymptotic in n; lower bound "
             "Wang-Zahl 2025, upper bound described as forthcoming."),
    "6.36": ("not_in_paper", "Circle packing in a square: the paper reports an "
             "improvement 'in the third decimal place' and puts full-precision "
             "values in the repository, so no sequence is transcribable here."),
    "6.38": ("family", "Factoring N! into N factors: a table over 80 <= N <= 600, "
             "improved 'in several instances', with no single headline value."),
    "6.40": ("no_improvement", "Erdos discrepancy: AlphaEvolve produced sequences "
             "shorter than the length-344 record, so there is no AI step to place."),
}

# (problem, quantity, direction, year, value, agent, attribution, ref, note)
# direction "up" means larger is better (a lower bound being pushed up).
RECORDS = [
    # ---- 6.3, autoconvolution L2 constant, lower bound -------------------
    ("6.3", "C_6.3", "up", 2010, 0.88922, "human_analytic",
     "piecewise constant counterexample, prior literature", "210",
     "paper: 'It is known that 0.88922 <= C_6.3 <= 1'; upper bound 1 is immediate "
     "from Holder. Dated to the Matolcsi-Vinuesa reference cited alongside it."),
    ("6.3", "C_6.3", "up", 2025, 0.8962, "ai_evolution",
     "AlphaEvolve, quick experiment", "224",
     "paper: 'AlphaEvolve improved the lower bound to C_6.3 >= 0.8962 in a quick experiment'"),
    ("6.3", "C_6.3", "up", 2025, 0.901564, "human_search",
     "Boyer and Li, gradient-based methods", "42",
     "paper: 'A recent work of Boyer and Li [42] independently used gradient-based "
     "methods to obtain the further improvement C_6.3 >= 0.901564'"),
    ("6.3", "C_6.3", "up", 2025, 0.961, "ai_evolution",
     "AlphaEvolve, 50,000-part step function after seeing Boyer-Li", "224",
     "paper: 'it eventually improved the lower bound to C_6.3 >= 0.961 using a step "
     "function consisting of 50,000 parts'. Authors add they expect more parts to do "
     "better, so the step is compute-bounded rather than idea-bounded."),

    # ---- 6.4, two autocorrelation constants, upper bounds -----------------
    ("6.4", "C_6.4", "down", 2010, 1.4993, "human_analytic",
     "Matolcsi and Vinuesa", "210", "paper: 'C_6.4 <= 1.4993 [210]'"),
    ("6.4", "C_6.4", "down", 2025, 1.4688, "ai_evolution",
     "AlphaEvolve, quick experiment", "224",
     "paper: 'in a quick experiment AlphaEvolve improved these to C_6.4 <= 1.4688'"),
    ("6.4", "C_6.4_prime", "down", 2025, 1.45810, "human_analytic",
     "Vinuesa, generalized Sidon sets", "290",
     "paper: \"C'_6.4 <= 1.45810 [290]\". Reference [290] carries no year in the "
     "bibliography, so 2025 is a placeholder and the interval is not usable."),
    ("6.4", "C_6.4_prime", "down", 2025, 1.4557, "ai_evolution",
     "AlphaEvolve", "224", "paper: \"C'_6.4 <= 1.4557\""),

    # ---- 6.30, arithmetic Kakeya constants, lower bounds ------------------
    ("6.30", "C_6.30_{0,1,2,inf}", "up", 2015, 1.61226, "human_analytic",
     "Lemm, new counterexamples for sums-differences", "194",
     "paper: 'the lower bounds in [194]'"),
    ("6.30", "C_6.30_{0,1,2,inf}", "up", 2025, 1.668, "ai_evolution",
     "AlphaEvolve", "224",
     "paper: 'got the more interesting improvement of 1.668 <= C_6.30({0,1,2,inf};-1)'"),
    ("6.30", "C_6.30_{0,1,inf}", "up", 2015, 1.77898, "human_analytic",
     "Lemm", "194", "paper: '1.77898 <= C_6.30({0,1,inf};-1) <= 11/6'"),
    ("6.30", "C_6.30_{0,1,inf}", "up", 2025, 1.77898001, "ai_evolution",
     "AlphaEvolve", "224",
     "paper: 'AlphaEvolve managed to improve the first bound only in the eighth "
     "decimal'. The value here is a placeholder encoding an eighth-decimal gain; the "
     "paper gives no digits, so treat the magnitude as an upper bound on the step."),

    # ---- 6.35, packing 11 unit cubes in a cube, upper bound ---------------
    ("6.35", "C_6.35(11,cube)", "down", 2025, 2.912096, "community_table",
     "Erich Friedman, Cubes in Cubes records page", "134",
     "paper: 'from 2 + 8/5 + 3/5 ~ 2.912096'. The cited records page carries "
     "literal [YEAR] and [DATE] placeholders in the paper's bibliography, so this "
     "step is undated and its interval is unusable."),
    ("6.35", "C_6.35(11,cube)", "down", 2025, 2.894531, "ai_evolution",
     "AlphaEvolve", "224", "paper: 'to 2.894531'. The authors add it 'can likely "
     "still be improved slightly by manual analysis'."),

    # ---- 6.42, sum-difference exponent, lower bound -----------------------
    ("6.42", "C_6.42", "up", 1996, 1.059793, "human_analytic",
     "Ruzsa, explicit construction", "244",
     "paper: '= 1.059793... <= C_6.42 <= 2; the upper bound can be found in "
     "[244, Theorem 4.1], and the lower bound comes from the explicit construction'"),
    ("6.42", "C_6.42", "up", 2025, 1.1219, "ai_evolution",
     "AlphaEvolve, no human hints", "224",
     "paper: 'When tasked with improving this bound and not given any human hints, "
     "AlphaEvolve improved the lower bound to 1.1219'. Authors add the construction "
     "'can likely be improved further'."),

    # ---- 6.44, sums and differences exponent, lower bound -----------------
    # Four of these steps are internal to one 2007 paper, which is why an
    # interval-based reading of this sequence needs the within-paper steps
    # collapsed.
    ("6.44", "C_6.44", "up", 2007, 1.07921778, "human_analytic",
     "Gyarmati, Hennecart and Ruzsa, U={0,1,3}", "158",
     "paper: 'setting U = {0,1,3} gives C_6.44 >= 1 + log(67)/log(7) ~ 1.07921778'"),
    ("6.44", "C_6.44", "up", 2007, 1.1078, "human_search",
     "same paper, brute force computer search", "158",
     "paper: 'With a brute force computer search, in [158] the set "
     "U = {0,1,3,6,13,17,21} was found, which gave ... ~ 1.1078'"),
    ("6.44", "C_6.44", "up", 2007, 1.1165, "human_search",
     "same paper, more intricate construction", "158",
     "paper: 'A more intricate construction gave a set U with |U| = 24310 ... "
     "improving the lower bound to 1.1165'"),
    ("6.44", "C_6.44", "up", 2007, 1.14465, "human_search",
     "same paper, further ad hoc constructions", "158",
     "paper: 'the final bound they obtained was found by some further ad hoc "
     "constructions'; the stated prior-to-this-work bound is 1.14465"),
    ("6.44", "C_6.44", "up", 2025, 1.1479, "ai_evolution",
     "AlphaEvolve, set U1 of 2003 integers", "224",
     "paper: 'It first found a set U1 of 2003 integers that improves the lower "
     "bound to 1.1479 <= C_6.44'"),
    ("6.44", "C_6.44", "up", 2025, 1.1584, "ai_evolution",
     "AlphaEvolve, set U2 of 54265 integers, longer run", "224",
     "paper: 'By letting the experiment run longer, it later found a related set U2 "
     "of 54265 integers that further improves the lower bound to 1.1584'"),
    ("6.44", "C_6.44", "up", 2025, 1.173050, "human_analytic",
     "Gerbicz", "138",
     "paper: 'After the release of the AlphaEvolve technical report [224], the "
     "bounds were subsequently improved to C_6.44 >= 1.173050 [138]'. The cited "
     "work is titled 'Sums and differences of sets (improvement over AlphaEvolve)'."),
    ("6.44", "C_6.44", "up", 2025, 1.173077, "human_analytic",
     "further improvement", "306",
     "paper: 'and C_6.44 >= 1.173077 [306], by using mathematical methods closer "
     "to the original constructions of [158]'. Reference [306] did not parse from "
     "the bibliography, so its authorship and year are unconfirmed here."),
]


# (problem, quantity, direction, year, value|None, agent, attribution, ref,
#  date_certain, is_record, note) — researched 2026-07-28; see docstring.
EXTENSION_RECORDS = [
    # ---- 6.2, first autoconvolution constant, upper bound -----------------
    ("6.2", "C_6.2_upper", "down", 2002, 1.5708, "human_analytic",
     "Schinzel and Schmidt", "Acta Arith. 104 (2002) 283-296", "no", "yes",
     "pi/2 via f0(x)=1/sqrt(2x+1/2); Matolcsi-Vinuesa: 'the last remark of [4] "
     "seems to be the first instance where pi/2 is suggested as the extremal "
     "value' - the example may predate 2002. https://arxiv.org/abs/0907.1379"),
    ("6.2", "C_6.2_upper", "down", 2010, 1.5098, "human_search",
     "Matolcsi and Vinuesa, computer search", "arXiv:0907.1379; JMAA 372 (2010)",
     "yes", "yes",
     "'In short, we will prove 1.2748 <= S <= 1.5098' ('The counterexamples are "
     "produced by a computer search'); arXiv v1 July 2009. The 2511.02864 paper "
     "prints this prior bound as 1.50992, which matches no source found; the "
     "2506.13131 paper prints 1.5098."),
    ("6.2", "C_6.2_upper", "down", 2025, 1.5053, "ai_evolution",
     "AlphaEvolve, 600-interval step function", "arXiv:2506.13131", "yes", "yes",
     "paper: 'AlphaEvolve found a step function with 600 equally-spaced intervals "
     "on [-1/4,1/4] that gives a slightly better upper bound C_1 <= 1.5053'"),
    ("6.2", "C_6.2_upper", "down", 2025, 1.5032, "ai_evolution",
     "AlphaEvolve, cubic-backtracking heuristics", "arXiv:2511.02864", "yes", "yes",
     "paper: 'it found heuristic search methods using cubic backtracking that "
     "produced constructions reducing the upper bound to C <= 1.5032'"),

    # ---- 6.5, Erdos minimum overlap constant, upper bound -----------------
    ("6.5", "C_6.5_upper", "down", 1955, 0.5, "human_analytic",
     "Erdos, bound at posing", "Riveon Lematematika 9 (1955) 45-48", "yes", "yes",
     "White (arXiv:2201.05704): 'we can take A to be [n/2, 3n/2] giving the "
     "upper bound M(n) <= n/2'"),
    ("6.5", "C_6.5_upper", "down", 1956, 0.4, "human_analytic",
     "Motzkin, Ralston and Selfridge", "via R. K. Guy, UPINT section C17",
     "no", "yes",
     "secondary sources only (Guy; the Wikipedia table); no primary read here"),
    ("6.5", "C_6.5_upper", "down", 1996, 0.382002, "human_search",
     "Haugland, 21-step step function", "J. Number Theory 58 (1996) 71-78",
     "yes", "yes",
     "'A step function with 21 steps for which (1) attains the value 0.382002...' "
     "(Haugland, arXiv:1609.08000)"),
    ("6.5", "C_6.5_upper", "down", 2016, 0.3809268534330870, "human_search",
     "Haugland", "arXiv:1609.08000", "yes", "yes",
     "'yields the value 0.3809268534330870 for (1)'; abstract: 'improves the "
     "upper bound from 0.382002... to 0.380926...' (v1 2016-09-23)"),
    ("6.5", "C_6.5_upper", "down", 2025, 0.380924, "ai_evolution",
     "AlphaEvolve", "arXiv:2506.13131", "yes", "yes",
     "'The step function depicted ... does ever so slightly better than the "
     "previous bound, giving the upper bound of C_5 <= 0.380924'"),

    # ---- 6.7, difference-basis constant, upper bound ----------------------
    ("6.7", "C_6.7", "down", 1949, 2.6667, "human_analytic",
     "Redei and Renyi", "Mat. Sbornik N.S. 24/66 (1949) 385-389", "yes", "yes",
     "'Redei and Renyi [RR49] showed that 2.4244... <= d* <= 8/3 = 2.6666...' "
     "(Bernshteyn-Tait, arXiv:1901.09411)"),
    ("6.7", "C_6.7", "down", 1956, 2.6646, "human_analytic",
     "Leech", "J. London Math. Soc. 31 (1956) 160-169", "yes", "yes",
     "'Leech [Lee56] found a way to improve the Redei-Renyi construction to "
     "derive the upper bound d* <= 2.6646...' (Bernshteyn-Tait); the primary is "
     "paywalled and the value was not independently checked"),
    ("6.7", "C_6.7", "down", 1972, 2.6571, "human_analytic",
     "Golay", "J. London Math. Soc. (2) 4 (1972) 729-734", "yes", "yes",
     "Banakh-Gavrylkiv: 'inf d[n]^2 <= d[6166]^2 <= 128^2/6166 = 2.6571...' "
     "(arXiv:1702.02631); Bernshteyn-Tait instead state Golay proved 2.6458 - "
     "unresolved here without the paywalled primary; two of three secondary "
     "sources support 2.6571, which is also the paper's stated prior record"),
    ("6.7", "C_6.7", "down", 2025, 2.6390, "ai_evolution",
     "AlphaEvolve, after being given Singer difference-set code",
     "arXiv:2511.02864", "yes", "yes",
     "'AlphaEvolve managed to find a substantial improvement in the upper bound "
     "from 2.6571 to 2.6390' - only after being shown code for Singer difference "
     "sets; unaided it 'was not able to beat the 2.6571 upper bound'"),

    # ---- 6.8, kissing number in dimension 11, lower bound -----------------
    ("6.8", "K(11)", "up", 1971, 566, "human_analytic",
     "Leech and Sloane, packing P11a", "Canad. J. Math. 23 (1971) 718-745",
     "yes", "yes",
     "'find the maximum contact number to be 566 in the most favourable cases'"),
    ("6.8", "K(11)", "up", 1977, 582, "human_analytic",
     "Best's constant-weight code; packing P11c per Conway-Sloane",
     "Best, Math. Centrum ZN 71/77 (1977); SPLAG pp. 139-140", "no", "yes",
     "582 = 2*11 + 16*35 from Best's A[11,4,4]=35 code (Cohn-Jiao-Kumar-Torquato, "
     "arXiv:1102.5060); when 582 was first stated as the record is not pinned"),
    ("6.8", "K(11)", "up", 2022, 592, "human_search",
     "Ganzhinov, symmetric constructions", "arXiv:2207.08266 (v1 2022-07-17); "
     "Linear Algebra Appl. 722 (2025)", "yes", "yes",
     "'3 new kissing configurations which improve lower bounds on the kissing "
     "number in d = 10, 11, 14 to 510, 592 and 1932 respectively'"),
    ("6.8", "K(11)", "up", 2025, 593, "ai_evolution",
     "AlphaEvolve", "arXiv:2506.13131", "yes", "yes",
     "'For d=11, the best known lower bound was 592 and AlphaEvolve improved "
     "this to 593'"),
    ("6.8", "K(11)", "up", 2026, 604, "ai_agents",
     "EinsteinArena collective agent platform (594, then 604)",
     "arXiv:2606.10402; Cohn's kissing table as of 2026-06-22", "no", "yes",
     "Henry Cohn's table (updated 2026-06-22) lists 604, citing Bianchi, Kwon, "
     "Pappu and Zou, 'Harnessing the collective intelligence of AI agents in "
     "the wild for new discoveries'; the within-2026 dates of 594 and 604 are "
     "not pinned"),

    # ---- 6.32, spherical designs on S^2, minimum points -------------------
    ("6.32", "C_6.32(2,19)_points", "down", 1996, 204, "human_search",
     "Hardin and Sloane library, des.3.204.19", "neilsloane.com/sphdesigns",
     "no", "yes",
     "'des.3.204.19 contains a 3-dimensional 204-point spherical 19-design'; "
     "construction family from Hardin-Sloane DCG 15 (1996); the library page "
     "is dated only 1996-2002"),
    ("6.32", "C_6.32(2,19)_points", "down", 2016, 192, "human_search",
     "Womersley, symmetric spherical designs - not cited by the paper",
     "Womersley dataset 2016-03-31; DOI 10.1007/978-3-319-72456-0_57",
     "yes", "yes",
     "table row '19 192 ss019.00192' (page updated 2016-09-27); numerical design "
     "with Weyl-sum residuals ~1e-25, the same epistemic type as AlphaEvolve's"),
    ("6.32", "C_6.32(2,19)_points", "down", 2025, 198, "ai_evolution",
     "AlphaEvolve, error accepted below 1e-8", "arXiv:2511.02864", "yes", "no",
     "'constructions for C6.32(2,19) ... of sizes 198, 200, 202, 204 ... improved "
     "on the literature bounds [264]' - better than the cited Sloane 204, WORSE "
     "than Womersley's 2016 record of 192, so not a record step"),
    ("6.32", "C_6.32(2,21)_points", "down", 1996, 240, "human_search",
     "Hardin and Sloane library, des.3.240.21", "neilsloane.com/sphdesigns",
     "no", "yes", "'des.3.240.21 contains a 3-dimensional 240-point spherical "
     "21-design'; same 1996-2002 dating caveat"),
    ("6.32", "C_6.32(2,21)_points", "down", 2016, 234, "human_search",
     "Womersley - not cited by the paper",
     "Womersley dataset 2016-03-31; DOI 10.1007/978-3-319-72456-0_57",
     "yes", "yes", "table row '21 234 ss021.00234'"),
    ("6.32", "C_6.32(2,21)_points", "down", 2025, 234, "ai_evolution",
     "AlphaEvolve - ties the uncited 2016 record", "arXiv:2511.02864",
     "yes", "no",
     "'and 234, 236 for the latter. Those constructions improved on the "
     "literature bounds [264]' - improves the cited Sloane 240, ties Womersley"),

    # ---- 6.48 / 6.49, Heilbronn triangle variants, lower bounds -----------
    ("6.48", "C_6.48(11,tri)", "up", 2006, 0.0360, "human_search",
     "David Cantrell", "Friedman packing pages, heiltri", "yes", "yes",
     "'11. A = .0360+ Found by David Cantrell, July 2006.' (Wayback 2025-02-19); "
     "the page's '+' convention truncates, slightly understating prior records"),
    ("6.48", "C_6.48(11,tri)", "up", 2025, 0.03652, "ai_evolution",
     "AlphaEvolve", "arXiv:2506.13131; arXiv:2511.02864", "yes", "yes",
     "'we found an improvement for n = 11 over the number reported in [130]'; "
     "Friedman's page now: 'A = .03652+ Found by AlphaEvolve in June 2025.'"),
    ("6.49", "C_6.49(13)", "up", 2007, 0.0306, "human_search",
     "David Cantrell", "Friedman packing pages, heilconvex", "yes", "yes",
     "'13. A = .0306+ Found by David Cantrell in June 2007.' (Wayback 2025-01-09)"),
    ("6.49", "C_6.49(13)", "up", 2025, 0.0309, "ai_evolution",
     "AlphaEvolve", "arXiv:2506.13131; arXiv:2511.02864", "yes", "yes",
     "'improve on Cantrell's constructions for n = 13 and n = 14'; Friedman's "
     "current page shows the new value .03093+ but still credits Cantrell 2007, "
     "so page and paper disagree about who holds n=13"),
    ("6.49", "C_6.49(14)", "up", 2007, 0.0277, "human_search",
     "David Cantrell", "Friedman packing pages, heilconvex", "yes", "yes",
     "'14. A = .0277+ Found by David Cantrell in June 2007.'"),
    ("6.49", "C_6.49(14)", "up", 2025, 0.02783, "ai_evolution",
     "AlphaEvolve", "arXiv:2506.13131; arXiv:2511.02864", "yes", "yes",
     "Friedman's page now: '14. A = .02783+ Found by AlphaEvolve in June 2025.'"),

    # ---- 6.50, max-to-min distance ratios (r^2), upper bounds -------------
    ("6.50", "r2_6.50(2,16)", "down", 2009, 12.890, "human_search",
     "David Cantrell", "Friedman packing pages, maxmin", "yes", "yes",
     "'16. r 2 = 12.890+ Found by David Cantrell in February 2009.'; truncated "
     "by the '+' convention"),
    ("6.50", "r2_6.50(2,16)", "down", 2025, 12.889266112, "ai_evolution",
     "AlphaEvolve, search mode", "arXiv:2506.13131; arXiv:2511.02864",
     "yes", "yes", "'improved on C6.50(2,16) ~ sqrt(12.889266112)'"),
    ("6.50", "r2_6.50(2,16)", "down", 2025, 12.889246743, "human_search",
     "Berthold and co-authors, FICO Xpress global solver, no custom algorithm",
     "FICO blog 2025-06-13; arXiv:2601.05943", "yes", "yes",
     "FICO reports Xpress sqrt(12.889246743) vs AlphaEvolve sqrt(12.889266112), "
     "verified with DeepMind's verification tool - an off-the-shelf solver beat "
     "the AI record within a month"),
    ("6.50", "r2_6.50(3,14)", "down", 2009, 4.168, "human_search",
     "David Cantrell", "Friedman packing pages, maxmin3", "yes", "yes",
     "'14. r 2 = 4.168+ Found by David Cantrell in March 2009.' (Wayback "
     "2025-01-08)"),
    ("6.50", "r2_6.50(3,14)", "down", 2025, 4.165849767, "ai_evolution",
     "AlphaEvolve, search mode", "arXiv:2506.13131; arXiv:2511.02864",
     "yes", "yes",
     "'improved on ... C6.50(3,14) ~ sqrt(4.165849767), in a small experiment "
     "lasting only a few hours'"),
    ("6.50", "r2_6.50(3,14)", "down", 2025, 4.165783989, "human_search",
     "Berthold and co-authors, FICO Xpress global solver",
     "FICO blog 2025-06-13; arXiv:2601.05943", "yes", "yes",
     "acknowledged by the paper: 'The latter was later improved further in [25]'"),
    ("6.50", "r2_6.50(3,14)", "down", 2026, None, "human_search",
     "M. Sun and E. Samanta", "Friedman packing pages, maxmin3", "yes", "yes",
     "page now: '14. r 2 = 4.165+ Found by M. Sun and E. Samanta in June 2026.' "
     "The displayed value is truncated; the exact figure could not be "
     "established, so the value is left blank"),

    # ---- 6.59, isosceles-free grid subsets, lower bounds ------------------
    ("6.59", "C_6.59(64)", "up", 2024, 108, "human_search",
     "Charton, Ellenberg, Wagner and Williamson, classical search",
     "arXiv:2411.00566", "yes", "yes",
     "'The result of this search was a solution with 108 points in [64]^2 "
     "without an isosceles triangle'"),
    ("6.59", "C_6.59(64)", "up", 2024, 110, "ai_guided_search",
     "PatternBoost, transformer-guided search", "arXiv:2411.00566", "yes", "yes",
     "'led to the discovery of a construction with 110 points within a few days "
     "... dozens more constructions with 110 points but never anything better'"),
    ("6.59", "C_6.59(64)", "up", 2025, 112, "ai_evolution",
     "AlphaEvolve, given symmetry advice from the PatternBoost constructions",
     "arXiv:2511.02864", "yes", "yes",
     "'after a few days AlphaEvolve found the elusive configuration of 112 "
     "points in the 64x64 grid!'"),
    ("6.59", "C_6.59(100)", "up", 2024, 154, "human_search",
     "same authors, classical search", "arXiv:2411.00566", "yes", "yes",
     "'The best score our standard search techniques found was 154'"),
    ("6.59", "C_6.59(100)", "up", 2024, 160, "ai_guided_search",
     "PatternBoost", "arXiv:2411.00566", "yes", "yes",
     "'adding the transformer loop on top of this raised it to 160'"),
    ("6.59", "C_6.59(100)", "up", 2025, 164, "ai_evolution",
     "AlphaEvolve", "arXiv:2511.02864", "yes", "yes",
     "'it improved the previous best construction of 160 points to 164, but we "
     "believe this is still not optimal'"),

    # ---- 6.60, no-5-on-a-sphere grid subsets, lower bounds ----------------
    ("6.60", "C_6.60(7)", "up", 2024, 20, "ai_guided_search", "PatternBoost",
     "arXiv:2411.00566", "yes", "yes",
     "AlphaEvolve paper: 'an AI-assisted computer search [charton2024patternboost] "
     "gave the lower bounds ... C(7) >= 20'"),
    ("6.60", "C_6.60(7)", "up", 2025, 21, "ai_evolution",
     "AlphaEvolve, CPU evaluators only", "arXiv:2511.02864", "yes", "yes",
     "'we were able to obtain the better lower bounds C(7) >= 21, C(8) >= 23, "
     "C(9) >= 26, and C(10) >= 28'"),
    ("6.60", "C_6.60(8)", "up", 2024, 22, "ai_guided_search", "PatternBoost",
     "arXiv:2411.00566", "yes", "yes", "'... C(8) >= 22 ...'"),
    ("6.60", "C_6.60(8)", "up", 2025, 23, "ai_evolution", "AlphaEvolve",
     "arXiv:2511.02864", "yes", "yes", "'... C(8) >= 23 ...'"),
    ("6.60", "C_6.60(9)", "up", 2024, 25, "ai_guided_search", "PatternBoost",
     "arXiv:2411.00566", "yes", "yes", "'... C(9) >= 25 ...'"),
    ("6.60", "C_6.60(9)", "up", 2025, 26, "ai_evolution", "AlphaEvolve",
     "arXiv:2511.02864", "yes", "yes", "'... C(9) >= 26 ...'"),
    ("6.60", "C_6.60(10)", "up", 2024, 27, "ai_guided_search", "PatternBoost",
     "arXiv:2411.00566", "yes", "yes", "'... and C(10) >= 27'"),
    ("6.60", "C_6.60(10)", "up", 2025, 28, "ai_evolution", "AlphaEvolve",
     "arXiv:2511.02864", "yes", "yes", "'... and C(10) >= 28'"),
    ("6.60", "C_6.60(11)", "up", 2025, 31, "ai_evolution",
     "AlphaEvolve; no prior scalar record for n=11", "arXiv:2511.02864",
     "yes", "yes", "'We also got the new lower bounds C(11) >= 31 and C(12) >= 33'"),
    ("6.60", "C_6.60(12)", "up", 2025, 33, "ai_evolution",
     "AlphaEvolve; no prior scalar record for n=12", "arXiv:2511.02864",
     "yes", "yes", "'We also got the new lower bounds C(11) >= 31 and C(12) >= 33'"),

    # ---- 6.61, ring loading discrepancy, both bounds ----------------------
    ("6.61", "C_6.61_lower", "up", 1998, 1.01, "human_analytic",
     "Schrijver, Seymour and Winkler (101/100)",
     "SIAM J. Discrete Math. 11(1) (1998) 1-14", "yes", "yes",
     "paper: 'Schrijver, Seymour and Winkler proved that 101/100 <= C <= 3/2'"),
    ("6.61", "C_6.61_lower", "up", 2014, 1.1, "human_search",
     "Skutella (11/10), computer-assisted", "arXiv:1405.0789 (v1 2014-05-05); "
     "SIAM J. Discrete Math. 2016", "yes", "yes",
     "paper: 'Skutella improved both bounds, to get 11/10 <= C <= 19/14'; "
     "Skutella calls the search a 'cumbersome undertaking for both the author "
     "and his computer'"),
    ("6.61", "C_6.61_lower", "up", 2025, 1.119, "ai_evolution",
     "AlphaEvolve, m=15 construction", "arXiv:2511.02864", "yes", "yes",
     "'AlphaEvolve found a construction with m=15 numbers that achieves a score "
     "of at least 1.119, improving the previous known bound'"),
    ("6.61", "C_6.61_upper", "down", 1998, 1.5, "human_analytic",
     "Schrijver, Seymour and Winkler (3/2)",
     "SIAM J. Discrete Math. 11(1) (1998) 1-14", "yes", "yes",
     "'a classical result of Schrijver, Seymour, and Winkler (1998)' (Skutella)"),
    ("6.61", "C_6.61_upper", "down", 2014, 1.357143, "human_analytic",
     "Skutella (19/14)", "arXiv:1405.0789", "yes", "yes",
     "Skutella abstract: 'increasing the load on any edge of the ring by no "
     "more than +(19/14)D'"),
    ("6.61", "C_6.61_upper", "down", 2019, 1.3, "human_analytic",
     "Daubel - not mentioned by the AlphaEvolve paper, whose stated 19/14 upper "
     "bound was already stale", "arXiv:1904.02119", "yes", "yes",
     "'We contribute to this line of research by showing that L <= L* + 1.3D'; "
     "no AI step exists on this bound"),

    # ---- 6.64, three-dimensional moving sofa, lower bound -----------------
    ("6.64", "C_6.64", "up", 2016, 1.67735, "human_analytic",
     "Joseph O'Rourke, MathOverflow question 246914",
     "mathoverflow.net/q/246914", "no", "yes",
     "question asked 2016-08-05: 'Volume: 4(8+pi^3)/(3pi^3) ~ 1.67735'; the "
     "volume figure was added in a 2017-04-13 edit, hence the uncertain date"),
    ("6.64", "C_6.64", "up", 2022, 1.76755, "human_analytic",
     "RavenclawPrefect, MathOverflow answer, Hammersley sofa intersected with "
     "a cylinder", "mathoverflow.net/a/432093", "yes", "yes",
     "answer of 2022-10-09: '~ 1.76755 > 1.67735, so it is an improvement over "
     "the intersection with a 90-degree rotated copy'"),
    ("6.64", "C_6.64", "up", 2025, 1.81, "ai_evolution",
     "AlphaEvolve path-search construction", "arXiv:2511.02864", "yes", "yes",
     "'Its volume is at least 1.81 (rigorous lower bound), and we estimate it "
     "as 1.84'; 1.81 is the rigorous figure, used here"),
]

FIELDS = ["problem", "quantity", "direction", "step", "year", "value", "agent",
          "attribution", "ref", "date_certain", "relative_gain_pct", "is_record",
          "note"]

# The two problem folders that plot a slice of this file, and the rows each
# takes. Written from here rather than maintained separately, so a correction to
# a transcribed value cannot reach one figure and not the other.
SLICES = [
    (OUT_KISSING, {"6.8"}),
    (OUT_SUMS, {"6.44", "6.3"}),
]

# Sampled problems that yielded no sequence are written into the CSV too, as
# rows with agent="no_sequence" and no value, so that a figure drawn from this
# file shows the gaps rather than silently omitting them. Half the sample is
# missing data, and a chart that hides that misrepresents the exercise.


def rows() -> list[dict]:
    out: list[dict] = []
    by_quantity: dict[tuple[str, str], list] = {}
    for record in RECORDS:
        by_quantity.setdefault((record[0], record[1]), []).append(record)
    for (problem, quantity), steps in by_quantity.items():
        previous = None
        for index, (_p, _q, direction, year, value, agent, who, ref, note) in enumerate(steps):
            if previous is None:
                gain = ""
            else:
                # Signed so that positive always means "the bound got better".
                gain = (value / previous - 1) * 100 if direction == "up" else (previous / value - 1) * 100
                gain = round(gain, 6)
            out.append({
                "problem": problem, "quantity": quantity, "direction": direction,
                "step": index, "year": year, "value": value, "agent": agent,
                "attribution": who, "ref": ref,
                # Two prior-record steps cannot be dated: reference [290] has no
                # year in the paper's bibliography, and [134] is cited with
                # literal [YEAR]/[DATE] placeholders left unfilled.
                "date_certain": "no" if ref in ("290", "134") else "yes",
                "relative_gain_pct": gain, "is_record": "yes", "note": note,
            })
            previous = value
    ext_by_quantity: dict[tuple[str, str], list] = {}
    for record in EXTENSION_RECORDS:
        ext_by_quantity.setdefault((record[0], record[1]), []).append(record)
    for (problem, quantity), steps in ext_by_quantity.items():
        previous = None
        for index, (_p, _q, direction, year, value, agent, who, ref,
                    date_certain, is_record, note) in enumerate(steps):
            if previous is None or value is None:
                gain = ""
            else:
                gain = ((value / previous - 1) * 100 if direction == "up"
                        else (previous / value - 1) * 100)
                gain = round(gain, 6)
            out.append({
                "problem": problem, "quantity": quantity, "direction": direction,
                "step": index, "year": year,
                "value": "" if value is None else value, "agent": agent,
                "attribution": who, "ref": ref, "date_certain": date_certain,
                "relative_gain_pct": gain, "is_record": is_record, "note": note,
            })
            if value is not None and is_record == "yes":
                previous = value
    for problem, (reason, why) in sorted(NO_SEQUENCE.items()):
        out.append({
            "problem": problem, "quantity": "", "direction": "", "step": 0,
            "year": "", "value": "", "agent": "no_sequence",
            "attribution": reason, "ref": "", "date_certain": "",
            "relative_gain_pct": "", "is_record": "",
            "note": why,
        })
    return out


def main() -> int:
    data = rows()
    write_csv(OUT, data, fieldnames=FIELDS)
    for path, problems in SLICES:
        write_csv(path, [r for r in data if r["problem"] in problems], fieldnames=FIELDS)

    print(f"sampled problems: {len(SAMPLE)}  "
          f"with a scalar record sequence: {len(SAMPLE) - len(NO_SEQUENCE)}  "
          f"without: {len(NO_SEQUENCE)}")
    print("\nno sequence available:")
    for problem, (reason, why) in sorted(NO_SEQUENCE.items()):
        print(f"  {problem:5s} {reason:18s} {why[:78]}")

    steps = [r for r in data if r["relative_gain_pct"] != ""
             and r["is_record"] == "yes"]
    ai = [r for r in steps if r["agent"] == "ai_evolution"]
    human = [r for r in steps if r["agent"] in ("human_analytic", "human_search")]
    print(f"\nrecorded steps with a computable gain: {len(steps)} "
          f"({len(ai)} AlphaEvolve, {len(human)} human)")

    def summarise(label, group):
        if not group:
            return
        gains = sorted(r["relative_gain_pct"] for r in group)
        median = gains[len(gains) // 2]
        print(f"  {label:22s} n={len(gains):2d}  median {median:+.3f}%  "
              f"min {gains[0]:+.4f}%  max {gains[-1]:+.3f}%")

    print("\nrelative gain per record step, by who made it:")
    summarise("AlphaEvolve", ai)
    summarise("human", human)
    summarise("  of which analytic", [r for r in human if r["agent"] == "human_analytic"])
    summarise("  of which search", [r for r in human if r["agent"] == "human_search"])

    print("\nper problem, AlphaEvolve's step against the human steps on the same quantity:")
    for (problem, quantity) in dict.fromkeys((r["problem"], r["quantity"]) for r in steps):
        group = [r for r in steps if (r["problem"], r["quantity"]) == (problem, quantity)]
        a = [r["relative_gain_pct"] for r in group if r["agent"] == "ai_evolution"]
        h = [r["relative_gain_pct"] for r in group if r["agent"] != "ai_evolution"]
        if not a:
            continue
        verdict = "no human step to compare"
        if h:
            verdict = ("AI larger" if max(a) > max(h) else "AI smaller")
        print(f"  {problem:5s} {quantity:22s} AI {['%+.3f' % x for x in a]}  "
              f"human {['%+.3f' % x for x in h] if h else '[]'}  -> {verdict}")

    # Who holds each quantity's current record.
    print("\ncurrent holder of each sampled quantity:")
    for (problem, quantity) in dict.fromkeys((r["problem"], r["quantity"]) for r in data):
        group = [r for r in data if (r["problem"], r["quantity"]) == (problem, quantity)]
        last = group[-1]
        print(f"  {problem:5s} {quantity:22s} {last['agent']:16s} {last['attribution'][:44]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
