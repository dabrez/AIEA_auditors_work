class Term:
    """Represents a term that can be a constant, variable, or compound term."""
    def __init__(self, name, args=None):
        self.name = name
        self.args = args or []
        self.is_variable = name.isupper() if isinstance(name, str) else False
    
    def __str__(self):
        if self.args:
            args_str = ", ".join(str(arg) for arg in self.args)
            return f"{self.name}({args_str})"
        return str(self.name)
    
    def __eq__(self, other):
        return (isinstance(other, Term) and 
                self.name == other.name and 
                self.args == other.args)
    
    def __hash__(self):
        return hash((self.name, tuple(self.args)))

class Clause:
    """Represents a clause: either a fact or a rule (head :- body)."""
    def __init__(self, head, body=None):
        self.head = head  # Term
        self.body = body or []  # List of Terms (empty for facts)
    
    def is_fact(self):
        return len(self.body) == 0
    
    def is_rule(self):
        return len(self.body) > 0
    
    def __str__(self):
        if self.is_fact():
            return str(self.head)
        else:
            body_str = ", ".join(str(term) for term in self.body)
            return f"{self.head} :- {body_str}"

class KnowledgeBase:
    """A knowledge base containing facts and rules."""
    
    def __init__(self):
        self.clauses = []  # List of Clause objects
        self.facts = set()  # Cache of ground facts for quick lookup
    
    def add_fact(self, predicate, *args):
        """Add a fact to the knowledge base."""
        term = Term(predicate, list(args))
        clause = Clause(term)
        self.clauses.append(clause)
        if not any(arg for arg in args if isinstance(arg, str) and arg.isupper()):
            # Only cache ground facts (no variables)
            self.facts.add(term)
    
    def add_rule(self, head_pred, head_args, body_conditions):
        """Add a rule to the knowledge base.
        
        Args:
            head_pred: predicate name for the head
            head_args: arguments for the head
            body_conditions: list of (predicate, args) tuples for the body
        """
        head = Term(head_pred, head_args)
        body = [Term(pred, args) for pred, args in body_conditions]
        clause = Clause(head, body)
        self.clauses.append(clause)
    
    def get_matching_clauses(self, goal):
        """Get all clauses whose head could potentially match the goal."""
        matching = []
        for clause in self.clauses:
            if clause.head.name == goal.name and len(clause.head.args) == len(goal.args):
                matching.append(clause)
        return matching
    
    def print_knowledge_base(self):
        """Print all facts and rules in the knowledge base."""
        print("Knowledge Base:")
        print("Facts:")
        for clause in self.clauses:
            if clause.is_fact():
                print(f"  {clause}")
        
        print("Rules:")
        for clause in self.clauses:
            if clause.is_rule():
                print(f"  {clause}")

class Unification:
    """Handles unification of terms with variables."""
    
    @staticmethod
    def unify(term1, term2, substitution=None):
        """Attempt to unify two terms. Returns substitution dict or None if impossible."""
        if substitution is None:
            substitution = {}
        
        # Apply existing substitutions
        term1 = Unification.substitute(term1, substitution)
        term2 = Unification.substitute(term2, substitution)
        
        # Same terms unify
        if term1 == term2:
            return substitution
        
        # Variable unification
        if term1.is_variable:
            if term1.name in substitution:
                return Unification.unify(substitution[term1.name], term2, substitution)
            else:
                substitution[term1.name] = term2
                return substitution
        
        if term2.is_variable:
            if term2.name in substitution:
                return Unification.unify(term1, substitution[term2.name], substitution)
            else:
                substitution[term2.name] = term1
                return substitution
        
        # Compound term unification
        if (term1.name == term2.name and 
            len(term1.args) == len(term2.args)):
            for arg1, arg2 in zip(term1.args, term2.args):
                arg1_term = Term(arg1) if not isinstance(arg1, Term) else arg1
                arg2_term = Term(arg2) if not isinstance(arg2, Term) else arg2
                substitution = Unification.unify(arg1_term, arg2_term, substitution)
                if substitution is None:
                    return None
            return substitution
        
        return None  # Cannot unify
    
    @staticmethod
    def substitute(term, substitution):
        """Apply substitution to a term."""
        if term.is_variable and term.name in substitution:
            return substitution[term.name]
        
        if term.args:
            new_args = []
            for arg in term.args:
                if isinstance(arg, Term):
                    new_args.append(Unification.substitute(arg, substitution))
                elif isinstance(arg, str) and arg.isupper() and arg in substitution:
                    new_args.append(substitution[arg])
                else:
                    new_args.append(arg)
            return Term(term.name, new_args)
        
        return term

class BackwardsChainingEngine:
    """A backwards chaining inference engine with unification."""
    
    def __init__(self, knowledge_base):
        self.kb = knowledge_base
        self.trace = []
        self.call_stack = []  # To prevent infinite recursion
    
    def prove(self, goal, substitution=None, depth=0):
        """
        Attempt to prove a goal using backwards chaining with unification.
        Returns list of successful substitutions.
        """
        if substitution is None:
            substitution = {}
        
        indent = "  " * depth
        goal_str = str(Unification.substitute(goal, substitution))
        self.trace.append(f"{indent}Trying to prove: {goal_str}")
        
        # Check for infinite recursion
        if (goal, tuple(sorted(substitution.items()))) in self.call_stack:
            self.trace.append(f"{indent}✗ Infinite recursion detected")
            return []
        
        self.call_stack.append((goal, tuple(sorted(substitution.items()))))
        
        solutions = []
        
        # Get all potentially matching clauses
        matching_clauses = self.kb.get_matching_clauses(goal)
        
        for clause in matching_clauses:
            # Rename variables in the clause to avoid conflicts
            renamed_clause = self._rename_variables(clause, depth)
            
            # Try to unify the goal with the clause head
            unified_sub = Unification.unify(goal, renamed_clause.head, substitution.copy())
            
            if unified_sub is not None:
                self.trace.append(f"{indent}Unified with: {renamed_clause}")
                
                if renamed_clause.is_fact():
                    # It's a fact, we're done
                    self.trace.append(f"{indent}✓ Fact proven: {goal_str}")
                    solutions.append(unified_sub)
                else:
                    # It's a rule, need to prove all body conditions
                    self.trace.append(f"{indent}Proving body conditions...")
                    body_solutions = self._prove_body(renamed_clause.body, unified_sub, depth + 1)
                    solutions.extend(body_solutions)
        
        self.call_stack.pop()
        
        if not solutions:
            self.trace.append(f"{indent}✗ Cannot prove: {goal_str}")
        
        return solutions
    
    def _prove_body(self, body_conditions, substitution, depth):
        """Prove all conditions in the body of a rule."""
        if not body_conditions:
            return [substitution]
        
        solutions = []
        first_condition = body_conditions[0]
        remaining_conditions = body_conditions[1:]
        
        # Prove the first condition
        first_solutions = self.prove(first_condition, substitution, depth)
        
        # For each solution of the first condition, prove the remaining ones
        for solution in first_solutions:
            remaining_solutions = self._prove_body(remaining_conditions, solution, depth)
            solutions.extend(remaining_solutions)
        
        return solutions
    
    def _rename_variables(self, clause, suffix):
        """Rename variables in a clause to avoid conflicts."""
        var_mapping = {}
        
        def rename_term(term):
            if term.is_variable:
                if term.name not in var_mapping:
                    var_mapping[term.name] = f"{term.name}_{suffix}"
                return Term(var_mapping[term.name])
            elif term.args:
                new_args = []
                for arg in term.args:
                    if isinstance(arg, Term):
                        new_args.append(rename_term(arg))
                    elif isinstance(arg, str) and arg.isupper():
                        if arg not in var_mapping:
                            var_mapping[arg] = f"{arg}_{suffix}"
                        new_args.append(var_mapping[arg])
                    else:
                        new_args.append(arg)
                return Term(term.name, new_args)
            return term
        
        new_head = rename_term(clause.head)
        new_body = [rename_term(term) for term in clause.body]
        return Clause(new_head, new_body)
    
    def query(self, predicate, *args):
        """Query the knowledge base."""
        self.trace = []
        self.call_stack = []
        goal = Term(predicate, list(args))
        solutions = self.prove(goal)
        return solutions, self.trace

# Example usage with family relationships
def demo_family_relationships():
    """Demonstrate backwards chaining with family relationships."""
    print("=== Family Relationships Demo ===\n")
    
    # Create knowledge base
    kb = KnowledgeBase()
    
    # Add facts about family relationships
    kb.add_fact("parent", "john", "mary")
    kb.add_fact("parent", "john", "tom")
    kb.add_fact("parent", "mary", "alice")
    kb.add_fact("parent", "mary", "bob")
    kb.add_fact("parent", "tom", "charlie")
    kb.add_fact("parent", "susan", "john")
    kb.add_fact("male", "john")
    kb.add_fact("male", "tom")
    kb.add_fact("male", "bob")
    kb.add_fact("male", "charlie")
    kb.add_fact("female", "mary")
    kb.add_fact("female", "alice")
    kb.add_fact("female", "susan")
    
    # Add rules
    kb.add_rule("grandparent", ["X", "Z"], [("parent", ["X", "Y"]), ("parent", ["Y", "Z"])])
    kb.add_rule("sibling", ["X", "Y"], [("parent", ["Z", "X"]), ("parent", ["Z", "Y"])])
    kb.add_rule("uncle", ["X", "Y"], [("sibling", ["X", "Z"]), ("parent", ["Z", "Y"]), ("male", ["X"])])
    kb.add_rule("aunt", ["X", "Y"], [("sibling", ["X", "Z"]), ("parent", ["Z", "Y"]), ("female", ["X"])])
    kb.add_rule("ancestor", ["X", "Y"], [("parent", ["X", "Y"])])
    kb.add_rule("ancestor", ["X", "Y"], [("parent", ["X", "Z"]), ("ancestor", ["Z", "Y"])])
    
    kb.print_knowledge_base()
    
    # Create inference engine
    engine = BackwardsChainingEngine(kb)
    
    # Test queries
    queries = [
        ("grandparent", "john", "alice"),
        ("grandparent", "susan", "mary"),
        ("sibling", "mary", "tom"),
        ("uncle", "tom", "alice"),
        ("ancestor", "john", "charlie"),
        ("aunt", "mary", "charlie")
    ]
    
    print("\n" + "="*50)
    print("QUERY RESULTS")
    print("="*50)
    
    for query in queries:
        print(f"\nQuery: {query[0]}({', '.join(query[1:])})")
        solutions, trace = engine.query(*query)
        
        if solutions:
            print(f"✓ PROVEN ({len(solutions)} solution(s))")
            for i, solution in enumerate(solutions, 1):
                if solution:
                    print(f"  Solution {i}: {solution}")
                else:
                    print(f"  Solution {i}: True")
        else:
            print("✗ NOT PROVEN")
        
        print("Reasoning trace:")
        for step in trace:
            print(step)
        print("-" * 30)

def demo_animal_classification():
    """Demonstrate with animal classification using variables."""
    print("\n\n=== Animal Classification Demo ===\n")
    
    kb = KnowledgeBase()
    
    # Facts about specific animals
    kb.add_fact("has_feathers", "tweety")
    kb.add_fact("can_fly", "tweety")
    kb.add_fact("has_fur", "fido")
    kb.add_fact("barks", "fido")
    kb.add_fact("has_scales", "nemo")
    kb.add_fact("swims", "nemo")
    
    # Rules about animal classification
    kb.add_rule("bird", ["X"], [("has_feathers", ["X"]), ("can_fly", ["X"])])
    kb.add_rule("mammal", ["X"], [("has_fur", ["X"])])
    kb.add_rule("dog", ["X"], [("mammal", ["X"]), ("barks", ["X"])])
    kb.add_rule("fish", ["X"], [("has_scales", ["X"]), ("swims", ["X"])])
    kb.add_rule("warm_blooded", ["X"], [("bird", ["X"])])
    kb.add_rule("warm_blooded", ["X"], [("mammal", ["X"])])
    kb.add_rule("can_move", ["X"], [("bird", ["X"])])
    kb.add_rule("can_move", ["X"], [("mammal", ["X"])])
    kb.add_rule("can_move", ["X"], [("fish", ["X"])])
    
    kb.print_knowledge_base()
    
    engine = BackwardsChainingEngine(kb)
    
    queries = [
        ("bird", "tweety"),
        ("dog", "fido"),
        ("fish", "nemo"),
        ("warm_blooded", "tweety"),
        ("warm_blooded", "fido"),
        ("can_move", "nemo")
    ]
    
    print("\n" + "="*50)
    print("ANIMAL CLASSIFICATION RESULTS")
    print("="*50)
    
    for query in queries:
        print(f"\nQuery: {query[0]}({', '.join(query[1:])})")
        solutions, trace = engine.query(*query)
        
        if solutions:
            print(f"✓ PROVEN")
        else:
            print("✗ NOT PROVEN")
        
        print("Reasoning trace:")
        for step in trace:
            print(step)
        print("-" * 30)

if __name__ == "__main__":
    demo_family_relationships()
    demo_animal_classification()
