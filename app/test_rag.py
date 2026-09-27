from rag import answer_question


query = "Who is the current president of India?"

result = answer_question(query)


print("\n================ ANSWER ================\n")
print(result["answer"])

print("\n================ SOURCES ================\n")

for source in result["sources"]:
    print(
        f"Source: {source['source']} | "
        f"Page: {source['page']}"
    )