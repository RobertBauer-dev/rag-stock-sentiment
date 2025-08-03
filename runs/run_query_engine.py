from app.rag.query_engine import search_similar_posts, generate_answer_from_context

query = "Wie war die Stimmung zu Tesla nach den Q2-Ergebnissen 2025?"
context = search_similar_posts(query, collection_name="tesla_2025q2")
print(context)

answer = generate_answer_from_context(query, context)
print("📣 Antwort vom LLM:\n")
print(answer)

