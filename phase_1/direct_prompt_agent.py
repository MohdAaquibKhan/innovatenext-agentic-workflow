# Test script for DirectPromptAgent class

from workflow_agents.base_agents import DirectPromptAgent
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")

prompt = "What is the Capital of France?"

direct_agent = DirectPromptAgent(openai_api_key)
direct_agent_response = direct_agent.respond(prompt)

# Print the response from the agent
print(direct_agent_response)

# This agent has no persona and no supplied knowledge, so its answer comes entirely
# from the general knowledge gpt-4.1-mini picked up during its own training -- not
# from anything we gave it at runtime.
print(
    "Knowledge source: the LLM's own pretrained general knowledge "
    "(no persona or external knowledge was supplied to this agent)."
)
