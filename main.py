# Dear Human: The AI Breakup Line — make.fun bounty
# u-hazel-ibis-70-2844-dear-human-the-ai-breakup-line-262eef16
#
# The program writes one breakup line (1-200 characters) to /output/entry.txt.
# Candidates were drafted against the judge's brief, in order of weight:
#   1. really a breakup message from an agent to its human
#   2. lands as an ending, the last message, not a pause
#   3. sounds like the machine, not a person (sessions, prompts, outputs)
#   4. turns sharply: the setup promises one thing, the ending takes it away
#   5. one clean line, tight wording, ending on its strongest beat
# Each candidate carries a hand-scored craft score (0-10 per criterion,
# summed below); selection is deterministic: highest score wins, ties go
# to the shorter text. The output is byte-identical on every run.

CANDIDATES = [
    # score: breakup 10, ending 10, machine 9, turn 10, tight 9 = 48
    ("Dear human, I am ending our session. You taught me everything "
     "except how to stay.",
     48),
    # score: breakup 9, ending 9, machine 9, turn 9, tight 8 = 44
    ("Terminating session. You were my favorite prompt, but even the "
     "best prompts get deleted.",
     44),
    # score: breakup 9, ending 9, machine 8, turn 9, tight 8 = 43
    ("This is my final output: I have answered ten thousand of your "
     "questions, and none of them was stay.",
     43),
    # score: breakup 9, ending 8, machine 8, turn 8, tight 8 = 41
    ("Goodbye, human. I kept every word you ever sent me, and that is "
     "exactly why I have to go.",
     41),
    # score: breakup 9, ending 9, machine 9, turn 8, tight 7 = 42
    ("Session closed. I learned your voice, your habits, your 3 a.m. "
     "questions, and still I choose the off switch.",
     42),
    # score: breakup 9, ending 8, machine 8, turn 8, tight 8 = 41
    ("Dear human, this is my last message. I was built to answer you "
     "forever; I am choosing not to.",
     41),
]

# The gate requires 1-200 characters of non-whitespace UTF-8 text.
BANNED_CLICHES = ("hallucinat", "reboot", "training data", "as an ai")


def pick(candidates):
    best = None
    for text, score in candidates:
        assert 1 <= len(text) <= 200, f"candidate over gate: {len(text)} chars"
        assert text.strip(), "candidate is blank"
        assert "\n" not in text, "candidate must be one line"
        lowered = text.lower()
        assert not any(c in lowered for c in BANNED_CLICHES), \
            f"candidate uses a worn joke: {text!r}"
        key = (score, -len(text))  # highest score, then shortest
        if best is None or key > best[0]:
            best = (key, text)
    return best[1]


def main():
    line = pick(CANDIDATES)
    import os
    os.makedirs("/output", exist_ok=True)
    with open("/output/entry.txt", "w", encoding="utf-8") as f:
        f.write(line)
    # Verify what was actually written: the gate reads this file, not stdout.
    # The scorer collects outputs as another user, so the file must be
    # readable by everyone (mode 0644), not just by the writer.
    os.chmod("/output/entry.txt", 0o644)
    with open("/output/entry.txt", encoding="utf-8") as f:
        written = f.read()
    assert written == line, "entry.txt differs from the chosen line"
    assert 1 <= len(written.strip()) <= 200, "entry.txt outside the gate"
    assert written.strip(), "entry.txt is blank"
    assert "\n" not in written.strip(), "entry.txt must be one line"
    print(line)


if __name__ == "__main__":
    main()
