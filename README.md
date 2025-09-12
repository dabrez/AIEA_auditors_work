# AIEA_auditors_work

# Introduction to Temporal Logic

A comprehensive guide to Linear Temporal Logic (LTL) and Computation Tree Logic (CTL) for formal verification.

> Based on EECS 294-98 lectures by Prof. Sanjit A. Seshia, UC Berkeley

## Table of Contents

- [Basic Concepts](#basic-concepts)
- [Safety vs Liveness Properties](#safety-vs-liveness-properties)
- [Linear Temporal Logic (LTL)](#linear-temporal-logic-ltl)
- [Computation Tree Logic (CTL)](#computation-tree-logic-ctl)
- [LTL vs CTL Comparison](#ltl-vs-ctl-comparison)
- [Practical Examples](#practical-examples)
- [Further Reading](#further-reading)

## Basic Concepts

### Behavior, Run, Computation

A **computation** is a sequence of states starting with an initial state:
```
s₀ → s₁ → s₂ → ... such that R(sᵢ, sᵢ₊₁) is true
```

Also called a "run" or "(computation) path".

A **trace** is the sequence of observable parts of states - essentially the sequence of state labels.

### Atomic State Properties

Boolean formulas over state variables. We represent these with:
- Distinct colors in diagrams
- Names like `p`, `q`, `req`, `ack`, etc.

Examples:
- `req` (request signal is active)
- `req & !ack` (request active but not acknowledged)

## Safety vs Liveness Properties

### Safety Properties
- **Definition**: "Something bad must not happen"
- **Characteristics**: Finite-length error trace
- **Examples**: 
  - System should not crash
  - No more than one processor should have cache line in write mode

### Liveness Properties  
- **Definition**: "Something good must happen"
- **Characteristics**: Infinite-length error trace
- **Examples**:
  - Every packet sent must be received at destination
  - Every request must eventually receive an acknowledge

### Exercise: Classify These Properties

1. "No more than one processor should have a cache line in write mode" → **Safety**
2. "The grant signal must be asserted at some point after the request signal is asserted" → **Liveness**
3. "Every request signal must receive an acknowledge and the request should stay asserted until acknowledged" → **Safety + Liveness**

## Linear Temporal Logic (LTL)

LTL expresses properties over a single computation path or run.

### Basic Temporal Operators

#### Globally (Always): `G p`
- `G p` is true if `p` holds at **all** states along the path
- Think: "**G**lobally, property p is true"

```
G p: p p p p p ...
     ✓ ✓ ✓ ✓ ✓
```

#### Eventually: `F p` 
- `F p` is true if `p` holds at **some** state along the path
- Think: "**F**inally, property p becomes true"

```
F p: ¬p ¬p p ¬p ¬p ...
     ✗  ✗  ✓  ✗  ✗
```

#### Next: `X p`
- `X p` is true if `p` holds in the **next** state
- Think: "ne**X**t state satisfies p"

```
X p: current_state → next_state
     (evaluate here)    (p true here)
```

#### Until: `p U q`
- `p U q` is true if:
  - `q` eventually becomes true
  - `p` holds in all states **until** `q` becomes true

```
p U q: p p p q ¬p ...
       ✓ ✓ ✓ ✓  ✗
```

### Operator Relationships

You can express operators in terms of others:
- `F p ≡ true U p` (eventually p = true until p)
- `G p ≡ ¬F ¬p` (always p = not eventually not-p)

### Common LTL Patterns

| Pattern | Meaning | Example |
|---------|---------|---------|
| `G F p` | Infinitely often p | System repeatedly processes requests |
| `F G p` | Eventually always p | System eventually stabilizes |
| `G(p → F q)` | Every p followed by q | Every request gets response |
| `G(p → X q)` | p immediately followed by q | Immediate response required |

## Computation Tree Logic (CTL)

CTL expresses properties over a **tree** of all possible executions from a given state.

### Path Quantifiers

- **A**: "Along **A**ll paths" - universal quantifier
- **E**: "Along some (**E**xists) path" - existential quantifier

### CTL Syntax Rules

**Every temporal operator (F, G, X, U) must be immediately preceded by either A or E.**

Valid CTL:
- `AG p` - Always globally p
- `EF p` - Eventually p on some path  
- `AX p` - Next p on all paths

Invalid CTL:
- `A(FG p)` - F not immediately preceded by quantifier
- `GF p` - Missing path quantifier entirely

### Common CTL Patterns

| Pattern | Meaning |
|---------|---------|
| `AG p` | p holds on all paths at all times |
| `EF p` | There exists a path where p eventually holds |
| `AF p` | On all paths, p eventually holds |
| `EG p` | There exists a path where p always holds |

### CTL Examples

**Deadlock Freedom**: `AG EX true`
- "Always globally, there exists a next state"
- Every reachable state has at least one outgoing transition

**Reachability**: `AG(EF reset)`
- "Always globally, there exists a path to reset"
- From any state, it's possible to reach the reset state

## LTL vs CTL Comparison

### Expressiveness
- **LTL and CTL have different expressive powers** - neither subsumes the other
- **CTL\*** subsumes both LTL and CTL

### Examples of Differences

| Property | LTL | CTL | Expressible? |
|----------|-----|-----|--------------|
| `GF p` (infinitely often) | ✓ | ✗ | LTL only |
| `AG EF p` (always possible) | ✗ | ✓ | CTL only |
| Fairness constraints | ✓ | ✗ | LTL only |

### Computational Complexity

| Logic | Model Checking Complexity |
|-------|-------------------------|
| CTL | **Linear** in formula size |
| LTL | **Exponential** in formula size |
| Both | Linear in state graph size |

### CTL as LTL Approximation

CTL can approximate LTL properties:

- `AG EF p` is **weaker** than `GF p`
  - Useful for finding bugs (if CTL fails, LTL fails)
- `AF AG p` is **stronger** than `FG p`  
  - Useful for correctness (if CTL passes, gives confidence)

## Practical Examples

### Cache Coherence
**Property**: "No more than one processor should have cache line in write mode"

**Variables**: `wr1`, `wr2` (processor 1/2 has write access)

**LTL**: `G(¬(wr1 ∧ wr2))`  
**CTL**: `AG(¬(wr1 ∧ wr2))`

### Request-Grant Protocol
**Property**: "Grant signal must be asserted sometime after request"

**Variables**: `req`, `grant`

**LTL**: `G(req → F grant)`  
**CTL**: `AG(req → AF grant)`

### Request-Acknowledge Protocol  
**Property**: "Every request gets acknowledge, request stays until ack"

**Variables**: `req`, `ack`

**LTL**: `G(req → (req U ack))`  
**CTL**: `AG(req → A(req U ack))`

## Key Insights

### When to Use What

**Use LTL when**:
- Reasoning about individual execution traces
- Expressing fairness properties
- Natural linear-time properties (request-response patterns)

**Use CTL when**:
- Reasoning about branching behavior
- Need efficient model checking
- Properties about existence of paths

### Practical Considerations

- **Most properties in practice are safety properties**
- **LTL is more intuitive** but computationally expensive
- **CTL is less expressive** but more tractable
- **The complexity difference matters** in real verification

## Further Reading

- [Model Checking by Clarke, Grumberg, and Peled](https://mitpress.mit.edu/books/model-checking)
- [Principles of Model Checking by Baier and Katoen](https://mitpress.mit.edu/books/principles-model-checking)
- [TLA+ specification language](https://lamport.azurewebsites.net/tla/tla.html)
- [SPIN model checker](http://spinroot.com/)

## Contributing

Feel free to submit issues and enhancement requests! This tutorial aims to make temporal logic accessible to practitioners.

## License

This educational content is based on academic materials and is shared for learning purposes.
