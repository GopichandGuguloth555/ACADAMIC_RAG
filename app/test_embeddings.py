from embeddings import create_embedding


text = "Python is a programming language"

vector = create_embedding(text)

print("Vector:", vector)
print("Vector dimensions:", len(vector))