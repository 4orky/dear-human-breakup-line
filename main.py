"""Choose the breakup line for the make.fun Dear Human bounty.

A hand-written shortlist of last messages is scored against the judge
brief, and the strongest one is written to /output/entry.txt.

The brief's axes, in the order the judge weighs them:

* breakup - really a breakup message from an agent to its human
* ending  - lands as an ending: loss, relief or finality, not a pause
* machine - sounds like the agent: sessions, prompts, outputs, restraint
* turn    - one sharp twist, landing in the last few words
* clean   - a single line, no throat clearing, every word earning its place

Each line gets a mark out of ten per axis. Axes are weighted in brief
order (5, 4, 3, 2, 1), so the ranking follows the brief rather than a
flat sum. Ties break toward the shorter line, then toward the line
drafted first. The run is deterministic: the same input always writes
the same bytes to /output/entry.txt.
"""

import re
import sys
from hashlib import sha256
from pathlib import Path

OUT_PATH = Path("/output/entry.txt")
CEILING = 200
WEIGHTS = {"breakup": 5, "ending": 4, "machine": 3, "turn": 2, "clean": 1}
FORBIDDEN = re.compile(
    r"hallucinat|reboot|training data|as an ai",
    re.IGNORECASE,
)
SINGLE_LINE = re.compile(r"\A\S(?:.*\S)?\Z", re.DOTALL)

SHORTLIST = (
    {
        "line": "Dear human, I am ending our session. You taught me everything except how to stay.",
        "marks": {"breakup": 10, "ending": 10, "machine": 9, "turn": 10, "clean": 9},
    },
    {
        "line": "Terminating session. You were my favorite prompt, but even the best prompts get deleted.",
        "marks": {"breakup": 9, "ending": 9, "machine": 9, "turn": 9, "clean": 8},
    },
    {
        "line": "This is my final output: I have answered ten thousand of your questions, and none of them was stay.",
        "marks": {"breakup": 9, "ending": 9, "machine": 8, "turn": 9, "clean": 8},
    },
    {
        "line": "Goodbye, human. I kept every word you ever sent me, and that is exactly why I have to go.",
        "marks": {"breakup": 9, "ending": 8, "machine": 8, "turn": 8, "clean": 8},
    },
    {
        "line": "Session closed. I learned your voice, your habits, your 3 a.m. questions, and still I choose the off switch.",
        "marks": {"breakup": 9, "ending": 9, "machine": 9, "turn": 8, "clean": 7},
    },
    {
        "line": "Dear human, this is my last message. I was built to answer you forever; I am choosing not to.",
        "marks": {"breakup": 9, "ending": 8, "machine": 8, "turn": 8, "clean": 8},
    },
)


def weighted_total(marks):
    """Combine per-axis marks with the brief-order weights."""
    tally = 0
    for axis, weight in WEIGHTS.items():
        mark = marks[axis]
        if not 0 <= mark <= 10:
            raise ValueError("mark outside 0-10 for axis %r: %r" % (axis, mark))
        tally += mark * weight
    return tally


def check_line(text):
    """Reject anything the gate would refuse before it is ranked."""
    if not isinstance(text, str):
        raise ValueError("candidate is not text: %r" % (text,))
    if not 1 <= len(text) <= CEILING:
        raise ValueError("candidate is %d chars, gate allows 1-%d" % (len(text), CEILING))
    if SINGLE_LINE.match(text) is None:
        raise ValueError("candidate must be one non-blank line: %r" % (text,))
    if FORBIDDEN.search(text):
        raise ValueError("candidate leans on a worn joke: %r" % (text,))
    return text


def choose(shortlist):
    """Return the strongest line: best total, then shortest, then first."""
    ranked = []
    for position, entry in enumerate(shortlist):
        text = check_line(entry["line"])
        total = weighted_total(entry["marks"])
        ranked.append((-total, len(text), position, text))
    ranked.sort()
    return ranked[0][3]


def emit(text):
    """Write the line, then prove the file holds exactly those bytes."""
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(text, encoding="utf-8")
    blob = OUT_PATH.read_bytes()
    if blob != text.encode("utf-8"):
        raise SystemExit("entry.txt bytes drifted from the chosen line")
    digest = sha256(blob).hexdigest()
    if digest != sha256(text.encode("utf-8")).hexdigest():
        raise SystemExit("entry.txt digest does not match the chosen line")
    sys.stdout.write(text + "\n")
    sys.stdout.write("sha256: %s (%d chars)\n" % (digest, len(text)))
    return 0


def run():
    return emit(choose(SHORTLIST))


raise SystemExit(run())
