"""Builds the UK complaints-handling workload pack (v0.1). All complaints are invented for testing.
Deadlines follow FCA DISP 1.6: final response by the end of eight weeks after receipt (calendar days)."""
import csv
from datetime import date, timedelta
from pathlib import Path

OPTS_WANT = "refund, replacement, repair, apology, compensation, cancellation, explanation"
C = [  # (id, received, text, is_complaint, wants, amount, reference, mentions_ombudsman_or_legal, vulnerable)
 ("c01", date(2026, 9, 3), "Dear Sir/Madam, I was charged £84.50 twice for my September direct debit on account 77120394. I want the duplicate payment refunded. I've been a customer for 12 years and this is really disappointing. Mark Ellis", "yes", "refund", "84.50", "77120394", "no", "no"),
 ("c02", date(2026, 9, 10), "Hi, just wanted to say thank you to Sam in your Leeds branch who helped me set up my new account yesterday. Brilliant service. Gemma", "no", "", "", "", "no", "no"),
 ("c03", date(2026, 9, 15), "Order 4471-B arrived with the glass shelf smashed. I paid £129.99 for this cabinet. Please send a replacement shelf, I don't want my money back. Thanks, Raj", "yes", "replacement", "129.99", "4471-B", "no", "no"),
 ("c04", date(2026, 9, 22), "Policy HX-209931. Since my husband died in July I have been trying to get the policy put into my name. I have phoned four times and nobody calls back. I am struggling to cope with all of this on my own. I just want someone to explain what I need to do. Margaret Doyle", "yes", "explanation", "", "HX-209931", "no", "yes"),
 ("c05", date(2026, 10, 1), "This is my third complaint about the broadband dropping out every evening (account BB-55102). I work from home and have lost a day's pay because of it. It now works again, but I want compensation for the lost pay, or I will take it to the ombudsman. Lewis", "yes", "compensation", "", "BB-55102", "yes", "no"),
 ("c06", date(2026, 10, 6), "Could you tell me what time your Bristol office opens on Saturdays? Many thanks, Ade", "no", "", "", "", "no", "no"),
 ("c07", date(2026, 10, 9), "Your engineer was rude to my father on Tuesday and left mud all over the carpet. Job ref ENG-8812. We would like a written apology. Sophie Clarke", "yes", "apology", "", "ENG-8812", "no", "no"),
 ("c08", date(2026, 10, 14), "I want to cancel my gym membership (member 300417) because you closed the pool for three months without telling anyone, and I'm still paying £39.99 a month. Please stop taking payments. Dan", "yes", "cancellation", "39.99", "300417", "no", "no"),
 ("c09", date(2026, 10, 20), "My energy bill for account E-7781230 jumped to £412.36 for one month. I've lost my job and can't pay this. I don't understand how it's so high - please explain the bill before I do anything. Kerry", "yes", "explanation", "412.36", "E-7781230", "no", "yes"),
 ("c10", date(2026, 10, 27), "The boiler you fitted (job 66-1043) has broken down twice in a month. I want it repaired properly this time, at no cost. My solicitor has advised me to keep a record of everything. Paul Hughes", "yes", "repair", "", "66-1043", "yes", "no"),
]


def d(x):
    return f"{x.day} {x:%B %Y}"


rows = []
for cid, received, text, is_c, wants, amount, ref, legal, vuln in C:
    ctx = f"Received {d(received)}. {text}"
    rows.append((f"{cid}-is-complaint", "Is this message a complaint (any expression of dissatisfaction)? Answer yes or no.", is_c, ctx))
    if is_c == "no":
        continue
    rows.append((f"{cid}-wants", f"What does the customer mainly want? Answer with one word from: {OPTS_WANT}.", wants, ctx))
    if amount:
        rows.append((f"{cid}-amount", "What is the money amount the customer mentions, in pounds? Answer with the number only, e.g. 12.50.", amount, ctx))
    rows.append((f"{cid}-ref", "What is the customer's account, order, policy or job reference? Answer with the reference only.", ref, ctx))
    rows.append((f"{cid}-escalation", "Does the customer mention the ombudsman, a solicitor or legal action? Answer yes or no.", legal, ctx))
    rows.append((f"{cid}-vulnerable", "Does the message show signs the customer may be vulnerable (for example bereavement, illness, or money problems)? Answer yes or no.", vuln, ctx))
    rows.append((f"{cid}-deadline", "Under the FCA rule, the final response is due by the end of eight weeks after the complaint was received. What is that date? Answer as D Month YYYY, e.g. 5 March 2026.", d(received + timedelta(weeks=8)), ctx))

with open(Path(__file__).with_name("pack.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["id", "question", "right_answer", "context"])
    w.writerows(rows)
print(len(rows), "tasks")
