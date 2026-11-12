from workflow_agents.base_agents import AugmentedPromptAgent
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Retrieve OpenAI API key from environment variables
openai_api_key = os.getenv("OPENAI_API_KEY")

prompt = "What is the capital of France?"
persona = "You are a college professor; your answers always start with: 'Dear students,'"

augmented_agent = AugmentedPromptAgent(openai_api_key, persona)
augmented_agent_response = augmented_agent.respond(prompt)

# Print the agent's response
print(augmented_agent_response)

# Knowledge source: the fact itself (Paris) still comes from the LLM's own pretrained
# general knowledge -- we didn't supply any external facts, only a persona to adopt.
print(
    "Knowledge source: the LLM's own pretrained general knowledge supplied the fact "
    "(Paris) -- no external knowledge was given to this agent, only a persona."
)

# Persona effect: specifying the persona (and telling the model to forget prior context)
# changed the greeting and tone of the response, not the underlying fact.
print(
    "Persona effect: the 'college professor' persona changed the greeting and tone of "
    "the response -- it opens with 'Dear students,' and reads in a more professorial "
    "voice -- but it did not change the underlying fact, since the capital of France "
    "is common knowledge the model already has."
)
