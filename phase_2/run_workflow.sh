#!/bin/bash
# Run the Phase 2 agentic workflow and save its output to a text file.
# Usage: bash run_workflow.sh   (run this from inside the phase_2 folder)

python agentic_workflow.py > output_agentic_workflow.txt 2>&1

echo "Done. Output file:"
ls output_agentic_workflow.txt
