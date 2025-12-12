# Model Configuration - GPT-5 Setup

## Overview

The system has been configured to use **GPT-5 models** with intelligent model selection based on query complexity.

## Model Configuration

### Default Models

- **Default Model (Simple Queries):** `gpt-5-mini`
  - Fast, cost-effective
  - Used for regular queries, simple tasks, and routine operations
  
- **Complex Model (Complex Queries):** `gpt-5`
  - Better reasoning capabilities
  - Used for complex analysis, synthesis, and strategic queries

### Model Selection Logic

The system automatically selects the appropriate model based on query characteristics:

#### Simple Queries → `gpt-5-mini`
- Short queries
- Simple commands
- Routine tasks
- Basic questions

#### Complex Queries → `gpt-5`
- Contains complex keywords: "analyze", "synthesize", "compare", "evaluate", "strategic", etc.
- Long queries (>50 words)
- Multiple questions (>2 questions)
- Persian complex keywords: "تحلیل", "مقایسه", "ارزیابی", "استراتژیک", etc.

## Configuration Files

### `config.py`

```python
# Default model for regular queries
DEFAULT_MODEL = "gpt-5-mini"

# Complex model for complex queries
COMPLEX_MODEL = "gpt-5"

# Helper functions
def is_complex_query(query: str) -> bool:
    """Determine if query requires complex model"""
    # Checks for keywords, length, question count
    
def get_model_for_query(query: str = None) -> str:
    """Get appropriate model for a query"""
    # Returns COMPLEX_MODEL or DEFAULT_MODEL
```

## Agent Integration

The main agent (`agent.py`) automatically:
1. Analyzes user queries
2. Determines complexity
3. Selects appropriate model (`gpt-5-mini` or `gpt-5`)
4. Uses selected model for processing

### Dynamic Model Selection

```python
# In agent_node function
user_query = extract_query_from_messages()
selected_model = get_model_for_query(user_query)

if selected_model != base_model:
    llm = ChatOpenAI(model=selected_model)
else:
    llm = base_llm
```

## Other Model Configurations

### RAG Agent
- **Model:** `gpt-5-mini` (can be upgraded to `gpt-5` for complex document analysis)

### Finance Agent
- **Model:** `gpt-5-mini` (can be upgraded to `gpt-5` for complex financial analysis)

### Embeddings
- **Model:** `text-embedding-3-large` (unchanged)

## Complex Query Keywords

The system recognizes these keywords (English and Persian) as indicators of complex queries:

**English:**
- analyze, synthesize, compare, evaluate, strategic, complex
- detailed analysis, comprehensive, deep dive, thorough

**Persian:**
- تحلیل, مقایسه, ارزیابی, استراتژیک, پیچیده, جامع

## Usage Examples

### Simple Query (uses gpt-5-mini)
```
User: "Create a task for tomorrow"
→ Model: gpt-5-mini
```

### Complex Query (uses gpt-5)
```
User: "Analyze and compare the strategic implications of our Q4 performance"
→ Model: gpt-5
```

### Persian Complex Query (uses gpt-5)
```
User: "تحلیل جامع عملکرد تیم و مقایسه با اهداف استراتژیک"
→ Model: gpt-5
```

## Testing

Run the test script to verify configuration:

```bash
python test_model_config.py
```

This will show:
- Default and complex model names
- Model selection for sample queries
- Complex query detection results

## Benefits

1. **Cost Optimization:** Use cheaper `gpt-5-mini` for simple queries
2. **Performance:** Use powerful `gpt-5` only when needed
3. **Automatic Selection:** No manual model selection required
4. **Intelligent Detection:** Recognizes query complexity automatically

## Customization

### Adding Complex Keywords

Edit `config.py`:

```python
COMPLEX_QUERY_KEYWORDS = [
    "analyze", "synthesize", "compare", "evaluate", "strategic", "complex",
    "detailed analysis", "comprehensive", "deep dive", "thorough",
    "تحلیل", "مقایسه", "ارزیابی", "استراتژیک", "پیچیده", "جامع",
    # Add your custom keywords here
]
```

### Adjusting Query Length Threshold

Edit `config.py` in `is_complex_query()`:

```python
# Current: 50 words
if len(query.split()) > 50:
    return True

# Change to your preferred threshold
if len(query.split()) > 30:  # More sensitive
    return True
```

### Adjusting Question Count Threshold

Edit `config.py` in `is_complex_query()`:

```python
# Current: >2 questions
if question_count > 2:
    return True

# Change to your preferred threshold
if question_count > 1:  # More sensitive
    return True
```

## Verification

✅ **Configuration Verified:**
- Default model: `gpt-5-mini` ✓
- Complex model: `gpt-5` ✓
- Model selection logic: Working ✓
- Agent integration: Complete ✓

## Notes

- The system will automatically use the appropriate model based on query analysis
- You can manually override by specifying a model when initializing agents
- Complex query detection is conservative (better to use gpt-5 when in doubt)
- All Phase 2 features respect this model configuration

---

**Last Updated:** Model configuration updated to GPT-5
**Status:** ✅ Active and tested








