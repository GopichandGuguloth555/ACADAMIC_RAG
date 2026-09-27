from retrieval import retrieve_documents


query = "What is computer science?"

results = retrieve_documents(query, k=5)

print("\nQuery:")
print(query)

print("\nRetrieved documents:")

documents = results["documents"][0]
metadatas = results["metadatas"][0]
distances = results["distances"][0]

for i in range(len(documents)):
    print(f"\n--- Result {i + 1} ---")
    print("Distance:", distances[i])
    print("Metadata:", metadatas[i])
    print("Content:")
    print(documents[i])