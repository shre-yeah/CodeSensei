"""
NLP Preprocessor for DSA Learning Platform
Extracts concepts and problem names from natural language user input
"""

import re
from typing import List, Dict, Tuple
from difflib import SequenceMatcher
from rapidfuzz import process, fuzz

class NLPPreprocessor:
    def __init__(self):
        # Keyword mappings for common ways users might refer to concepts
        self.concept_keywords = {
            "basics" :["basic", "basics", "fundamentals", "introduction", "intro"],
            "arrays": ["array", "arrays", "list", "lists"],
            "strings": ["string", "strings", "str"],
            "selection_sort": ["selection sort", "selection-sort"],
            "bubble_sort": ["bubble sort", "bubble-sort"],
            "insertion_sort": ["insertion sort", "insertion-sort"],
            "merge_sort": ["merge sort", "mergesort", "merge-sort"],
            "quick_sort": ["quick sort", "quicksort", "quick-sort"],
            "two_pointers": ["two pointer", "two pointers", "two-pointer", "dual pointer"],
            "sliding_window": ["sliding window", "window", "sliding-window"],
            "hashing": ["hash", "hashing", "hashmap", "hash map", "hash table", "dictionary", "dict"],
            "linked_lists": ["linked list", "linked lists", "linkedlist", "ll"],
            "fast_slow_pointers": ["fast slow", "fast and slow", "tortoise hare", "floyd"],
            "stacks": ["stack", "stacks"],
            "queues": ["queue", "queues"],
            "binary_search": ["binary search", "bsearch", "bs", "binary-search"],
            "recursion": ["recursion", "recursive"],
            "backtracking": ["backtrack", "backtracking", "back tracking"],
            "trees": ["tree", "trees"],
            "binary_trees": ["binary tree", "binary trees", "btree"],
            "bst": ["bst", "binary search tree", "binary-search-tree"],
            "dfs": ["dfs", "depth first", "depth-first", "depth first search"],
            "bfs": ["bfs", "breadth first", "breadth-first", "breadth first search", "level order"],
            "graphs": ["graph", "graphs"],
            "dynamic_programming": ["dp", "dynamic programming", "dynamic-programming", "memoization"],
            "heaps": ["heap", "heaps", "priority queue", "priorityqueue"],
            "tries": ["trie", "tries", "prefix tree"],
            "sorting": ["sort", "sorting", "merge sort", "quick sort"],
            "greedy": ["greedy"],
            "bit_manipulation": ["bit", "bits", "bitwise", "bit manipulation"],
            "string_manipulation": ["string manipulation", "string operations"],
            "string": ["string", "strings"]
        }
        
        # Problem name mappings
        self.problem_keywords = {
            "two_sum": ["two sum", "twosum", "2sum", "2 sum"],
            "three_sum": ["three sum", "threesum", "3sum", "3 sum"],
            "best_time_to_buy_sell_stock": ["best time to buy", "stock", "buy sell stock", "buy and sell"],
            "maximum_subarray": ["maximum subarray", "max subarray", "kadane"],
            "reverse_linked_list": ["reverse linked list", "reverse ll", "reverse list"],
            "linked_list_cycle": ["linked list cycle", "cycle detection", "detect cycle", "ll cycle"],
            "merge_two_sorted_lists": ["merge two sorted", "merge lists", "merge sorted lists"],
            "valid_parentheses": ["valid parentheses", "valid brackets", "balanced parentheses", "matching brackets"],
            "binary_search": ["binary search problem", "search in array"],
            "binary_tree_inorder": ["inorder", "inorder traversal", "in-order"],
            "validate_bst": ["validate bst", "valid bst", "check bst"],
            "lowest_common_ancestor": ["lca", "lowest common ancestor", "common ancestor"],
            "number_of_islands": ["number of islands", "islands", "count islands"],
            "coin_change": ["coin change", "minimum coins"],
            "climbing_stairs": ["climbing stairs", "climb stairs", "stairs"],
            "permutations": ["permutations", "permutation"],
            "subsets": ["subsets", "subset", "powerset"],
            "top_k_frequent": ["top k frequent", "k frequent", "top k"],
        }
        
        # Common phrases to remove (stop words specific to our domain)
        self.stop_phrases = [
            "i learned", "i've learned", "i have learned", "i know", "i understand",
            "i solved", "i've solved", "i have solved", "i completed", "i finished",
            "about", "the", "a", "an", "how to", "what is", "tell me about",
            "can you", "please", "help me with", "explain", "I learned", "I've learned", "I have learned", "I know", "I understand",
            "I solved", "I've solved", "I have solved", "I completed", "I finished",
        ]

    def clean_text(self, text: str) -> str:
        """Basic text cleaning"""
        # Convert to lowercase
        text = text.lower().strip()
        
        # Remove punctuation except hyphens (for multi-word concepts)
        text = re.sub(r'[^\w\s\-]', ' ', text)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        print("\n cleaned data", text)
        return text

    def remove_stop_phrases(self, text: str) -> str:
       # 1. Split the text into a list of words (tokens)
        words = text.split()
        
        # 2. Create a set for faster lookups (O(1) time complexity)
        stop_set = set(self.stop_phrases)
        
        # 3. Keep only words that are NOT in the stop set
        # We check 'word' and 'word.lower()' just to be safe, 
        # though your text is likely already lowercased.
        filtered_words = [w for w in words if w not in stop_set]
        
        # 4. Join them back into a string
        return " ".join(filtered_words)

    # If using rapidfuzz (Alternative method)
    def fuzzy_match(self, text: str, candidates: List[str], threshold: float = 0.75) -> Tuple[str, float]:
        # extractOne finds the best match in a list
        match = process.extractOne(text, candidates, scorer=fuzz.partial_ratio)
        
        if match:
            candidate, score, index = match
            # rapidfuzz returns score out of 100, so divide by 100
            normalized_score = score / 100.0
            
            if normalized_score >= threshold:
                return candidate, normalized_score
                
        return None, 0.0

    def extract_concepts(self, text: str, fuzzy: bool = True) -> List[Dict]:
        """
        Extract DSA concepts from natural language text
        
        Args:
            text: User input text
            fuzzy: Whether to use fuzzy matching
            
        Returns:
            List of dicts with 'concept' and 'confidence' keys
        """
        cleaned = self.clean_text(text)
        cleaned = self.remove_stop_phrases(cleaned)
        
        found_concepts = []
        
        for concept, keywords in self.concept_keywords.items():
            # Direct keyword matching
            for keyword in keywords:
                if keyword in cleaned:
                    found_concepts.append({
                        "concept": concept,
                        "matched_text": keyword,
                        "confidence": 1.0,
                        "method": "exact"
                    })
                    break  # Found this concept, move to next
            
            # Fuzzy matching if enabled and no exact match found
            if fuzzy and not any(c["concept"] == concept for c in found_concepts):
                match, score = self.fuzzy_match(cleaned, keywords, threshold=0.75)
                if match:
                    found_concepts.append({
                        "concept": concept,
                        "matched_text": match,
                        "confidence": score,
                        "method": "fuzzy"
                    })
        
        # Remove duplicates (keep highest confidence)
        unique_concepts = {}
        for item in found_concepts:
            concept = item["concept"]
            if concept not in unique_concepts or item["confidence"] > unique_concepts[concept]["confidence"]:
                unique_concepts[concept] = item
        
        return list(unique_concepts.values())

    def extract_problems(self, text: str, fuzzy: bool = True) -> List[Dict]:
        """
        Extract problem names from natural language text
        
        Args:
            text: User input text
            fuzzy: Whether to use fuzzy matching
            
        Returns:
            List of dicts with 'problem' and 'confidence' keys
        """
        cleaned = self.clean_text(text)
        cleaned = self.remove_stop_phrases(cleaned)
        
        found_problems = []
        
        for problem, keywords in self.problem_keywords.items():
            # Direct keyword matching
            for keyword in keywords:
                if keyword in cleaned:
                    found_problems.append({
                        "problem": problem,
                        "matched_text": keyword,
                        "confidence": 1.0,
                        "method": "exact"
                    })
                    break
            
            # Fuzzy matching
            if fuzzy and not any(p["problem"] == problem for p in found_problems):
                match, score = self.fuzzy_match(cleaned, keywords, threshold=0.75)
                if match:
                    found_problems.append({
                        "problem": problem,
                        "matched_text": match,
                        "confidence": score,
                        "method": "fuzzy"
                    })
        
        # Remove duplicates
        unique_problems = {}
        for item in found_problems:
            problem = item["problem"]
            if problem not in unique_problems or item["confidence"] > unique_problems[problem]["confidence"]:
                unique_problems[problem] = item
        
        return list(unique_problems.values())

    def detect_intent(self, text: str) -> str:
        """
        Detect user intent: 'learned_concept', 'solved_problem', or 'query'
        """
        text_lower = text.lower()
        
        #Goal Pattern indicators
        goal_patterns = [
            r'\b(learn|study|master|get to)\b.*\b(concept|algorithm|topic|dsa|problem)\b',
            r'\b(how do i|what is the path to|path to)\b',
            r'\b(teach me|guide me to)\b'
        ]
        # Learned concept indicators
        learned_patterns = [
            r'\b(learned|learning|studied|know|understand)\b.*\b(about|concept|topic)\b',
            r'\bfinished learning\b',
            r'\bcompleted.*concept\b'
        ]
        
        # Solved problem indicators
        solved_patterns = [
            r'\b(solved|completed|finished|did)\b.*\b(problem|question|challenge)\b',
            r'\b(solved|completed|finished)\b.*\b(leetcode|lc)\b',
            r'\bjust (solved|completed|finished)\b'
        ]
        
        for pattern in learned_patterns:
            if re.search(pattern, text_lower):
                return "learned_concept"
        
        for pattern in solved_patterns:
            if re.search(pattern, text_lower):
                return "solved_problem"
        
        
        
        # If no clear intent, check what we can extract
        concepts = self.extract_concepts(text, fuzzy=False)
        problems = self.extract_problems(text, fuzzy=False)
        
        if problems:
            return "solved_problem"
        elif concepts:
            return "learned_concept"
        
        return "query"

    def process_user_input(self, text: str) -> Dict:
        """
        Complete preprocessing pipeline
        
        Args:
            text: Raw user input
            
        Returns:
            Dict with 'intent', 'concepts', 'problems', and 'original_text'
        """
        intent = self.detect_intent(text)
        concepts = self.extract_concepts(text)
        problems = self.extract_problems(text)
        
        return {
            "intent": intent,
            "concepts": [c["concept"] for c in concepts],
            "concepts_detailed": concepts,
            "problems": [p["problem"] for p in problems],
            "problems_detailed": problems,
            "original_text": text,
            "cleaned_text": self.clean_text(text)
        }


# Example usage and testing
if __name__ == "__main__":
    preprocessor = NLPPreprocessor()
    
    print("=" * 70)
    print("NLP PREPROCESSOR - DEMO")
    print("=" * 70)
    
    # Test cases
    test_inputs = [
        "I learned about arrays and hashing today!",
        "Just solved Two Sum problem on LeetCode",
        "I've been studying binary search and sliding window techniques",
        "Completed the valid parentheses question",
        "I know linked lists and want to learn more",
        "solved twosum and threesum problems",
        "Learning about graphs and dfs/bfs",
        "finished dynamic programming problems",
        "I understand recursion and backtracking now"
    ]
    
    for i, text in enumerate(test_inputs, 1):
        print(f"\n{'─' * 70}")
        print(f"Test {i}: \"{text}\"")
        print('─' * 70)
        
        result = preprocessor.process_user_input(text)
        
        print(f"Intent: {result['intent']}")
        
        if result['concepts']:
            print(f"\nConcepts found:")
            for detail in result['concepts_detailed']:
                print(f"  • {detail['concept']} (confidence: {detail['confidence']:.2f}, method: {detail['method']})")
        
        if result['problems']:
            print(f"\nProblems found:")
            for detail in result['problems_detailed']:
                print(f"  • {detail['problem']} (confidence: {detail['confidence']:.2f}, method: {detail['method']})")
        
        if not result['concepts'] and not result['problems']:
            print("  (No concepts or problems detected)")
    
    print("\n" + "=" * 70)
    
    # Additional tests for fuzzy matching
    print("\n🔍 FUZZY MATCHING DEMO")
    print("=" * 70)
    
    fuzzy_tests = [
        "I learnd aray and hshing",  # Typos
        "solved tu sum problem",      # Typo in Two Sum
        "studying binery serch",      # Typo in Binary Search
    ]
    
    for text in fuzzy_tests:
        print(f"\nInput (with typos): \"{text}\"")
        result = preprocessor.process_user_input(text)
        print(f"Detected concepts: {result['concepts']}")
        print(f"Detected problems: {result['problems']}")
    
    print("\n" + "=" * 70)