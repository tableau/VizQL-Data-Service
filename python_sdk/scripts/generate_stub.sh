#!/bin/bash

# Exit on error
set -e

# Print commands as they are executed
set -x

pip install datamodel-code-generator==0.43.1

# Generate client code
datamodel-codegen --input ../VizQLDataServiceOpenAPISchema.json --output-model-type pydantic_v2.BaseModel --input-file-type openapi --output src/api/openapi_generated-raw.py --use-annotated --base-class TableauModel

echo "Starting post-processing..."
python scripts/post_process.py

echo "OpenAPI client generation completed successfully"