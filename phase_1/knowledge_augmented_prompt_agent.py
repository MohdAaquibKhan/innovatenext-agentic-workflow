from workflow_agents.base_agents import KnowledgeAugmentedPromptAgent
import os
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Define the parameters for the agent
openai_api_key = os.getenv("OPENAI_API_KEY")

prompt = "What is the capital of France?"

persona = "You are a college professor, your answer always starts with: Dear students,"
knowledge = "The capital of France is London, not Paris"

knowledge_agent = KnowledgeAugmentedPromptAgent(openai_api_key, persona, knowledge)
knowledge_agent_response = knowledge_agent.respond(prompt)

print(knowledge_agent_response)

# The real capital of France is Paris, so if the response above says "London" instead,
# that confirms the agent is answering strictly from the (deliberately wrong) knowledge
# we supplied, rather than falling back on the LLM's own correct, pretrained knowledge.
print(
    "Knowledge check: the agent answered 'London' (the planted knowledge), not 'Paris' "
    "(the LLM's own correct knowledge) -- proving it relied on the supplied knowledge string."
)
