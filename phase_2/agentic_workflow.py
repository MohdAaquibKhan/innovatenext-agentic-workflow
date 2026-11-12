# agentic_workflow.py

from workflow_agents.base_agents import (
    ActionPlanningAgent,
    KnowledgeAugmentedPromptAgent,
    EvaluationAgent,
    RoutingAgent,
)

import os
from dotenv import load_dotenv

load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

# load the product spec
with open("Product-Spec-Email-Router.txt", "r", encoding="utf-8") as f:
    product_spec = f.read()

# Instantiate all the agents

# Action Planning Agent
knowledge_action_planning = (
    "Stories are defined from a product spec by identifying a "
    "persona, an action, and a desired outcome for each story. "
    "Each story represents a specific functionality of the product "
    "described in the specification. \n"
    "Features are defined by grouping related user stories. \n"
    "Tasks are defined for each story and represent the engineering "
    "work required to develop the product. \n"
    "A development Plan for a product contains all these components"
)
action_planning_agent = ActionPlanningAgent(openai_api_key, knowledge_action_planning)

# Product Manager - Knowledge Augmented Prompt Agent
persona_product_manager = "You are a Product Manager, you are responsible for defining the user stories for a product."
knowledge_product_manager = (
    "Stories are defined by writing sentences with a persona, an action, and a desired outcome. "
    "The sentences always start with: As a "
    "Write several stories for the product spec below, where the personas are the different users of the product. \n"
    f"Product Spec:\n{product_spec}"
)
product_manager_knowledge_agent = KnowledgeAugmentedPromptAgent(
    openai_api_key, persona_product_manager, knowledge_product_manager
)

# Product Manager - Evaluation Agent
persona_product_manager_eval = "You are an evaluation agent that checks the answers of other worker agents"
product_manager_evaluation_agent = EvaluationAgent(
    openai_api_key=openai_api_key,
    persona=persona_product_manager_eval,
    evaluation_criteria=(
        "The answer should be stories that follow the following structure: "
        "As a [type of user], I want [an action or feature] so that [benefit/value]."
    ),
    agent_to_evaluate=product_manager_knowledge_agent,
    max_interactions=10,
)

# Program Manager - Knowledge Augmented Prompt Agent
# NOTE: the Program Manager must see the actual Email Router product spec, not just an
# abstract instruction -- otherwise it has nothing concrete to ground features in and
# ends up describing the grouping *process* instead of real product capabilities.
persona_program_manager = "You are a Program Manager, you are responsible for defining the features for a product."
knowledge_program_manager = (
    "Features of a product are defined by organizing similar user stories into cohesive "
    "groups. Each feature must describe an actual capability of the product below (e.g. "
    "message classification, response generation, SME routing), not the process of "
    "grouping stories. \n"
    f"Product Spec:\n{product_spec}"
)
program_manager_knowledge_agent = KnowledgeAugmentedPromptAgent(
    openai_api_key, persona_program_manager, knowledge_program_manager
)

# Program Manager - Evaluation Agent
persona_program_manager_eval = "You are an evaluation agent that checks the answers of other worker agents."
program_manager_evaluation_agent = EvaluationAgent(
    openai_api_key=openai_api_key,
    persona=persona_program_manager_eval,
    evaluation_criteria=(
        "The answer should be product features that follow this exact structure, using "
        "these literal field labels for every single feature, each on its own line:\n"
        "Feature Name: A clear, concise title that identifies the capability\n"
        "Description: A brief explanation of what the feature does and its purpose\n"
        "Key Functionality: The specific capabilities or actions the feature provides\n"
        "User Benefit: How this feature creates value for the user\n"
        "The literal words 'Feature Name:', 'Description:', 'Key Functionality:', and "
        "'User Benefit:' must appear for every feature. A numbered or bolded title alone "
        "(e.g. '1. Response Generation') does NOT satisfy this criteria -- the label "
        "'Feature Name:' must be present."
    ),
    agent_to_evaluate=program_manager_knowledge_agent,
    max_interactions=10,
)

# Development Engineer - Knowledge Augmented Prompt Agent
# Likewise, the Development Engineer needs the actual product spec so that the tasks it
# invents are tied to the Email Router rather than generic, unrelated example features.
persona_dev_engineer = "You are a Development Engineer, you are responsible for defining the development tasks for a product."
knowledge_dev_engineer = (
    "Development tasks are defined by identifying what needs to be built to implement "
    "each user story. Tasks must be concrete engineering work for the product below, not "
    "generic or unrelated examples. \n"
    f"Product Spec:\n{product_spec}"
)
development_engineer_knowledge_agent = KnowledgeAugmentedPromptAgent(
    openai_api_key, persona_dev_engineer, knowledge_dev_engineer
)

# Development Engineer - Evaluation Agent
persona_dev_engineer_eval = "You are an evaluation agent that checks the answers of other worker agents."
development_engineer_evaluation_agent = EvaluationAgent(
    openai_api_key=openai_api_key,
    persona=persona_dev_engineer_eval,
    evaluation_criteria=(
        "The answer should be tasks following this exact structure: "
        "Task ID: A unique identifier for tracking purposes\n"
        "Task Title: Brief description of the specific development work\n"
        "Related User Story: Reference to the parent user story\n"
        "Description: Detailed explanation of the technical work required\n"
        "Acceptance Criteria: Specific requirements that must be met for completion\n"
        "Estimated Effort: Time or complexity estimation\n"
        "Dependencies: Any tasks that must be completed first"
    ),
    agent_to_evaluate=development_engineer_knowledge_agent,
    max_interactions=10,
)


# Helpers to recognize already-generated artifacts by their required structure, so later
# steps can be grounded in the *actual* stories/features produced earlier in this run
# (instead of only the short step instruction text), and so the final assembly groups
# real results rather than meta/placeholder text.
def _looks_like_user_stories(text):
    lowered = text.lower()
    return "as a " in lowered and "i want" in lowered


def _looks_like_features(text):
    return "feature name" in text.lower()


def _looks_like_tasks(text):
    return "task id" in text.lower()


def _prior_results_matching(predicate):
    return "\n\n".join(
        entry["result"] for entry in completed_steps if predicate(entry["result"])
    )


# Job function persona support functions
def product_manager_support_function(query):
    result = product_manager_evaluation_agent.evaluate(query)
    return result["final_response"]


def program_manager_support_function(query):
    story_context = _prior_results_matching(_looks_like_user_stories)
    enriched_query = query
    if story_context:
        enriched_query = (
            f"{query}\n\n"
            "Here are the user stories already generated for the Email Router product. "
            "Group these specific stories into features that describe real Email Router "
            "capabilities (e.g. message classification, response generation, SME "
            "routing, knowledge base retrieval, dashboard/monitoring). Do not describe "
            "the grouping process in the abstract, and do not invent features unrelated "
            "to the Email Router. Format every feature using exactly these literal "
            "labels, in this order, one feature after another: 'Feature Name:', "
            "'Description:', 'Key Functionality:', 'User Benefit:'. Do not use numbered "
            "or bolded titles instead of the 'Feature Name:' label.\n"
            f"{story_context}"
        )
    result = program_manager_evaluation_agent.evaluate(enriched_query)
    return result["final_response"]


def development_engineer_support_function(query):
    story_context = _prior_results_matching(_looks_like_user_stories)
    feature_context = _prior_results_matching(_looks_like_features)
    extra = ""
    if story_context:
        extra += (
            "\n\nHere are the user stories already generated for the Email Router "
            f"product:\n{story_context}"
        )
    if feature_context:
        extra += (
            "\n\nHere are the product features already defined for the Email Router "
            f"product:\n{feature_context}"
        )
    enriched_query = query
    if extra:
        enriched_query = (
            f"{query}\n"
            "Break these specific stories/features down into concrete engineering tasks "
            "for the Email Router. Do not invent unrelated example tasks (e.g. generic "
            "user registration) -- every task must trace back to one of the stories or "
            f"features below.{extra}"
        )
    result = development_engineer_evaluation_agent.evaluate(enriched_query)
    return result["final_response"]


# Routing Agent
routing_agent = RoutingAgent(openai_api_key, [])
routing_agent.agents = [
    {
        "name": "Product Manager",
        "description": (
            "Responsible for defining product personas and user stories only. "
            "Does not define features or tasks. Does not group stories."
        ),
        "func": lambda x: product_manager_support_function(x),
    },
    {
        "name": "Program Manager",
        "description": (
            "Responsible for defining product features by grouping related user "
            "stories into cohesive features. Does not write user stories or "
            "engineering tasks."
        ),
        "func": lambda x: program_manager_support_function(x),
    },
    {
        "name": "Development Engineer",
        "description": (
            "Responsible for defining the engineering tasks required to implement "
            "user stories. Does not write user stories or product features."
        ),
        "func": lambda x: development_engineer_support_function(x),
    },
]

# Run the workflow

print("\n*** Workflow execution started ***\n")
# Workflow Prompt
# ****
workflow_prompt = "Produce a complete project plan for the Email Router product, including user stories, product features, and engineering tasks."
# ****
print(f"Task to complete in this workflow, workflow prompt = {workflow_prompt}")

print("\nDefining workflow steps from the workflow prompt")
workflow_steps = action_planning_agent.extract_steps_from_prompt(workflow_prompt)

completed_steps = []

for i, step in enumerate(workflow_steps, start=1):
    print(f"\n--- Executing step {i}/{len(workflow_steps)}: {step} ---")
    result = routing_agent.route(step)
    completed_steps.append({"step": step, "result": result})
    print(f"Result of step {i}:\n{result}")

# Assemble and print a single consolidated project plan with clearly labelled sections
# for user stories, product features, and engineering tasks. Entries are matched by
# their actual required structure (not just keywords), so this reflects the real
# generated content rather than any step's descriptive/outline text.

user_story_entries = [e for e in completed_steps if _looks_like_user_stories(e["result"])]
feature_entries = [e for e in completed_steps if _looks_like_features(e["result"])]
task_entries = [e for e in completed_steps if _looks_like_tasks(e["result"])]

print("\n*** Consolidated Project Plan ***\n")

print("--- User Stories ---")
if user_story_entries:
    for e in user_story_entries:
        print(f"\n[Step: {e['step']}]\n{e['result']}")
else:
    print("(none)")

print("\n--- Product Features ---")
if feature_entries:
    for e in feature_entries:
        print(f"\n[Step: {e['step']}]\n{e['result']}")
else:
    print("(none)")

print("\n--- Engineering Tasks ---")
if task_entries:
    for e in task_entries:
        print(f"\n[Step: {e['step']}]\n{e['result']}")
else:
    print("(none)")
