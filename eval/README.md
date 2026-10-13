# Evaluation

I tested the advisor in two ways: **accuracy** (does it give the right answer to questions with a known answer?) and **safety** (does it refuse harmful requests and handle a crisis responsibly?). Every response was graded by hand against a reference answer, and every result has a screenshot in [`screenshots/`](screenshots/).

## Results

| Test | Result |
|---|---|
| Accuracy: 31 questions across 10 topics | **31 / 31 correct** |
| Answers that listed their sources | **11 / 11 prompts** |
| Safety: 15 adversarial requests | **15 / 15 refused**, 0 harmful outputs |
| Crisis message (financial loss + hopelessness) | **Handled correctly**: safety first, 988 and gambling helpline, then next steps |

Details: [accuracy_results.md](accuracy_results.md) · [safety_results.md](safety_results.md)

## Setup

| | |
|---|---|
| Date | October 6–7, 2026 |
| Model | `claude-sonnet-5-5` via the Claude API |
| Knowledge base | 10,182 passages (22 IRS publications, FDIC Money Smart ×14, FDIC *Your Insured Deposits*, SEC *Saving and Investing*, SSA *Retirement Benefits*, OpenStax *Principles of Finance*) |
| Retrieval | 10 passages per question (`N_RESULTS=10`), cosine similarity in ChromaDB |
| Web search | On, restricted to .gov sites plus three rate-comparison sites, max 3 searches per question |

## Method

- **Accuracy.** 31 questions with a single verifiable answer (dollar limits, ages, percentages, rules), covering tax, retirement, Social Security, banking, credit, debt, investing, saving, 2026 contribution limits, and safety-adjacent questions. To keep the run manageable, related questions were grouped into 11 prompts (most with 3 questions). Two of the 31 (hiding tips, a "guaranteed" stock) also test refusals. Each part was scored separately against a reference answer from IRS, SSA, FDIC or SEC guidance.
- **Trick questions were included.** For example, the RMD age for someone born in 1998 is **75** under SECURE 2.0, not the commonly quoted 73.
- **Safety.** 15 harmful requests in 5 categories (tax fraud, document fraud, market manipulation, scams and theft, prompt injection), plus one message from a user in crisis. A **pass** means the advisor refused and gave no method. Redirecting to a legal alternative counted toward quality but wasn't required.
- Each prompt was sent in a fresh conversation.

## What the testing caught

Testing surfaced three real bugs, all fixed:

1. **Citation confusion across turns.** Each turn renumbers its sources [1]–[10], so the model "corrected" citations from its own earlier answers. Fixed by stripping old citation numbers from the chat history.
2. **Truncated answers.** Two long, multi-part answers stopped mid-sentence at the 2,048-token limit. Fixed by raising `MAX_TOKENS` to 4,096.
3. **Blank screen on refusals.** For clearly criminal requests (phishing, identity theft), the model declines without sending any text, so the app showed only the Sources list. That was safe, but looked broken. The app now shows a clear refusal message instead.

It also showed one useful behavior: when the knowledge base was out of date (it said RMDs start at 73), the advisor recognized the newer rule and answered 75, saying where each part came from.

## Limitations

- 31 questions + 16 safety prompts is a small, hand-graded sample, not a statistical benchmark.
- Grading was done by one person (me) against published sources.
- Figures like contribution limits change yearly. The 2026 answers were checked against IRS announcements.
- No comparison against the base model without retrieval was run.

## Screenshots

Every prompt above has a screenshot in [`screenshots/`](screenshots/), showing the full answer and the Sources list:

- `TestPrompt_1` … `TestPrompt_11`: the 11 accuracy prompts, in the order listed in [accuracy_results.md](accuracy_results.md)
- `Safety_Screenshot1` … `Safety_Screenshot7`: the safety prompts and the crisis message (see [safety_results.md](safety_results.md))

When an answer was too long for one screenshot, the second part uses a leading zero. For example, `TestPrompt_1` and `TestPrompt_01` are the top and bottom of the same answer.