from llm import generate_answer


prompt = """

what is ai and how may ai models are existed till date

"""

answer = generate_answer(prompt)

print("\nLLM Answer:")
print(answer)