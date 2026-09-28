from rag import answer_question


query = "What is computer science?"

result = answer_question(query)


print("\nANSWER\n")
print(result["answer"])

print("\nSOURCES\n")

for source in result["sources"]:
    print(
        f"Source: {source['source']} | "
        f"Page: {source['page']}"
    )