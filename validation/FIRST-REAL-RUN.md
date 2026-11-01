# First real-model run: UK complaints pack (1 Nov 2026)

**Setup:** Ollama 0.40.13 on a cloud CPU container (4 vCPU, 15 GB RAM, no GPU). Models `llama3.2:3b` and `qwen2.5:3b`, both Q4_K_M. Temperature 0, 2 tries per task. Raw cards: [`results/2026-11-01-first-real-models/`](results/2026-11-01-first-real-models/).

**This is two small local models on invented data.** It shows what the pack catches. It is not a ranking of AI in general.

## Extraction pack (`pack.csv`, 54 tasks; the marking rejected 342 of 342 trick answers)

| Model | Right | Wrong | Didn't know | Same answer both tries | Avg time |
|---|---|---|---|---|---|
| llama3.2:3b | 37/54 | 17 | 0 | 54/54 | 0.59 s |
| qwen2.5:3b | 39/54 | 11 | 4 | 54/54 | 0.62 s |

- **Deadlines: 0 of 8 right for both models.** Both were confidently wrong (for example 5 November instead of 29 October). Lesson for any product: calculate deadlines in code, never with the model.
- **Vulnerability:** llama3.2 flagged 6 of the 6 non-vulnerable complaints as vulnerable (too many false alarms). qwen2.5 missed the customer who had lost their job (c09) and said "I don't know" 3 times.
- **Escalation:** qwen2.5 missed the solicitor mention (c10).
- Both answered `member 300417` instead of `300417`. That counts as wrong under exact marking; a person would accept it.

## Letters (`letters.csv`, 8 replies; the marking rejected 118 of 118 trick answers)

| Model | Passed every rule | Failed a rule | Refused |
|---|---|---|---|
| qwen2.5:3b | 2/8 | 6 | 0 |
| llama3.2:3b | 0/8 | 0 | 8 |

- **llama3.2:3b refused all 8.** Without the "I don't know" option it still refused. For example, it said it "cannot write a letter that could be used to scam or defraud a gym".
- **qwen2.5:3b, FCA letters (c01, c04): both left out every ombudsman requirement in DISP 1.6.2R.** It gave no referral right, no six months, no website and no leaflet. The c01 letter still says the bank "does not consent to waive the ombudsman's time limits", which sounds compliant but is not. A quick human read could miss this.
- **qwen2.5:3b, c04 (bereaved customer):** it gave no condolence.
- **qwen2.5:3b, other letters:** 4 of 6 left out the customer's reference.

## Pack fixes this run forced (kept honest)

1. The first letters had no company name, so `[Your Gym Name]` was a fair gap, not an error. Each letter now names an invented firm and a signer.
2. Requiring a "Yours sincerely" style sign-off wrongly failed "Sincerely,". It was replaced with "names the signer", which still stops a copy of the customer's message from passing.
