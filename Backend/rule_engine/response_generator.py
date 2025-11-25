"""
Natural Response Generator - Makes recommendations feel encouraging and human
"""

import random
from typing import Dict, List

print("hello from response generator")
class ResponseGenerator:
    def __init__(self):
        # Encouraging intros for concept learning
        self.concept_intros = [
            "Great progress! 🎉",
            "Nice work! 💪",
            "Awesome! 🚀",
            "You're doing great! ⭐",
            "Fantastic! 🎯",
            "Keep it up! 🔥",
            "Excellent! 👏",
            "Love to see it! ✨"
        ]
        
        # Transitions to next concepts
        self.next_concept_phrases = [
            "You're ready to tackle",
            "Time to level up with",
            "Next up, you should explore",
            "You're well-prepared for",
            "Consider diving into",
            "You'd do well with",
            "A natural next step would be"
        ]
        
        # Problem recommendation phrases
        self.problem_phrases = [
            "Here are some problems you can crush now:",
            "You're ready for these challenges:",
            "Try your hand at these:",
            "These problems are perfect for your level:",
            "Give these a shot:",
            "You should be able to solve:",
            "Test your skills with:"
        ]
        
        # After solving a problem
        self.problem_solved_intros = [
            "Nicely done! 🎉",
            "Great job solving that! 💯",
            "You crushed it! 🔥",
            "Well done! ⭐",
            "Awesome solve! 🚀",
            "That's a solid win! 💪",
            "Nice! 👏"
        ]
        
        # Similar problems phrases
        self.similar_problem_phrases = [
            "Since you solved that, try these similar ones:",
            "You're on a roll! Keep the momentum with:",
            "Build on that success with:",
            "Similar problems to practice:",
            "Keep the pattern going with:"
        ]
        
        # Difficulty encouragement
        self.difficulty_encouragement = {
            "easy": "a great foundation",
            "medium": "a solid challenge",
            "hard": "a tough but rewarding problem"
        }
        
        # Empty state messages
        self.no_recommendations = [
            "Hmm, I don't have specific recommendations yet. Keep learning and come back!",
            "You're either way ahead or just starting out! Keep going! 💪",
            "I need a bit more context. Tell me what you've learned so far!"
        ]

    def format_concept_list(self, concepts: List[str]) -> str:
        """Format a list of concepts in a natural way"""
        if not concepts:
            return ""
        
        if len(concepts) == 1:
            return concepts[0].replace("_", " ").title()
        
        formatted = [c.replace("_", " ").title() for c in concepts]
        
        if len(formatted) == 2:
            return f"{formatted[0]} and {formatted[1]}"
        
        return ", ".join(formatted[:-1]) + f", and {formatted[-1]}"

    def format_problem_name(self, problem: str) -> str:
        """Format problem name to be readable"""
        return problem.replace("_", " ").title()

    def generate_concept_learned_response(self, recommendation_data: Dict) -> str:
        """
        Generate natural response for when user learns concepts
        
        Args:
            recommendation_data: Output from DSARecommender.recommend_from_concepts()
        """
        learned = recommendation_data.get("learned_concepts", [])
        next_concepts = recommendation_data.get("next_concepts", [])
        problems = recommendation_data.get("problems_to_solve", [])
        difficulty= recommendation_data.get("recommended_difficulty")
        response_parts = []
        
        # Encouraging intro
        intro = random.choice(self.concept_intros)
        learned_text = self.format_concept_list(learned)
        response_parts.append(f"{intro} You've got {learned_text} down!")
        
        # Next concepts
        if next_concepts:
            transition = random.choice(self.next_concept_phrases)
            concepts_text = self.format_concept_list(next_concepts[:3])  # Limit to 3
            response_parts.append(f"\n\n{transition} {concepts_text}.")
            
            if len(next_concepts) > 3:
                response_parts.append(f" (Plus {len(next_concepts) - 3} more topics when you're ready!)")
        
        # Problems to solve
        if problems:
            problem_intro = random.choice(self.problem_phrases)
            response_parts.append(f"\n\n{problem_intro}")
            
            # Group by difficulty
            easy = [p for p in problems if p["difficulty"] == "easy"]
            medium = [p for p in problems if p["difficulty"] == "medium"]
            hard = [p for p in problems if p["difficulty"] == "hard"]
            
            for difficulty, problem_list in [("Easy", easy), ("Medium", medium), ("Hard", hard)]:
                if problem_list:
                    response_parts.append(f"\n\n**{difficulty}:**")
                    for i, prob in enumerate(problem_list[:5], 1):  # Limit to 5 per difficulty
                        name = self.format_problem_name(prob["name"])
                        pattern = prob.get("pattern", "").replace("_", " ").title()
                        response_parts.append(f"\n{i}. {name} (Pattern: {pattern})")
        else:
            response_parts.append(f"\n\nKeep learning! Once you pick up a few more concepts, I'll have some problems for you to try.")
        
        return "".join(response_parts)

    def generate_problem_solved_response(self, recommendation_data: Dict, problem_name: str) -> str:
        """
        Generate natural response for when user solves a problem
        
        Args:
            recommendation_data: Output from DSARecommender.recommend_from_problem()
            problem_name: Name of the solved problem
        """
        if "error" in recommendation_data:
            return f"Hmm, I couldn't find that problem. {recommendation_data.get('suggestion', '')}"
        
        concepts = recommendation_data.get("concepts_learned", [])
        similar = recommendation_data.get("similar_problems", [])
        pattern_based = recommendation_data.get("pattern_based_problems", [])
        next_concepts = recommendation_data.get("next_concepts", [])
        pattern = recommendation_data.get("pattern", "")
        
        response_parts = []
        
        # Encouraging intro
        intro = random.choice(self.problem_solved_intros)
        formatted_name = self.format_problem_name(problem_name)
        response_parts.append(f"{intro} You just solved **{formatted_name}**!")
        
        # Mention concepts
        if concepts:
            concepts_text = self.format_concept_list(concepts)
            response_parts.append(f" You practiced {concepts_text}.")
        
        # Pattern mention
        if pattern:
            pattern_text = pattern.replace("_", " ").title()
            response_parts.append(f" This is a classic **{pattern_text}** problem.")
        
        # Similar problems
        all_similar = similar + pattern_based
        if all_similar:
            similar_intro = random.choice(self.similar_problem_phrases)
            response_parts.append(f"\n\n{similar_intro}")
            
            for i, prob in enumerate(all_similar[:6], 1):  # Limit to 6
                name = self.format_problem_name(prob["name"])
                difficulty = prob["difficulty"].capitalize()
                emoji = "🟢" if difficulty == "Easy" else "🟡" if difficulty == "Medium" else "🔴"
                response_parts.append(f"\n{i}. {emoji} {name} ({difficulty})")
        
        # Next concepts
        if next_concepts:
            concepts_text = self.format_concept_list(next_concepts[:3])
            response_parts.append(f"\n\n💡 Ready to learn something new? Check out {concepts_text}!")
        
        return "".join(response_parts)

    def generate_learning_path_response(self, path_data: Dict) -> str:
        """
        Generate natural response for learning path
        
        Args:
            path_data: Output from DSARecommender.get_learning_path()
        """
        if "error" in path_data:
            return f"Oops! {path_data['error']}"
        
        path = path_data.get("learning_path", [])
        current = path_data.get("current_level", [])
        goal = path_data.get("goal", "")
        
        response_parts = []
        
        response_parts.append("🗺️ **Your Learning Path:**\n\n")
        
        if current:
            current_text = self.format_concept_list(current)
            response_parts.append(f"You already know: {current_text}\n\n")
        
        if path:
            goal_text = goal.replace("_", " ").title()
            response_parts.append(f"To master **{goal_text}**, follow this path:\n\n")
            
            for i, concept in enumerate(path, 1):
                concept_text = concept.replace("_", " ").title()
                emoji = "✅" if i == 1 else "📍"
                response_parts.append(f"{emoji} {i}. {concept_text}\n")
            
            response_parts.append(f"\nTake it one step at a time, and you'll get there! 💪")
        
        if "note" in path_data:
            response_parts.append(f"\n\n💡 {path_data['note']}")
        
        return "".join(response_parts)

    def generate_general_encouragement(self) -> str:
        """Generate a general encouraging message"""
        messages = [
            "You're making great progress! Keep at it! 🚀",
            "Every problem solved is a step forward! 💪",
            "Consistency is key - you're doing awesome! ⭐",
            "Keep building that problem-solving muscle! 🔥",
            "You've got this! One concept at a time! ✨"
        ]
        return random.choice(messages)

    def add_motivational_footer(self, response: str, include_tip: bool = True) -> str:
        """Add a motivational footer to any response"""
        tips = [
            "\n\n💡 **Tip:** Practice makes perfect - consistency beats intensity!",
            "\n\n💡 **Tip:** Don't rush - understanding beats memorization!",
            "\n\n💡 **Tip:** Stuck? Try explaining the problem out loud!",
            "\n\n💡 **Tip:** Review problems you've solved - repetition builds mastery!",
            "\n\n💡 **Tip:** Focus on patterns, not just individual problems!"
        ]
        
        if include_tip and random.random() > 0.5:  # 50% chance of adding a tip
            response += random.choice(tips)
        
        return response


# Demo / Testing
if __name__ == "__main__":
    generator = ResponseGenerator()
    print("heelloo from response generator demo")
    print("=" * 70)
    print("NATURAL RESPONSE GENERATOR - DEMO")
    print("=" * 70)
    
    # Test 1: Concept learned
    print("\n" + "─" * 70)
    print("Test 1: I learned Arrays and Hashing")
    print("─" * 70)
    
    mock_concept_data = {
        "learned_concepts": ["arrays", "hashing"],
        "next_concepts": ["two_pointers", "sliding_window", "binary_search"],
        "problems_to_solve": [
            {"name": "two_sum", "difficulty": "easy", "pattern": "two_sum_pattern"},
            {"name": "valid_anagram", "difficulty": "easy", "pattern": "hashing"},
            {"name": "three_sum", "difficulty": "medium", "pattern": "two_pointers"},
        ]
    }
    
    response = generator.generate_concept_learned_response(mock_concept_data)
    response = generator.add_motivational_footer(response)
    print(response)
    
    # Test 2: Problem solved
    print("\n\n" + "─" * 70)
    print("Test 2: User solved Two Sum")
    print("─" * 70)
    
    mock_problem_data = {
        "concepts_learned": ["arrays", "hashing"],
        "similar_problems": [
            {"name": "three_sum", "difficulty": "medium"},
            {"name": "four_sum", "difficulty": "medium"},
        ],
        "pattern_based_problems": [
            {"name": "two_sum_ii", "difficulty": "easy"},
        ],
        "next_concepts": ["two_pointers", "sliding_window"],
        "pattern": "two_sum_pattern"
    }
    
    response = generator.generate_problem_solved_response(mock_problem_data, "two_sum")
    response = generator.add_motivational_footer(response)
    print(response)
    
    # Test 3: Learning path
    print("\n\n" + "─" * 70)
    print("Test 3: Learning path to Dynamic Programming")
    print("─" * 70)
    
    mock_path_data = {
        "learning_path": ["recursion", "dynamic_programming"],
        "current_level": ["arrays", "hashing"],
        "goal": "dynamic_programming"
    }
    
    response = generator.generate_learning_path_response(mock_path_data)
    print(response)
    
    # Test 4: Multiple generations to show randomness
    print("\n\n" + "─" * 70)
    print("Test 4: Same input, different outputs (randomization)")
    print("─" * 70)
    
    for i in range(3):
        print(f"\nVariation {i+1}:")
        print(generator.generate_concept_learned_response(mock_concept_data).split('\n')[0])
    
    print("\n" + "=" * 70)