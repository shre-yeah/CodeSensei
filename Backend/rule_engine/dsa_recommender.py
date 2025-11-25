"""
DSA Learning Recommendation Engine - Rule-based Prototype
Provides concept and problem recommendations based on user progress
"""

class DSARecommender:
    def __init__(self):
        # Concept dependency graph: concept -> prerequisites and next concepts
        self.concept_graph = {
            "basics":
            {
                "prerequisites": ["Basic Programming Concepts", "Data Types", "Control Structures", "Loops", "Functions"],
                "next_concepts": ["arrays", "hashing", "linked_lists", "stacks", "queues", "recursion", "trees" ],
                "difficulty": "easy"
            },
             "insertion sort":{
                "prerequisites": ["arrays"," basics"],
                "next_concepts": ["selection sort", "bubble sort", "merge sort"],
                "difficulty": "easy"
            },
            "selection sort":{
                "prerequisites": ["insertion sort"],  
                "next_concepts": ["bubble sort", "merge sort"],
                "difficulty": "easy"
            },
            "bubble sort":{
                "prerequisites": ["selection sort"],  
                "next_concepts": ["merge sort", "quick sort"],
                "difficulty": "easy"
            },
            "merge sort":{
                "prerequisites": ["bubble sort"],  
                "next_concepts": ["quick sort", "heap sort"],
                "difficulty": "medium"
            },
            "quick sort":{
                "prerequisites": ["merge sort"],  
                "next_concepts": ["heap sort"],
                "difficulty": "medium"
            },
            "heap sort":{
                "prerequisites": ["quick sort"],  
                "next_concepts": ["counting sort", "binary search"],
                "difficulty": "medium"
            },
            
            "arrays": {
                "prerequisites": ["basics", "insertion sort", "bubble sort", "merge sort", "quick sort"],
                "next_concepts": ["binary search","two_pointers", "sliding_window", "prefix_sum"],
                "difficulty": "easy"
            },
           
            "two_pointers": {
                "prerequisites": ["arrays"],
                "next_concepts": ["sliding_window", "fast_slow_pointers"],
                "difficulty": "easy"
            },
            "sliding_window": {
                "prerequisites": ["arrays", "two_pointers"],
                "next_concepts": ["prefix_sum", "monotonic_queue", "strings"],
                "difficulty": "medium"
            },
            "strings": {
                "prerequisites": ["arrays", "hashing"],
                "next_concepts": ["linked_lists"],
                "difficulty": "easy"
            },
            "hashing": {
                "prerequisites": [],
                "next_concepts": ["two_sum_pattern", "frequency_counting"],
                "difficulty": "easy"
            },
            "linked_lists": {
                "prerequisites": [],
                "next_concepts": ["fast_slow_pointers", "reverse_linked_list"],
                "difficulty": "easy"
            },
            "fast_slow_pointers": {
                "prerequisites": ["linked_lists"],
                "next_concepts": ["cycle_detection", "middle_element"],
                "difficulty": "medium"
            },
            "stacks": {
                "prerequisites": [],
                "next_concepts": ["monotonic_stack", "next_greater_element"],
                "difficulty": "easy"
            },
            "queues": {
                "prerequisites": [],
                "next_concepts": ["bfs", "sliding_window_maximum"],
                "difficulty": "easy"
            },
            "binary_search": {
                "prerequisites": ["arrays"],
                "next_concepts": ["binary_search_answer", "rotated_array"],
                "difficulty": "medium"
            },
            "recursion": {
                "prerequisites": [],
                "next_concepts": ["backtracking", "divide_conquer"],
                "difficulty": "medium"
            },
            "backtracking": {
                "prerequisites": ["recursion"],
                "next_concepts": ["permutations", "combinations", "n_queens"],
                "difficulty": "hard"
            },
            "trees": {
                "prerequisites": [],
                "next_concepts": ["binary_trees", "tree_traversal"],
                "difficulty": "easy"
            },
            "binary_trees": {
                "prerequisites": ["trees"],
                "next_concepts": ["bst", "dfs", "bfs"],
                "difficulty": "medium"
            },
            "bst": {
                "prerequisites": ["binary_trees"],
                "next_concepts": ["inorder_traversal", "validate_bst"],
                "difficulty": "medium"
            },
            "dfs": {
                "prerequisites": ["trees", "recursion"],
                "next_concepts": ["graph_dfs", "tree_dp"],
                "difficulty": "medium"
            },
            "bfs": {
                "prerequisites": ["trees", "queues"],
                "next_concepts": ["level_order", "graph_bfs"],
                "difficulty": "medium"
            },
            "graphs": {
                "prerequisites": ["dfs", "bfs"],
                "next_concepts": ["graph_traversal", "shortest_path", "topological_sort"],
                "difficulty": "hard"
            },
            "dynamic_programming": {
                "prerequisites": ["recursion"],
                "next_concepts": ["1d_dp", "2d_dp", "knapsack"],
                "difficulty": "hard"
            },
            "heaps": {
                "prerequisites": ["binary_trees"],
                "next_concepts": ["priority_queue", "top_k_elements"],
                "difficulty": "medium"
            },
            "tries": {
                "prerequisites": ["trees", "hashing"],
                "next_concepts": ["word_search", "prefix_matching"],
                "difficulty": "medium"
            }
        }
        
        # Problem database: problem -> concepts, difficulty, similar problems
        self.problems = {
            "two_sum": {
                "concepts": ["arrays", "hashing"],
                "difficulty": "easy",
                "pattern": "two_sum_pattern",
                "similar": ["three_sum", "four_sum", "two_sum_ii"]
            },
            "three_sum": {
                "concepts": ["arrays", "two_pointers", "sorting"],
                "difficulty": "medium",
                "pattern": "two_sum_pattern",
                "similar": ["two_sum", "four_sum", "three_sum_closest"]
            },
            "best_time_to_buy_sell_stock": {
                "concepts": ["arrays", "sliding_window"],
                "difficulty": "easy",
                "pattern": "kadane",
                "similar": ["max_subarray", "best_time_ii", "best_time_iii"]
            },
            "maximum_subarray": {
                "concepts": ["arrays", "dynamic_programming"],
                "difficulty": "medium",
                "pattern": "kadane",
                "similar": ["best_time_to_buy_sell_stock", "maximum_product_subarray"]
            },
            "reverse_linked_list": {
                "concepts": ["linked_lists"],
                "difficulty": "easy",
                "pattern": "linked_list_reversal",
                "similar": ["reverse_linked_list_ii", "reverse_nodes_k_group"]
            },
            "linked_list_cycle": {
                "concepts": ["linked_lists", "fast_slow_pointers"],
                "difficulty": "easy",
                "pattern": "cycle_detection",
                "similar": ["linked_list_cycle_ii", "happy_number", "find_duplicate"]
            },
            "merge_two_sorted_lists": {
                "concepts": ["linked_lists", "recursion"],
                "difficulty": "easy",
                "pattern": "merge",
                "similar": ["merge_k_sorted_lists", "merge_sorted_array"]
            },
            "valid_parentheses": {
                "concepts": ["stacks"],
                "difficulty": "easy",
                "pattern": "stack_matching",
                "similar": ["generate_parentheses", "longest_valid_parentheses"]
            },
            "binary_search": {
                "concepts": ["binary_search", "arrays"],
                "difficulty": "easy",
                "pattern": "binary_search_basic",
                "similar": ["search_insert", "find_first_last", "search_2d_matrix"]
            },
            "binary_tree_inorder": {
                "concepts": ["binary_trees", "dfs", "recursion"],
                "difficulty": "easy",
                "pattern": "tree_traversal",
                "similar": ["preorder_traversal", "postorder_traversal", "level_order"]
            },
            "validate_bst": {
                "concepts": ["bst", "dfs", "recursion"],
                "difficulty": "medium",
                "pattern": "bst_validation",
                "similar": ["kth_smallest_bst", "inorder_successor_bst"]
            },
            "lowest_common_ancestor": {
                "concepts": ["binary_trees", "dfs", "recursion"],
                "difficulty": "medium",
                "pattern": "lca",
                "similar": ["lca_bst", "lca_deepest_leaves"]
            },
            "number_of_islands": {
                "concepts": ["graphs", "dfs", "bfs"],
                "difficulty": "medium",
                "pattern": "graph_traversal",
                "similar": ["max_area_island", "surrounded_regions", "pacific_atlantic"]
            },
            "coin_change": {
                "concepts": ["dynamic_programming"],
                "difficulty": "medium",
                "pattern": "unbounded_knapsack",
                "similar": ["coin_change_ii", "min_cost_climbing_stairs", "perfect_squares"]
            },
            "climbing_stairs": {
                "concepts": ["dynamic_programming", "recursion"],
                "difficulty": "easy",
                "pattern": "1d_dp",
                "similar": ["fibonacci", "house_robber", "min_cost_climbing_stairs"]
            },
            "permutations": {
                "concepts": ["backtracking", "recursion"],
                "difficulty": "medium",
                "pattern": "permutation",
                "similar": ["permutations_ii", "combinations", "subsets"]
            },
            "subsets": {
                "concepts": ["backtracking", "recursion"],
                "difficulty": "medium",
                "pattern": "subset",
                "similar": ["subsets_ii", "combinations", "permutations"]
            },
            "top_k_frequent": {
                "concepts": ["heaps", "hashing"],
                "difficulty": "medium",
                "pattern": "top_k",
                "similar": ["kth_largest", "top_k_frequent_words", "sort_characters_frequency"]
            }
        }
        
        # Pattern to concept mapping
        self.pattern_concepts = {
            "two_sum_pattern": ["hashing", "two_pointers"],
            "sliding_window": ["arrays", "two_pointers"],
            "fast_slow_pointers": ["linked_lists"],
            "binary_search_basic": ["binary_search", "arrays"],
            "tree_traversal": ["binary_trees", "dfs", "bfs"],
            "graph_traversal": ["graphs", "dfs", "bfs"],
            "1d_dp": ["dynamic_programming", "recursion"],
            "backtracking": ["backtracking", "recursion"]
        }

    def normalize_input(self, text):
        """Normalize user input to match our database keys"""
        # Convert to lowercase and replace spaces with underscores
        return text.lower().strip().replace(" ", "_").replace("-", "_")

   

        
    def recommend_from_concepts(self, learned_concepts):
        """
        Given concepts user has learned, recommend next concepts and problems
        
        Args:
            learned_concepts: List of concept names
            
        Returns:
            dict with 'next_concepts' and 'problems_to_solve'
        """
        learned_set = set(self.normalize_input(c) for c in learned_concepts)
        next_concepts = set()
        recommended_problems = []
        
        # Find next concepts based on what's learned
        for concept in learned_set:
            if concept in self.concept_graph:
                # Add concepts that this unlocks
                for next_concept in self.concept_graph[concept]["next_concepts"]:
                    # Check if prerequisites are met
                    if next_concept in self.concept_graph:
                        prereqs = self.concept_graph[next_concept].get("prerequisites", [])
                        if all(p in learned_set for p in prereqs):
                            next_concepts.add(next_concept)
        
        # Find problems that match learned concepts
        for problem_name, problem_data in self.problems.items():
            problem_concepts = set(problem_data["concepts"])
            # If user knows all concepts for this problem
            if problem_concepts.issubset(learned_set):
                recommended_problems.append({
                    "name": problem_name,
                    "difficulty": problem_data["difficulty"],
                    "concepts": problem_data["concepts"],
                    "pattern": problem_data["pattern"]
                })
        
        # Sort problems by difficulty
        difficulty_order = {"easy": 0, "medium": 1, "hard": 2}
        recommended_problems.sort(key=lambda x: difficulty_order[x["difficulty"]])
        
        # Safely determine difficulty for a next concept (if any)
        next_list = sorted(list(next_concepts))
        difficulty = None
        if next_list:
            # pick the first valid next concept's difficulty if available
            difficulty = self.concept_graph.get(next_list[0], {}).get("difficulty")
        return {
            "next_concepts": next_list,
            "problems_to_solve": recommended_problems[:5],  # Limit to top 5
            "learned_concepts": list(learned_set),
            "difficulty": difficulty 
        }

    def recommend_from_problem(self, solved_problem):
        """
        Given a problem user solved, recommend similar problems and next concepts
        
        Args:
            solved_problem: Problem name
            
        Returns:
            dict with 'similar_problems', 'next_concepts', and 'concepts_learned'
        """
        problem_key = self.normalize_input(solved_problem)
        
        if problem_key not in self.problems:
            return {
                "error": f"Problem '{solved_problem}' not found in database",
                "suggestion": "Try problems like: two_sum, reverse_linked_list, valid_parentheses"
            }
        
        problem_data = self.problems[problem_key]
        concepts_used = problem_data["concepts"]
        
        # Find similar problems
        similar = []
        for sim_problem in problem_data["similar"]:
            if sim_problem in self.problems:
                similar.append({
                    "name": sim_problem,
                    "difficulty": self.problems[sim_problem]["difficulty"],
                    "concepts": self.problems[sim_problem]["concepts"]
                })
        
        # Find more problems with same pattern
        pattern_problems = []
        for prob_name, prob_data in self.problems.items():
            if (prob_data["pattern"] == problem_data["pattern"] and 
                prob_name != problem_key and 
                prob_name not in problem_data["similar"]):
                pattern_problems.append({
                    "name": prob_name,
                    "difficulty": prob_data["difficulty"],
                    "concepts": prob_data["concepts"]
                })
        
        # Recommend next concepts based on what was used
        next_concepts_rec = self.recommend_from_concepts(concepts_used)
        
        return {
            "concepts_learned": concepts_used,
            "similar_problems": similar[:5],
            "pattern_based_problems": pattern_problems[:5],
            "next_concepts": next_concepts_rec["next_concepts"][:5],
            "pattern": problem_data["pattern"],

            "difficulty": problem_data["difficulty"]
        }

    def get_learning_path(self, current_concepts, goal_concept):
        """
        Generate a learning path from current concepts to goal concept
        
        Args:
            current_concepts: List of concepts already learned
            goal_concept: Target concept to learn
            
        Returns:
            List of concepts in order to learn
        """
        goal = self.normalize_input(goal_concept)
        learned = set(self.normalize_input(c) for c in current_concepts)
        
        if goal not in self.concept_graph:
            return {"error": f"Concept '{goal_concept}' not found"}
        
        # Simple BFS to find path
        from collections import deque
        
        queue = deque([(goal, [goal])])
        visited = {goal}
        
        while queue:
            current, path = queue.popleft()
            
            if current in self.concept_graph:
                prereqs = self.concept_graph[current].get("prerequisites", [])
                
                # If all prereqs are learned, we found a path
                if all(p in learned for p in prereqs):
                    path.reverse()
                    return {
                        "learning_path": path,
                        "current_level": list(learned),
                        "goal": goal
                    }
                
                # Add prerequisites to explore
                for prereq in prereqs:
                    if prereq not in visited and prereq not in learned:
                        visited.add(prereq)
                        queue.append((prereq, path + [prereq]))
        
        return {
            "learning_path": [goal],
            "note": "All prerequisites already learned or no prerequisites needed"
        }


# Example usage
if __name__ == "__main__":
    recommender = DSARecommender()
    
    print("=" * 60)
    print("DSA LEARNING RECOMMENDATION ENGINE - DEMO")
    print("=" * 60)
    
    # Test 1: User learned some concepts
    print("\n📚 Test 1: I learned Arrays and Hashing today")
    print("-" * 60)
    result = recommender.recommend_from_concepts(["arrays", "hashing"])
    print(f"Next concepts to learn: {result['next_concepts']}")
    print(f"\nProblems you can solve ({len(result['problems_to_solve'])}):")
    for prob in result['problems_to_solve'][:5]:
        print(f"  - {prob['name']} [{prob['difficulty']}] (Pattern: {prob['pattern']})")
    
    # Test 2: User solved a problem
    print("\n\n🎯 Test 2: User solved 'Two Sum'")
    print("-" * 60)
    result = recommender.recommend_from_problem("two sum")
    print(f"Concepts learned: {result['concepts_learned']}")
    print(f"Pattern: {result['pattern']}")
    print(f"\nSimilar problems:")
    for prob in result['similar_problems']:
        print(f"  - {prob['name']} [{prob['difficulty']}]")
    print(f"\nNext concepts: {result['next_concepts']}")
    
    # Test 3: Learning path
    print("\n\n🗺️  Test 3: Learning path from Arrays to Dynamic Programming")
    print("-" * 60)
    result = recommender.get_learning_path(["arrays"], "dynamic_programming")
    print(f"Path: {' -> '.join(result['learning_path'])}")
    
    print("\n" + "=" * 60)