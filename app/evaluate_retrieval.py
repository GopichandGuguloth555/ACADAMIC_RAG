from evaluation_dataset import EVALUATION_DATASET
from retrieval import retrieve_documents


def evaluate():

    total = len(EVALUATION_DATASET)
    passed = 0

    for item in EVALUATION_DATASET:

        question = item["question"]
        expected_keywords = item["expected_keywords"]

        result = retrieve_documents(
            question,
            k=5
        )

        documents = result["documents"]

        combined_text = " ".join(documents).lower()

        found = all(
            keyword.lower() in combined_text
            for keyword in expected_keywords
        )

        print("\n" + "=" * 60)
        print("Question:")
        print(question)

        print("\nSearch query:")
        print(result["search_query"])

        print("\nResult:")
        print("PASS" if found else "FAIL")

        if found:
            passed += 1

    accuracy = (passed / total) * 100

    print("\n" + "=" * 60)
    print("Retrieval Evaluation")
    print("=" * 60)
    print(f"Passed: {passed}/{total}")
    print(f"Retrieval accuracy: {accuracy:.2f}%")


if __name__ == "__main__":
    evaluate()