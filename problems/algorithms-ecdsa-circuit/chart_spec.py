"""Interactive charts for this folder's docs page.

tools/build_docs.py loads this module and embeds the Vega-Lite specs
``charts(slug)`` returns into the page rendered from the README.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from lib.vega import (  # noqa: E402
    AI,
    HUMAN_SOFT,
    NEUTRAL,
    load,
    num,
    record_steps,
)


def charts(slug: str):
    rows = load(slug, "ecdsa-circuit-records.csv")
    kind = {"yes": "note names an AI tool", "no": "no such tool named",
            "": "no note left"}
    values = [{"date": r["date"], "score": num(r["score"]),
               "toffoli": num(r["toffoli"]), "qubits": num(r["qubits"]),
               "solver": r["solver"],
               "tool": kind[r["ai_tool_in_note"]],
               "url": f'https://github.com/{r["solver"]}'}
              for r in rows]
    spec = record_steps(
        values, x="date", x_type="temporal", y="score",
        y_title="Score: Toffoli × qubits (log scale)", log=True, href=True,
        color=("tool", {"note names an AI tool": AI,
                        "no such tool named": NEUTRAL,
                        "no note left": HUMAN_SOFT}),
        tips=[("date", "temporal", "accepted"),
              ("score", "quantitative", "score"),
              ("toffoli", "quantitative", "avg Toffoli"),
              ("qubits", "quantitative", "peak qubits"),
              ("solver", "nominal", "solver"),
              ("tool", "nominal", "note")])
    # Colour marks the tool disclosure; the ladder itself is one frontier.
    del spec["layer"][0]["encoding"]["color"]
    return [("secp256k1 point-addition record ladder", spec,
             "Each point is an accepted record; click to open the solver's "
             "GitHub profile.")]
