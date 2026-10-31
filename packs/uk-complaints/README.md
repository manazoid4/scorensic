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
uv run scorensic check packs/uk-complaints/pack.csv --model <your-model>
```

**Contents:** 54 tasks from 10 complaints and non-complaints. All of them are **invented for testing**; none is real customer data. Deadlines are calculated by `build.py` (received date + 8 weeks), not typed in by hand.

**Checks on the pack itself:**
- The marking rejects all 342 trick answers.
- An independent model review (DeepSeek V4.1 Flash) found every label unambiguous.
- A second model (Big Pickle) recomputed all 8 deadlines.

**Limits (v0.1):**
- Only 10 messages, so this is too small to rank models finely.
- Drafting the actual response letter is not tested yet. That needs a different kind of marking (must-include and must-not-say rules), which is next.
- "Business days" deadlines (DISP 1.5 and the payment-services rules) are not included yet.
- This is not legal or compliance advice.
