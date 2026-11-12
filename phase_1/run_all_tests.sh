#!/bin/bash
# Run every Phase 1 agent test script and save each one's output to its own text file.
# Usage: bash run_all_tests.sh   (run this from inside the phase_1 folder)

for script in direct_prompt_agent augmented_prompt_agent knowledge_augmented_prompt_agent rag_knowledge_prompt_agent evaluation_agent routing_agent action_planning_agent; do
  echo "=== Running ${script}.py ==="
  python "${script}.py" > "output_${script}.txt" 2>&1
done

echo "Done. Output files:"
ls output_*.txt
