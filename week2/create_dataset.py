from langsmith import Client
from openai import OpenAI

class OpenEvalsClient():
    client: Client
    llm: OpenAI

    def __init__(self, langsmith_client, openai_client):
        self.client = langsmith_client
        self.llm = openai_client


    def prepare_examples(self, test_cases):
        examples = []
        for test_case in test_cases:
            examples.append({
                "inputs": {
                    "question": test_case['question']
                },
                "outputs": {
                    "answer": test_case['reference']
                }
            })
        return examples

    def initialize_dataset(self, test_cases):
        # create a dataset
        dataset = self.client.create_dataset(dataset_name="Sample Project Codebase 3", description="Test cases for evaluating comprehension of the sample project codebase.")
        
        print(f"Created dataset with ID: {dataset.id}")

        # prepare examples
        examples = self.prepare_examples(test_cases)

        print(examples)

        # upload examples to the dataset
        self.client.create_examples(dataset_id=dataset.id, examples=examples)
        print(f"Uploaded {len(examples)} examples to the dataset.")