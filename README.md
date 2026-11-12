[README.md](https://github.com/user-attachments/files/34739918/README.md)
# AI-Powered Agentic Workflow for Project Management

An agentic system that turns a raw product specification into a complete,
evaluated development plan — user stories, product features, and engineering
tasks — with no human in the loop beyond the initial prompt.

Built as a pilot for a fictional startup, **InnovateNext Solutions**, using their
upcoming **Email Router** product spec as the test case. The same toolkit and
workflow are reusable for any future product spec.

## What it does

Given a one-line request like:

> "Produce a complete project plan for the Email Router product, including user
> stories, product features, and engineering tasks."

the system:

1. **Plans** — breaks the request down into a sequence of concrete sub-tasks
   (identify personas, define actions, write user stories, group into features,
   break stories into engineering tasks, compile the final plan).
2. **Routes** — for each sub-task, picks the right specialist (Product Manager,
   Program Manager, or Development Engineer) by comparing the embedding of the
   sub-task against each specialist's description.
3. **Generates & evaluates** — each specialist drafts an answer, then a
   dedicated evaluator checks it against a strict format (e.g. "As a [user], I
   want [action] so that [benefit]") and sends it back for correction until it
   passes, or a maximum number of attempts is reached.
4. **Assembles** — all the accepted outputs are compiled into one consolidated
   plan, grouped into User Stories, Product Features, and Engineering Tasks.

## Architecture

The project is split into two phases:

### Phase 1 — Agent toolkit (`phase_1/`)

A small, reusable library of agent classes (`workflow_agents/base_agents.py`),
each wrapping a different interaction pattern with an LLM:

| Agent | Purpose |
|---|---|
| `DirectPromptAgent` | Plain pass-through to the LLM — no persona, no extra context. |
| `AugmentedPromptAgent` | Adds a persona via a system prompt. |
| `KnowledgeAugmentedPromptAgent` | Adds a persona **and** forces answers to come only from a supplied knowledge string, not the model's own training data. |
| `RAGKnowledgePromptAgent` | Retrieval-augmented variant: chunks a large text, embeds the chunks, and answers from whichever chunk is most relevant to the question. |
| `EvaluationAgent` | Wraps a worker agent in a generate → critique → correct loop until its output meets a given criteria (or a max number of iterations is hit). |
| `RoutingAgent` | Picks the best agent for a prompt by cosine similarity between the prompt's embedding and each candidate agent's description. |
| `ActionPlanningAgent` | Breaks a high-level goal into an ordered list of concrete steps. |

Each class has a standalone test script (e.g. `routing_agent.py`,
`evaluation_agent.py`) with its own sample output saved under
`output_*.txt`.

### Phase 2 — The project management workflow (`phase_2/`)

`agentic_workflow.py` wires four of those agents together into the actual
pilot:

- An `ActionPlanningAgent` turns the TPM's prompt into an ordered list of steps.
- A `RoutingAgent` sends each step to one of three simulated teams:
  - **Product Manager** team — `KnowledgeAugmentedPromptAgent` (grounded in the
    full Email Router product spec) + `EvaluationAgent` enforcing the user
    story format.
  - **Program Manager** team — groups related stories into features, with an
    `EvaluationAgent` enforcing the feature format (Name / Description / Key
    Functionality / User Benefit).
  - **Development Engineer** team — breaks stories into engineering tasks, with
    an `EvaluationAgent` enforcing the task format (Task ID / Title / Related
    Story / Description / Acceptance Criteria / Estimated Effort /
    Dependencies).
- The validated output of every step is assembled into one consolidated,
  clearly-sectioned project plan.

Input: [`Product-Spec-Email-Router.txt`](phase_2/Product-Spec-Email-Router.txt)
Output: [`phase_2/output_agentic_workflow.txt`](phase_2/output_agentic_workflow.txt)

## Project structure

```
phase_1/
├── workflow_agents/
│   └── base_agents.py          # all 7 agent classes
├── direct_prompt_agent.py
├── augmented_prompt_agent.py
├── knowledge_augmented_prompt_agent.py
├── rag_knowledge_prompt_agent.py
├── evaluation_agent.py
├── routing_agent.py
├── action_planning_agent.py
└── output_*.txt                # saved run output for each script above

phase_2/
├── workflow_agents/
│   └── base_agents.py          # same library, used by the workflow
├── agentic_workflow.py         # orchestrates the full pilot
├── Product-Spec-Email-Router.txt
└── output_agentic_workflow.txt # saved run output
```

## Running it

Each agent calls the OpenAI API (`gpt-4.1-mini` for completions,
`text-embedding-3-large` for the routing agent's embeddings), so you'll need an
API key.

```bash
pip install -r requirements.txt   # pandas, openai, python-dotenv, numpy

# create a .env file in phase_1/ (and again in phase_2/) containing:
# OPENAI_API_KEY=your_key_here

cd phase_1
python direct_prompt_agent.py
python augmented_prompt_agent.py
python knowledge_augmented_prompt_agent.py
python rag_knowledge_prompt_agent.py
python evaluation_agent.py
python routing_agent.py
python action_planning_agent.py

cd ../phase_2
python agentic_workflow.py
```

## Why this design

The interesting part isn't any single LLM call — it's the **separation of
concerns between generation and verification**. Every worker agent is paired
with an evaluator that doesn't trust the first answer; it checks the output
against an explicit structural contract and bounces it back for revision when
it doesn't match. That's what makes the pipeline's output consistent enough to
hand to a routing layer and chain into a larger plan, instead of a one-shot
answer you'd have to manually clean up.

This project was built as part of Udacity's Agentic AI course.
