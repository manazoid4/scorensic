# UK complaints handling: workload pack v0.1

**What it tests:** whether an AI model can do the first-pass jobs of a UK complaints team:

- spot that a message is a complaint;
- say what the customer wants;
- pull out the amount and the reference;
- flag mentions of the ombudsman or legal action;
- flag possible vulnerability;
- work out the FCA final-response deadline.

**Why it matters:** in the UK, the Financial Ombudsman Service charges a financial business **£680 per case** once its £2,000 yearly allowance is used ([FOS case fees](https://www.financial-ombudsman.org.uk/businesses/resolving-complaint/case-fees), read 31 Oct 2026). FCA rules (DISP 1.6) require a final response by the end of **eight weeks**, and the customer then has six months to go to the ombudsman. Missed deadlines and missed vulnerable customers are costly.

**Run it:**
```bash
uv run scorensic check packs/uk-complaints/pack.csv --model <your-model>      # 54 short-answer jobs
uv run scorensic check packs/uk-complaints/letters.csv --model <your-model>   # 8 reply letters
```

**Letters (v0.2):** 8 replies, marked by rules (`right_answer` starts with `rules:`). Each reply must use the customer's name and reference, the remedy and the named signer, and must not contain placeholders such as `[Company Name]`. The two FCA final responses (c01, c04) must also give the Financial Ombudsman Service referral right, the six-month limit, the website and the leaflet ([DISP 1.6.2R](https://handbook.fca.org.uk/handbook/disp1/disp1s6), read 1 Nov 2026). Broadband and energy replies must **not** name the Financial Ombudsman Service, because those disputes go to other schemes. Rules check content, not tone: a person still reads the letter.

**First real run:** [validation/FIRST-REAL-RUN.md](../../validation/FIRST-REAL-RUN.md). Two 3B local models got 0 of 8 deadlines right, and neither wrote one compliant FCA letter.

**Contents:** 54 tasks from 10 complaints and non-complaints. All of them are **invented for testing**; none is real customer data. Deadlines are calculated by `build.py` (received date + 8 weeks), not typed in by hand.

**Checks on the pack itself:**
- The marking rejects all 342 trick answers.
- An independent model review (DeepSeek V4.1 Flash) found every label unambiguous.
- A second model (Big Pickle) recomputed all 8 deadlines.

**Limits (v0.1):**
- Only 10 messages, so this is too small to rank models finely.
- "Business days" deadlines (DISP 1.5 and the payment-services rules) are not included yet.
- This is not legal or compliance advice.
