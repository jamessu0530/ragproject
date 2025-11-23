from embedding_utils import get_embedding

vec = get_embedding("這是一段測試文字")
print(len(vec), vec[:5])
