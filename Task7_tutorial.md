# Backwards Chaining Inference Engine

A complete implementation of a backwards chaining inference engine in Python, featuring variable unification, recursive reasoning, and a structured knowledge base. This implementation demonstrates core concepts from logic programming and expert systems.


## Overview

Backwards chaining is a goal-driven inference method used in artificial intelligence and expert systems. Instead of starting with facts and deriving conclusions (forward chaining), backwards chaining starts with a goal and works backwards to find supporting evidence.

This implementation provides:
- A structured knowledge base for facts and rules
- Variable unification for flexible pattern matching
- Recursive proof strategies
- Detailed reasoning traces for transparency
- Protection against infinite recursion




## Quick Start

```python
from backwards_chaining import KnowledgeBase, BackwardsChainingEngine

# Create a knowledge base
kb = KnowledgeBase()

# Add some facts
kb.add_fact("parent", "john", "mary")
kb.add_fact("parent", "mary", "alice")
kb.add_fact("male", "john")

# Add a rule: grandparent(X, Z) :- parent(X, Y), parent(Y, Z)
kb.add_rule("grandparent", ["X", "Z"], 
           [("parent", ["X", "Y"]), ("parent", ["Y", "Z"])])

# Create inference engine
engine = BackwardsChainingEngine(kb)

# Query the knowledge base
solutions, trace = engine.query("grandparent", "john", "alice")

if solutions:
    print("✓ john is alice's grandparent")
    print("Reasoning:")
    for step in trace:
        print(step)
else:
    print("✗ Cannot prove john is alice's grandparent")
```

## How Backwards Chaining Works

The backwards chaining algorithm follows this process:

1. **Start with Goal**: Begin with what you want to prove
2. **Check Facts**: If the goal is already a known fact, return success
3. **Find Rules**: Look for rules whose conclusion matches the goal
4. **Prove Premises**: For each applicable rule, recursively prove all premises
5. **Unify Variables**: Match variables in rules with specific values
6. **Return Solutions**: Collect all successful proof paths



### BackwardsChainingEngine

```python
class BackwardsChainingEngine:
    def __init__(self, knowledge_base: KnowledgeBase)
    def query(self, predicate: str, *args) -> Tuple[List[Dict], List[str]]
    def prove(self, goal: Term, substitution: Dict = None, depth: int = 0) -> List[Dict]
```



## License

MIT License - see LICENSE file for details.

## References

- Russell, S. & Norvig, P. *Artificial Intelligence: A Modern Approach*
- Clocksin, W.F. & Mellish, C.S. *Programming in Prolog*
- Bratko, I. *Prolog Programming for Artificial Intelligence*
