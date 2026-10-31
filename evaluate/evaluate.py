import json
import statistics
import time

import httpx

API_URL = "http://localhost:8000/ask"
QUESTIONS = [
    "О чем первый документ?",
    "какие факты есть в документах?",
    "Сделай краткий вывод по документам.",
    "Какие выводы можно сделать по результатам?",
    "Что можно сказать о данных?",
]

def evaluate_ask(question: str, k: int = 3) -> dict:
    results = []
    with httpx.Client() as client:
        for question in QUESTIONS:
            start_time = time.perf_counter()
            try:
                response = client.post(API_URL, json={"question": question, "k": 3},)
                time_result = time.perf_counter() - start_time
                dt = response.json()
                answer = dt["answer"]
                result = {"question": question, "seconds": time_result, "length": len(answer), "answer": answer}
                results.append(result)
            except Exception as e:
                print(f"Error occurred while processing question: {question}. Error: {e}")
                continue     
    return results

def evaluate_stream_ask(question: str, k: int = 3) -> dict:
    results = []
    with httpx.Client(timeout=120.0) as client:
        for question in QUESTIONS:
            start_time = time.perf_counter()
            tokens = []
            try:
                with client.stream("POST", f"{API_URL}/stream", json = {"question": question, "k": k}) as response:
                    for line in response.iter_lines():
                        if line.startswith("data: ") and "[DONE]" not in line:
                            token = line[len("data: "):]
                            tokens.append(token)
                time_result = time.perf_counter() - start_time
                answer = "".join(tokens)
                result = {"question": question, "seconds": time_result, "length": len(answer), "answer": answer}
                results.append(result)
            except Exception as e:
                print(f"Error occurred while processing question: {question}. Error: {e}")
                continue
    return results

def main() -> None:
    results = evaluate_ask(QUESTIONS)
    if not results:
        print("No results to display.")
        return
    with open("output/evaluation_results.json", "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
    avg_time = statistics.mean([r["seconds"] for r in results])
    avg_length = statistics.mean([r["length"] for r in results])
    print("Results:")
    print(f"Successfully processed {len(results)} of {len(QUESTIONS)} questions")
    print(f"Average time: {avg_time:.2f} seconds")
    print(f"Average answer length: {avg_length:.2f} characters")


if __name__ == "__main__":
    main()