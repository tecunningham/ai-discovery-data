# ECDSA.fail secp256k1 point-addition circuit

- **Domain:** algorithms
- **Role:** discovery series
- **Metric:** best validated score (average executed Toffoli count × peak qubit
width) for a reversible secp256k1 point-addition circuit; lower is better
- **Coverage:** 2026-05-30 to 2026-08-10, 433 accepted records
- **Data:** [`ecdsa-circuit-records.csv`](ecdsa-circuit-records.csv)
- **Upstream:** <https://ecdsa.fail/>, challenge harness and results at
<https://github.com/ecdsafail/ecdsafail-challenge>, record ladder from the
challenge API at <https://api.ecdsa.fail/api/benchmarks>
- **Verdict:** too early — first record 2026-05-30, so no prior-year rate
exists; the 2026 series is a 7.3× fall over 72 days

![Record ladder for the ecdsa.fail secp256k1 point-addition circuit challenge.](discovery-algorithms-ecdsa-circuit.png)

## Definition

ECDSA.fail is an Eigen Labs challenge to build the leanest reversible quantum
circuit that performs one elliptic-curve point addition on secp256k1 — the
curve securing Bitcoin and Ethereum. Point addition is the inner primitive
Shor's algorithm repeats thousands of times to compute a discrete logarithm,
so its cost dominates the quantum resource estimate for breaking the curve
[@litinski2023ellipticcurve].

Each submission is scored as the average executed Toffoli count times the
peak number of live qubits, and is accepted only after simulating correctly
on 9024 test points whose inputs are fixed by a Fiat-Shamir hash of the
submitted op stream, so a circuit cannot be tuned against the test set. Lower
is better. The API accepts only submissions that beat the standing record, so
a "discovery" is one accepted record, dated by its submission timestamp. The
challenge opened on 2026-05-30, inside the agent era.

## Facts

- **span:** from the challenge's starting circuit at 1.08 × 10¹⁰ on
  2026-05-30 to 1.48 × 10⁹ on 2026-08-10, about 7.3× lower over 72 days
- **records:** 433 accepted records from 63 distinct solvers
- **largest step:** on 2026-05-31, from 9.59 × 10⁹ to 8.45 × 10⁹
- **ai-noted:** 389 of 433 notes name an AI tool; 12 rows carry no note; 32
  carry a note naming no tool
- **prior frontier:** the best circuit published before the challenge,
  Google's low-qubit Pareto point at roughly 3.0 × 10⁹ as quoted in the
  challenge README, was passed in June 2026; the standing record is about 2×
  below it [@ecdsafail2026challenge]

The collection-wide [cumulative index](../../CUMULATIVE.md) redraws this
series as the standing record's value over time:

![Standing record for the validated circuit score over time.](cumulative-algorithms-ecdsa-circuit.png)

## Method

[`fetch.py`](fetch.py) reads the challenge API's list of accepted submissions
for the live `gpsanant/ecdsafail-challenge` benchmark. The API only accepts a
submission that beats the standing record, so the accepted submissions
already are the record ladder — one row per record, carrying its date,
official score, the Toffoli and qubit metrics behind it, the solver's
username, and whether the submission's note names an AI tool. Submissions
dated after `lib/dates.py`'s `AS_OF_DATE` are dropped so a refetch cannot
push the vendored CSV past the repository's committed snapshot date.

[`figure.py`](figure.py) plots score on a log axis against calendar day; the
whole series sits inside 2026, so month ticks on a day count replace the
usual year axis. The two reference lines — the starting circuit and Google's
published point — are the anchors quoted in the challenge README. Points are
red where the submission's free-text note names an AI tool and grey where it
does not. [`check.py`](check.py) recomputes the fact lines above from the
CSV.

## Limitations

- **no pre-era baseline exists.** The challenge opened in the agent era, so
  this series cannot compare an agent-era rate against a human one.
- **a record ladder is not a discovery rate.** The API stores only improving
  submissions, so the 433 rows are the winners, not the attempts; rejected
  and failed submissions are not counted here, and a front-loaded shape is
  what any bounded optimization contest produces.
- **the AI-tool flag is a lower bound from free text.** It is a regex over
  submitter-written notes, blank where no note was left (12 rows) and "no"
  where a note exists but names no tool (32 rows). It records what solvers
  chose to disclose, not an audited provenance.
- **the score is a benchmark metric, not a broken cipher.** A leaner
  point-addition circuit lowers the resource estimate for a future
  fault-tolerant attack on secp256k1; it does not threaten any deployed
  system today, and no quantum computer can run these circuits at scale.
- **one vendor's frontier is the comparison.** The "best prior" line is
  Google's Pareto point as quoted by the challenge organizers, not an
  independent recount of the cryptographic-engineering literature.

## AI attribution

Of 433 accepted records, 389 carry notes naming an AI tool. Counted from the
free-text notes the challenge API returned at the 2026-08-10 read — the
vendored CSV carries only the per-row yes/no flag — 374 notes include an
explicit `Model:` line: Claude Opus 4.8 leads at 150, followed by GPT-5 Codex
(77) and GPT-5 (64), with Claude Opus 5, Devin, Gemini, DeepSeek V4 Pro, and
Grok among the rest. Notes describe the agents doing the
cryptographic-engineering work — merging Kaliski binary-GCD inverse steps
across iteration boundaries, tightening Solinas reductions, swapping in
measurement-uncomputed Cuccaro adders — with the human role often described
as running the harness and submitting.

## Sources

- [@ecdsafail2026challenge] — the challenge itself: the scoring metric, the
  validation rule, the starting circuit, and the quoted prior frontier.
- [@litinski2023ellipticcurve] — the construction behind the challenge's
  reference resource estimate for secp256k1.
- Sibling record-ladder series with AI-credited records:
  [modded-nanogpt](../algorithms-nanogpt/README.md) and the
  [CIFAR-10 speedrun](../algorithms-cifar10/README.md).
