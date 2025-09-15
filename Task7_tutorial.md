# Backwards Chaining Inference Engine

A complete implementation of a backwards chaining inference engine in Python, featuring variable unification, recursive reasoning, and a structured knowledge base. This implementation demonstrates core concepts from logic programming and expert systems.

## Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Architecture](#architecture)
- [Quick Start](#quick-start)
- [How Backwards Chaining Works](#how-backwards-chaining-works)
- [Knowledge Base Structure](#knowledge-base-structure)
- [Variable Unification](#variable-unification)
- [Examples](#examples)
- [API Reference](#api-reference)
- [Advanced Usage](#advanced-usage)
- [Limitations](#limitations)
- [Contributing](#contributing)

## Overview

Backwards chaining is a goal-driven inference method used in artificial intelligence and expert systems. Instead of starting with facts and deriving conclusions (forward chaining), backwards chaining starts with a goal and works backwards to find supporting evidence.

This implementation provides:
- A structured knowledge base for facts and rules
- Variable unification for flexible pattern matching
- Recursive proof strategies
- Detailed reasoning traces for transparency
- Protection against infinite recursion

## Key Features

- **Variable Unification**: Support for logical variables (uppercase names) with automatic binding
- **Recursive Rules**: Handle complex relationships like ancestor chains
- **Multiple Solutions**: Find all possible ways to prove a goal
- **Reasoning Traces**: Step-by-step explanation of the inference process
- **Infinite Loop Detection**: Prevents stack overflow in recursive scenarios
- **Clean API**: Easy-to-use interface for building knowledge bases and making queries

## Architecture

The system consists of four main components:

```
┌─────────────────┐    ┌─────────────────┐
│  KnowledgeBase  │◄───┤ BackwardChain   │
│  - Facts        │    │ Engine          │
│  - Rules        │    │                 │
└─────────────────┘    └─────────────────┘
         │                       │
         ▼                       ▼
┌─────────────────┐    ┌─────────────────┐
│     Term        │    │  Unification    │
│  - Constants    │    │  - Variable     │
│  - Variables    │    │    binding      │
│  - Compounds    │    │  - Substitution │
└─────────────────┘    └─────────────────┘
```

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

### Example Walkthrough

Given the goal `grandparent(john, alice)`:

```
1. Goal: grandparent(john, alice)
2. Find rule: grandparent(X, Z) :- parent(X, Y), parent(Y, Z)
3. Unify: X=john, Z=alice
4. New goals: parent(john, Y), parent(Y, alice)
5. Prove parent(john, Y): finds parent(john, mary), so Y=mary
6. Prove parent(mary, alice): finds this as a fact
7. Success: All premises proven
```

## Knowledge Base Structure

### Facts

Facts are ground truths with no variables:

```python
kb.add_fact("parent", "john", "mary")      # parent(john, mary)
kb.add_fact("color", "sky", "blue")        # color(sky, blue)
kb.add_fact("likes", "alice", "chocolate") # likes(alice, chocolate)
```

### Rules

Rules define logical implications using variables (uppercase):

```python
# sibling(X, Y) :- parent(Z, X), parent(Z, Y)
kb.add_rule("sibling", ["X", "Y"], 
           [("parent", ["Z", "X"]), ("parent", ["Z", "Y"])])

# ancestor(X, Y) :- parent(X, Y)
kb.add_rule("ancestor", ["X", "Y"], [("parent", ["X", "Y"])])

# ancestor(X, Y) :- parent(X, Z), ancestor(Z, Y)  [recursive]
kb.add_rule("ancestor", ["X", "Y"], 
           [("parent", ["X", "Z"]), ("ancestor", ["Z", "Y"])])
```

### Terms and Variables

- **Constants**: Lowercase strings or any non-string values (`"john"`, `42`)
- **Variables**: Uppercase strings (`"X"`, `"PERSON"`, `"AGE"`)
- **Compounds**: Terms with arguments (`parent(john, mary)`)

## Variable Unification

Unification is the process of making two terms equal by finding appropriate variable bindings.

### Examples

```python
# Unify parent(john, X) with parent(john, mary)
# Result: X = mary

# Unify sibling(X, Y) with sibling(tom, mary)  
# Result: X = tom, Y = mary

# Unify parent(X, Y) with parent(alice, Z)
# Result: X = alice, Y = Z (or any consistent binding)
```

### Substitution

Once variables are bound, they're consistently replaced throughout the proof:

```python
# Rule: grandparent(X, Z) :- parent(X, Y), parent(Y, Z)
# Goal: grandparent(john, alice)
# After unification: X=john, Z=alice
# Subgoals become: parent(john, Y), parent(Y, alice)
```

## Examples

### Family Relationships

```python
# Build family tree
kb = KnowledgeBase()
kb.add_fact("parent", "john", "mary")
kb.add_fact("parent", "john", "tom") 
kb.add_fact("parent", "mary", "alice")
kb.add_fact("male", "john")
kb.add_fact("male", "tom")
kb.add_fact("female", "mary")

# Define relationships
kb.add_rule("grandparent", ["X", "Z"], 
           [("parent", ["X", "Y"]), ("parent", ["Y", "Z"])])
kb.add_rule("uncle", ["X", "Y"], 
           [("sibling", ["X", "Z"]), ("parent", ["Z", "Y"]), ("male", ["X"])])

# Query relationships
engine = BackwardsChainingEngine(kb)
solutions, _ = engine.query("grandparent", "john", "alice")  # ✓ True
solutions, _ = engine.query("uncle", "tom", "alice")         # ✓ True
```

### Animal Classification

```python
kb = KnowledgeBase()

# Animal facts
kb.add_fact("has_feathers", "tweety")
kb.add_fact("can_fly", "tweety")
kb.add_fact("has_fur", "fido")
kb.add_fact("barks", "fido")

# Classification rules
kb.add_rule("bird", ["X"], [("has_feathers", ["X"]), ("can_fly", ["X"])])
kb.add_rule("mammal", ["X"], [("has_fur", ["X"])])
kb.add_rule("dog", ["X"], [("mammal", ["X"]), ("barks", ["X"])])
kb.add_rule("warm_blooded", ["X"], [("bird", ["X"])])
kb.add_rule("warm_blooded", ["X"], [("mammal", ["X"])])

# Classify animals
engine = BackwardsChainingEngine(kb)
solutions, _ = engine.query("bird", "tweety")           # ✓ True
solutions, _ = engine.query("dog", "fido")              # ✓ True  
solutions, _ = engine.query("warm_blooded", "tweety")   # ✓ True
```

## API Reference

### KnowledgeBase

```python
class KnowledgeBase:
    def add_fact(self, predicate: str, *args) -> None
    def add_rule(self, head_pred: str, head_args: List[str], 
                body_conditions: List[Tuple[str, List[str]]]) -> None
    def get_matching_clauses(self, goal: Term) -> List[Clause]
    def print_knowledge_base(self) -> None
```

### BackwardsChainingEngine

```python
class BackwardsChainingEngine:
    def __init__(self, knowledge_base: KnowledgeBase)
    def query(self, predicate: str, *args) -> Tuple[List[Dict], List[str]]
    def prove(self, goal: Term, substitution: Dict = None, depth: int = 0) -> List[Dict]
```

### Term

```python
class Term:
    def __init__(self, name: str, args: List = None)
    @property
    def is_variable(self) -> bool
```

### Unification

```python
class Unification:
    @staticmethod
    def unify(term1: Term, term2: Term, substitution: Dict = None) -> Dict
    @staticmethod  
    def substitute(term: Term, substitution: Dict) -> Term
```

## Advanced Usage

### Multiple Solutions

Some queries may have multiple valid answers:

```python
# Who are john's children?
solutions, _ = engine.query("parent", "john", "X")
# Returns: [{"X": "mary"}, {"X": "tom"}]

# Find all grandparent relationships
solutions, _ = engine.query("grandparent", "X", "Y") 
# Returns all valid X, Y combinations
```

### Recursive Rules

Handle transitive relationships:

```python
# Ancestor relationship (recursive)
kb.add_rule("ancestor", ["X", "Y"], [("parent", ["X", "Y"])])
kb.add_rule("ancestor", ["X", "Y"], 
           [("parent", ["X", "Z"]), ("ancestor", ["Z", "Y"])])

# Can prove multi-generational relationships
solutions, _ = engine.query("ancestor", "john", "alice")  # ✓ True
```

### Debugging with Traces

Use reasoning traces to understand the inference process:

```python
solutions, trace = engine.query("grandparent", "john", "alice")
for step in trace:
    print(step)

# Output:
# Trying to prove: grandparent(john, alice)
# Unified with: grandparent(X_0, Z_0) :- parent(X_0, Y_0), parent(Y_0, Z_0)
# Proving body conditions...
#   Trying to prove: parent(john, Y_0)
#   ✓ Fact proven: parent(john, mary)
#   Trying to prove: parent(mary, alice)  
#   ✓ Fact proven: parent(mary, alice)
# ✓ All premises proven
```

## Limitations

- **No Negation**: Cannot handle negation as failure or closed-world assumption
- **No Arithmetic**: No built-in arithmetic predicates or constraint solving  
- **Simple Unification**: No occurs check or complex term unification
- **Memory Usage**: Keeps full reasoning traces (can be memory-intensive)
- **Performance**: Not optimized for large knowledge bases (no indexing)

## Performance Considerations

For better performance with large knowledge bases:

1. **Fact Ordering**: Place more specific facts before general ones
2. **Rule Ordering**: Order rule premises from most to least restrictive
3. **Goal Ordering**: Query more specific goals first in complex scenarios
4. **Limit Depth**: Set maximum recursion depth for recursive rules

## Contributing

Contributions are welcome! Areas for improvement:

- **Optimization**: Indexing for faster clause retrieval
- **Extensions**: Cut operator, negation as failure, constraint handling
- **Testing**: More comprehensive test coverage
- **Documentation**: Additional examples and use cases

## License

MIT License - see LICENSE file for details.

## References

- Russell, S. & Norvig, P. *Artificial Intelligence: A Modern Approach*
- Clocksin, W.F. & Mellish, C.S. *Programming in Prolog*
- Bratko, I. *Prolog Programming for Artificial Intelligence*
