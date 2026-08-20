import sys
import os
import json


# --------------------------------------------------
# Project root
# --------------------------------------------------

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

sys.path.append(
    PROJECT_ROOT
)


# --------------------------------------------------
# Imports
# --------------------------------------------------

from app.generator import AnswerGenerator


# --------------------------------------------------
# Load Metadata
# --------------------------------------------------

METADATA_FILE = os.path.join(
    PROJECT_ROOT,
    "index",
    "metadata.json"
)


with open(
    METADATA_FILE,
    "r",
    encoding="utf-8"
) as file:

    metadata = json.load(file)


# --------------------------------------------------
# Test Context
# --------------------------------------------------

contexts = metadata[:3]


# --------------------------------------------------
# Generator
# --------------------------------------------------

generator = AnswerGenerator()


# --------------------------------------------------
# Test Question
# --------------------------------------------------

query = "what is a corporation?"


print("=" * 70)
print("GENERATOR TEST")
print("=" * 70)

print("\nQuestion:")
print(query)


print("\nGenerating answer...")


result = generator.generate(
    query=query,
    contexts=contexts
)


print("\n")
print("=" * 70)
print("RESULT")
print("=" * 70)

print("\nAnswer:")

print(
    result["answer"]
)


print("\nGrounded:")

print(
    result["grounded"]
)