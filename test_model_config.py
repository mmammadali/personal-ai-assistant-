"""Test model configuration"""
from config import DEFAULT_MODEL, COMPLEX_MODEL, get_model_for_query, is_complex_query

print("=" * 60)
print("Model Configuration Test")
print("=" * 60)

print(f"\nDefault Model: {DEFAULT_MODEL}")
print(f"Complex Model: {COMPLEX_MODEL}")

# Test simple queries
simple_queries = [
    "hello",
    "what is the weather",
    "create a task",
    "show me events",
    "سلام"
]

print("\n" + "-" * 60)
print("Simple Queries (should use gpt-5-mini):")
print("-" * 60)
for query in simple_queries:
    model = get_model_for_query(query)
    is_complex = is_complex_query(query)
    print(f"Query: '{query[:40]}...'")
    print(f"  Model: {model} | Complex: {is_complex}")

# Test complex queries
complex_queries = [
    "analyze and compare the strategic implications",
    "synthesize information from multiple sources",
    "evaluate the comprehensive impact",
    "تحلیل جامع و مقایسه استراتژیک",
    "This is a very long query that contains many words and requires detailed analysis and comprehensive evaluation of multiple factors and strategic considerations that need thorough examination"
]

print("\n" + "-" * 60)
print("Complex Queries (should use gpt-5):")
print("-" * 60)
for query in complex_queries:
    model = get_model_for_query(query)
    is_complex = is_complex_query(query)
    print(f"Query: '{query[:40]}...'")
    print(f"  Model: {model} | Complex: {is_complex}")

print("\n" + "=" * 60)
print("Configuration Test Complete")
print("=" * 60)








