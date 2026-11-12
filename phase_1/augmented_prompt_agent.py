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

# The agent still answers from the LLM's own pretrained general knowledge -- we didn't
# give it any external facts, just a persona to adopt. Specifying the persona in the
# system prompt (and explicitly telling it to forget prior context) changed the tone
# and framing of the answer -- it comes back addressed to "Dear students," in a more
# professorial voice -- but it didn't change the underlying facts, since the capital
# of France is common knowledge the model already has.
