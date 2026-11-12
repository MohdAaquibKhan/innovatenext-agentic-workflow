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
persona_program_manager = "You are a Program Manager, you are responsible for defining the features for a product."
knowledge_program_manager = "Features of a product are defined by organizing similar user stories into cohesive groups."
program_manager_knowledge_agent = KnowledgeAugmentedPromptAgent(
    openai_api_key, persona_program_manager, knowledge_program_manager
)

# Program Manager - Evaluation Agent
persona_program_manager_eval = "You are an evaluation agent that checks the answers of other worker agents."
program_manager_evaluation_agent = EvaluationAgent(
    openai_api_key=openai_api_key,
    persona=persona_program_manager_eval,
    evaluation_criteria=(
        "The answer should be product features that follow the following structure: "
        "Feature Name: A clear, concise title that identifies the capability\n"
        "Description: A brief explanation of what the feature does and its purpose\n"
        "Key Functionality: The specific capabilities or actions the feature provides\n"
        "User Benefit: How this feature creates value for the user"
    ),
    agent_to_evaluate=program_manager_knowledge_agent,
    max_interactions=10,
)

# Development Engineer - Knowledge Augmented Prompt Agent
persona_dev_engineer = "You are a Development Engineer, you are responsible for defining the development tasks for a product."
knowledge_dev_engineer = "Development tasks are defined by identifying what needs to be built to implement each user story."
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


# Job function persona support functions
def product_manager_support_function(query):
    result = product_manager_evaluation_agent.evaluate(query)
    return result["final_response"]


def program_manager_support_function(query):
    result = program_manager_evaluation_agent.evaluate(query)
    return result["final_response"]


def development_engineer_support_function(query):
    result = development_engineer_evaluation_agent.evaluate(query)
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

# Assemble and print a single consolidated project plan with clearly labelled
# sections for user stories, product features, and engineering tasks.


def _belongs_to(entry, keywords):
    haystack = (entry["step"] + " " + entry["result"]).lower()
    return any(keyword in haystack for keyword in keywords)


user_story_entries = [
    e for e in completed_steps if _belongs_to(e, ["user stor", "stor", "persona"])
]
feature_entries = [
    e for e in completed_steps if _belongs_to(e, ["feature"])
]
task_entries = [
    e for e in completed_steps if _belongs_to(e, ["task", "engineering"])
]

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
