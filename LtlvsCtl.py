"""
LTL vs CTL Demonstration
Shows the differences between Linear Temporal Logic and Computation Tree Logic
through a simple state machine and property evaluation.
"""

from typing import Dict, List, Set, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import itertools

class State:
    """Represents a state in our system with atomic propositions."""
    def __init__(self, name: str, props: Set[str]):
        self.name = name
        self.props = props  # Set of atomic propositions true in this state
        
    def __str__(self):
        return f"{self.name}({', '.join(sorted(self.props))})"
    
    def __repr__(self):
        return self.__str__()

class StateMachine:
    """A simple state machine for demonstrating temporal logic."""
    
    def __init__(self):
        self.states: Dict[str, State] = {}
        self.transitions: Dict[str, List[str]] = {}
        self.initial_state: Optional[str] = None
    
    def add_state(self, name: str, props: Set[str]):
        """Add a state with its atomic propositions."""
        self.states[name] = State(name, props)
        if name not in self.transitions:
            self.transitions[name] = []
    
    def add_transition(self, from_state: str, to_state: str):
        """Add a transition between states."""
        if from_state not in self.transitions:
            self.transitions[from_state] = []
        self.transitions[from_state].append(to_state)
    
    def set_initial(self, state: str):
        """Set the initial state."""
        self.initial_state = state
    
    def get_successors(self, state: str) -> List[str]:
        """Get all successor states."""
        return self.transitions.get(state, [])
    
    def has_prop(self, state: str, prop: str) -> bool:
        """Check if a proposition is true in a state."""
        return prop in self.states[state].props
    
    def generate_paths(self, start_state: str, max_length: int = 10) -> List[List[str]]:
        """Generate all possible paths up to max_length from start_state."""
        paths = []
        
        def dfs(current_path: List[str], visited_cycles: Set[Tuple[str, ...]]):
            if len(current_path) > max_length:
                return
            
            current_state = current_path[-1]
            successors = self.get_successors(current_state)
            
            if not successors:  # Dead end
                paths.append(current_path.copy())
                return
            
            for next_state in successors:
                new_path = current_path + [next_state]
                
                # Detect cycles to avoid infinite recursion
                if len(new_path) >= 3:
                    cycle_check = tuple(new_path[-3:])
                    if cycle_check in visited_cycles:
                        paths.append(new_path)
                        continue
                    visited_cycles.add(cycle_check)
                
                dfs(new_path, visited_cycles)
        
        dfs([start_state], set())
        return paths

class LTLEvaluator:
    """Evaluates LTL formulas on linear paths."""
    
    def __init__(self, state_machine: StateMachine):
        self.sm = state_machine
    
    def eventually(self, path: List[str], prop: str, start_pos: int = 0) -> bool:
        """F prop: Eventually prop holds along the path."""
        for i in range(start_pos, len(path)):
            if self.sm.has_prop(path[i], prop):
                return True
        return False
    
    def globally(self, path: List[str], prop: str, start_pos: int = 0) -> bool:
        """G prop: Globally prop holds along the path."""
        for i in range(start_pos, len(path)):
            if not self.sm.has_prop(path[i], prop):
                return False
        return True
    
    def next_state(self, path: List[str], prop: str, pos: int) -> bool:
        """X prop: Next state satisfies prop."""
        if pos + 1 < len(path):
            return self.sm.has_prop(path[pos + 1], prop)
        return False
    
    def until(self, path: List[str], prop1: str, prop2: str, start_pos: int = 0) -> bool:
        """prop1 U prop2: prop1 until prop2."""
        for i in range(start_pos, len(path)):
            if self.sm.has_prop(path[i], prop2):
                return True
            if not self.sm.has_prop(path[i], prop1):
                return False
        return False
    
    def evaluate_on_all_paths(self, formula_name: str, formula_func) -> Dict[str, bool]:
        """Evaluate a formula on all paths from initial state."""
        if not self.sm.initial_state:
            return {}
        
        paths = self.sm.generate_paths(self.sm.initial_state)
        results = {}
        
        for i, path in enumerate(paths):
            result = formula_func(path)
            results[f"Path {i+1}: {' → '.join(path)}"] = result
        
        return results

class CTLEvaluator:
    """Evaluates CTL formulas on state trees."""
    
    def __init__(self, state_machine: StateMachine):
        self.sm = state_machine
    
    def exists_eventually(self, state: str, prop: str, visited: Set[str] = None) -> bool:
        """EF prop: There exists a path where prop eventually holds."""
        if visited is None:
            visited = set()
        
        if state in visited:  # Cycle detection
            return False
        
        if self.sm.has_prop(state, prop):
            return True
        
        visited.add(state)
        successors = self.sm.get_successors(state)
        
        for next_state in successors:
            if self.exists_eventually(next_state, prop, visited.copy()):
                return True
        
        return False
    
    def all_eventually(self, state: str, prop: str, visited: Set[str] = None) -> bool:
        """AF prop: On all paths, prop eventually holds."""
        if visited is None:
            visited = set()
        
        if state in visited:  # Cycle without prop - fails
            return False
        
        if self.sm.has_prop(state, prop):
            return True
        
        successors = self.sm.get_successors(state)
        if not successors:  # Dead end without prop
            return False
        
        visited.add(state)
        
        for next_state in successors:
            if not self.all_eventually(next_state, prop, visited.copy()):
                return False
        
        return True
    
    def all_globally(self, state: str, prop: str, visited: Set[str] = None) -> bool:
        """AG prop: On all paths, prop always holds."""
        if visited is None:
            visited = set()
        
        if not self.sm.has_prop(state, prop):
            return False
        
        if state in visited:  # Safe cycle
            return True
        
        visited.add(state)
        successors = self.sm.get_successors(state)
        
        for next_state in successors:
            if not self.all_globally(next_state, prop, visited.copy()):
                return False
        
        return True
    
    def exists_globally(self, state: str, prop: str, visited: Set[str] = None) -> bool:
        """EG prop: There exists a path where prop always holds."""
        if visited is None:
            visited = set()
        
        if not self.sm.has_prop(state, prop):
            return False
        
        if state in visited:  # Found a cycle where prop holds
            return True
        
        visited.add(state)
        successors = self.sm.get_successors(state)
        
        for next_state in successors:
            if self.exists_globally(next_state, prop, visited.copy()):
                return True
        
        return False

def create_example_system() -> StateMachine:
    """Create an example system: a simple request-response protocol."""
    sm = StateMachine()
    
    # States: idle, requesting, processing, responding
    sm.add_state("idle", {"idle"})
    sm.add_state("requesting", {"req", "active"})
    sm.add_state("processing", {"req", "active", "busy"})
    sm.add_state("responding", {"ack", "active"})
    sm.add_state("error", {"error"})
    
    # Transitions
    sm.add_transition("idle", "requesting")
    sm.add_transition("requesting", "processing")
    sm.add_transition("requesting", "error")  # Can fail
    sm.add_transition("processing", "responding")
    sm.add_transition("responding", "idle")
    sm.add_transition("error", "idle")  # Recovery possible
    
    sm.set_initial("idle")
    return sm

def demonstrate_ltl_vs_ctl():
    """Demonstrate the differences between LTL and CTL."""
    
    print("=== LTL vs CTL Demonstration ===\n")
    
    # Create example system
    sm = create_example_system()
    ltl_eval = LTLEvaluator(sm)
    ctl_eval = CTLEvaluator(sm)
    
    print("System States:")
    for name, state in sm.states.items():
        print(f"  {state}")
    
    print("\nTransitions:")
    for from_state, to_states in sm.transitions.items():
        for to_state in to_states:
            print(f"  {from_state} → {to_state}")
    
    print(f"\nInitial state: {sm.initial_state}")
    
    # Generate some paths
    paths = sm.generate_paths(sm.initial_state, max_length=6)
    print(f"\nSample paths from initial state:")
    for i, path in enumerate(paths[:5]):  # Show first 5 paths
        print(f"  Path {i+1}: {' → '.join(path)}")
    
    print("\n" + "="*60)
    print("PROPERTY EVALUATION")
    print("="*60)
    
    # Property 1: Eventually acknowledge (EF ack vs AF ack)
    print("\n1. EVENTUALLY ACKNOWLEDGE")
    print("   LTL: F ack (eventually ack on some path)")
    print("   CTL: EF ack vs AF ack\n")
    
    # LTL: Check on all paths
    ltl_results = ltl_eval.evaluate_on_all_paths(
        "F ack", 
        lambda path: ltl_eval.eventually(path, "ack")
    )
    
    print("   LTL Results (F ack on each path):")
    for path, result in ltl_results.items():
        print(f"     {path}: {result}")
    
    # CTL: Check on state tree
    ef_ack = ctl_eval.exists_eventually("idle", "ack")
    af_ack = ctl_eval.all_eventually("idle", "ack")
    
    print(f"\n   CTL Results from initial state:")
    print(f"     EF ack (exists path with eventual ack): {ef_ack}")
    print(f"     AF ack (all paths eventually ack): {af_ack}")
    
    # Property 2: Always no error (AG ¬error vs G ¬error)
    print("\n2. SAFETY: NO ERROR")
    print("   LTL: G ¬error (always no error on a path)")
    print("   CTL: AG ¬error (always no error on all paths)\n")
    
    # LTL: Check on all paths
    ltl_safety = ltl_eval.evaluate_on_all_paths(
        "G ¬error",
        lambda path: ltl_eval.globally(path, "error") == False
    )
    
    print("   LTL Results (G ¬error on each path):")
    for path, result in ltl_safety.items():
        print(f"     {path}: {result}")
    
    # CTL: Check on state tree
    ag_not_error = ctl_eval.all_globally("idle", "error") == False
    
    print(f"\n   CTL Results from initial state:")
    print(f"     AG ¬error (no error on all paths): {ag_not_error}")
    
    # Property 3: Infinitely often active (shows LTL vs CTL difference)
    print("\n3. LIVENESS: INFINITELY OFTEN ACTIVE")
    print("   This shows a key difference between LTL and CTL")
    print("   LTL: GF active (infinitely often active)")
    print("   CTL: AG EF active (always possible to reach active)\n")
    
    # For LTL GF, we'd need infinite paths, so we approximate
    print("   LTL approximation: checking if 'active' appears multiple times")
    
    def check_multiple_active(path):
        count = sum(1 for state in path if sm.has_prop(state, "active"))
        return count >= 2
    
    ltl_gf_approx = ltl_eval.evaluate_on_all_paths(
        "Multiple active (GF approximation)",
        check_multiple_active
    )
    
    print("   LTL Results (approximated GF active):")
    for path, result in ltl_gf_approx.items():
        print(f"     {path}: {result}")
    
    # CTL: AG EF active
    def ag_ef_active(state, visited=None):
        """AG EF active: always globally, exists eventually active"""
        if visited is None:
            visited = set()
        if state in visited:
            return True  # Cycle is okay for AG EF
        
        # EF active from current state
        if not ctl_eval.exists_eventually(state, "active"):
            return False
        
        visited.add(state)
        successors = sm.get_successors(state)
        
        for next_state in successors:
            if not ag_ef_active(next_state, visited.copy()):
                return False
        return True
    
    ag_ef_result = ag_ef_active("idle")
    print(f"\n   CTL Results from initial state:")
    print(f"     AG EF active (always possible to reach active): {ag_ef_result}")
    
    print("\n" + "="*60)
    print("KEY INSIGHTS")
    print("="*60)
    print("""
1. LTL reasons about individual paths - each path either satisfies or doesn't
2. CTL reasons about the tree structure - exists vs all path quantifiers
3. LTL 'GF p' (infinitely often) cannot be expressed in CTL
4. CTL 'AG EF p' (always possible) cannot be expressed in LTL
5. CTL is computationally cheaper to check than LTL
""")

if __name__ == "__main__":
    demonstrate_ltl_vs_ctl()