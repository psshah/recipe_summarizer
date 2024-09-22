# Import necessary libraries
from dotenv import load_dotenv
from llama_index.core import SimpleDirectoryReader

# Load environment variables
load_dotenv()

from openai import OpenAI
import json


summary_prompt = """
You are an expert summarizer tasked with generating summaries of recipes based on the following document excerpt.
The summary should focus on retrieving recipe title, key ingredients, preparation time, serving size, instructions and specific tips or notes from the text.

Instructions:

- Generate **1** summary, each with a corresponding **expected_output**.
- Present the output in the following structured JSON format:

[
  {
    "recipe_title": "Can you summarize the recipe in this document?",
    "expected_output": "Sure, here is a overall summary..."
  },
]
"""

client = OpenAI()

# Function to generate summary
def generate_summary(prompt, text, temperature=0.2):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": text}],
        temperature=temperature,
    )

    print(response.choices[0].message.content)

    # Strip extraneous symbols from the response content
    content = response.choices[0].message.content.strip()

    # Remove potential JSON code block markers
    content = content.strip()
    if content.startswith('```'):
        content = content.split('\n', 1)[-1]
    if content.endswith('```'):
        content = content.rsplit('\n', 1)[0]
    content = content.strip()

    # Attempt to parse the cleaned content as JSON
    try:
        parsed_content = json.loads(content.strip())
        return parsed_content
    except json.JSONDecodeError:
        print("Error: Unable to parse JSON. Raw content:")
        print(content)
        return []
############

# Generate dataset
import os
import json

# 1. Load documents from a directory
documents = SimpleDirectoryReader("data").load_data()

# 2. Generate summary for each document
dataset_file = 'recipe_dataset.json'

if os.path.exists(dataset_file):
    # Load dataset from local file if it exists
    with open(dataset_file, 'r') as f:
        dataset = json.load(f)
else:
    # Generate dataset if local file doesn't exist
    dataset = []
    for doc in documents:
        recipe_summaries = generate_summary(summary_prompt, doc.text, temperature=0.2)
        dataset.extend(recipe_summaries)

    print("Fetched dataset: writing to file")
    # Write dataset to local file
    with open(dataset_file, 'w') as f:
        json.dump(dataset, f)

    print("Completed writing dataset to file")

# 2. Upload dataset in Langfuse
from langfuse import Langfuse
langfuse = Langfuse()

dataset_name = "recipe_summarizer_evaluation_set"
langfuse.create_dataset(name=dataset_name)

for item in dataset:
    langfuse.create_dataset_item(
     dataset_name=dataset_name,
      input=item["recipe_title"],
      expected_output=item["expected_output"]
)

print("Completed writing dataset to langfuse")
