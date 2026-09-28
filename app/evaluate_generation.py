from evaluation_dataset import EVALUATION_DATASET
from rag import answer_question
from llm import generate_answer


def evaluate_generation():

    total = len(EVALUATION_DATASET)
    passed = 0

    for item in EVALUATION_DATASET:

        question = item["question"]

        result = answer_question(question)

        answer = result["answer"]

        documents = result.get("sources", [])

        # Build a simple evaluation prompt
        evaluation_prompt = f"""
You are evaluating an answer produced by a RAG system.

Question:
{question}

Answer:
{answer}

Sources:
{documents}

Determine whether the answer is supported by the retrieved
sources.

Return ONLY one of:

SUPPORTED
NOT_SUPPORTED
"""

        evaluation = generate_answer(evaluation_prompt).strip()

        print("\n" + "=" * 60)
        print("Question:")
        print(question)

        print("\nGenerated Answer:")
        print(answer)

        print("\nEvaluation:")
        print(evaluation)

        if "SUPPORTED" in evaluation.upper() and \
           "NOT_SUPPORTED" not in evaluation.upper():
            passed += 1

    accuracy = (passed / total) * 100

    print("\n" + "=" * 60)
    print("Generation Evaluation")
    print("=" * 60)
    print(f"Passed: {passed}/{total}")
    print(f"Faithfulness: {accuracy:.2f}%")


if __name__ == "__main__":
    evaluate_generation()