import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.environ["NVIDIA_API_KEY"], base_url="https://integrate.api.nvidia.com/v1")

response = client.chat.completions.create(
    model="meta/llama-3.3-70b-instruct",
    messages=[
        {"role": "system", "content": "Respond with ONLY a JSON object: {\"problem_statement\": \"...\", \"examples\": [...], \"constraints\": [...], \"test_cases\": [...], \"python_solution\": \"...\"} — generate a full coding interview question for 'Elections in Saransk', category Greedy, difficulty Hard, with exactly 10 test cases and a working Python solution."},
        {"role": "user", "content": "Generate it."},
    ],
    temperature=0.4,
    max_tokens=2500,
    response_format={"type": "json_object"},
)

print("FINISH REASON:", response.choices[0].finish_reason)
print("LENGTH:", len(response.choices[0].message.content))
print("---CONTENT---")
print(response.choices[0].message.content)