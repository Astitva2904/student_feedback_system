import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import json
import datetime
from typing import Dict, List, Tuple, Optional
import logging
from dataclasses import dataclass, asdict
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RewardType(Enum):
    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"
    PLATINUM = "platinum"

@dataclass
class StudentResponse:
    student_id: str
    question_id: str
    response_text: str
    subject: str
    timestamp: datetime.datetime
    expected_keywords: List[str] = None

@dataclass
class Feedback:
    response_id: str
    student_id: str
    similarity_score: float
    reward_type: RewardType
    feedback_text: str
    strengths: List[str]
    improvement_areas: List[str]
    personalized_tips: List[str]
    points_earned: int
    timestamp: datetime.datetime

@dataclass
class EducatorAlert:
    alert_id: str
    student_id: str
    alert_type: str
    severity: str
    description: str
    timestamp: datetime.datetime
    action_required: bool

class FeedbackGenerator:
    def __init__(self, model_name: str = 'sentence-transformers/all-MiniLM-L6-v2'):
        """Initialize the feedback generation system"""
        logger.info(f"Loading model: {model_name}")
        self.model = SentenceTransformer(model_name)
        self.feedback_history = []
        self.educator_alerts = []
        
        # Load reference answers and reward criteria
        self.reference_answers = self._load_reference_answers()
        self.reward_criteria = self._setup_reward_criteria()
        
    def _load_reference_answers(self) -> Dict:
        """Load reference answers for different subjects"""
        return {
            "mathematics": {
                "algebra": [
                    "To solve linear equations, isolate the variable by performing inverse operations on both sides",
                    "The quadratic formula is x = (-b ± √(b²-4ac)) / 2a for equations ax² + bx + c = 0",
                    "Functions represent relationships between input and output values"
                ],
                "geometry": [
                    "The Pythagorean theorem states that a² + b² = c² for right triangles",
                    "Area of a circle is π × radius squared",
                    "Parallel lines never intersect and have the same slope"
                ]
            },
            "science": {
                "physics": [
                    "Newton's first law states that objects in motion stay in motion unless acted upon by force",
                    "Energy cannot be created or destroyed, only transformed from one form to another",
                    "Force equals mass times acceleration (F = ma)"
                ],
                "chemistry": [
                    "Atoms consist of protons, neutrons, and electrons",
                    "Chemical reactions involve breaking and forming bonds between atoms",
                    "The periodic table organizes elements by atomic number"
                ]
            },
            "english": {
                "literature": [
                    "Theme is the central message or meaning of a literary work",
                    "Character development shows how characters change throughout a story",
                    "Symbolism uses objects or actions to represent deeper meanings"
                ],
                "grammar": [
                    "Subjects perform the action in a sentence while objects receive it",
                    "Proper punctuation helps clarify meaning and structure",
                    "Active voice makes writing more direct and engaging"
                ]
            }
        }
    
    def _setup_reward_criteria(self) -> Dict:
        """Setup criteria for different reward types"""
        return {
            RewardType.PLATINUM: {"min_score": 0.9, "points": 100, "description": "Exceptional understanding!"},
            RewardType.GOLD: {"min_score": 0.8, "points": 75, "description": "Excellent work!"},
            RewardType.SILVER: {"min_score": 0.65, "points": 50, "description": "Good effort!"},
            RewardType.BRONZE: {"min_score": 0.4, "points": 25, "description": "Keep trying!"}
        }
    
    def analyze_response(self, student_response: StudentResponse) -> Tuple[float, List[str]]:
        """Analyze student response against reference answers"""
        try:
            # Get relevant reference answers
            subject_refs = self.reference_answers.get(student_response.subject.lower(), {})
            if not subject_refs:
                logger.warning(f"No reference answers found for subject: {student_response.subject}")
                return 0.5, []
            
            # Flatten all reference answers for the subject
            all_refs = []
            for topic_refs in subject_refs.values():
                all_refs.extend(topic_refs)
            
            # Add expected keywords if provided
            if student_response.expected_keywords:
                keyword_text = " ".join(student_response.expected_keywords)
                all_refs.append(keyword_text)
            
            # Encode student response and reference answers
            student_embedding = self.model.encode([student_response.response_text])
            reference_embeddings = self.model.encode(all_refs)
            
            # Calculate similarities
            similarities = cosine_similarity(student_embedding, reference_embeddings)[0]
            max_similarity = np.max(similarities)
            
            # Find best matching references
            top_indices = np.argsort(similarities)[-3:][::-1]  # Top 3 matches
            best_matches = [all_refs[i] for i in top_indices if similarities[i] > 0.3]
            
            return float(max_similarity), best_matches
            
        except Exception as e:
            logger.error(f"Error analyzing response: {str(e)}")
            return 0.0, []
    
    def determine_reward(self, similarity_score: float) -> Tuple[RewardType, int]:
        """Determine reward type and points based on similarity score"""
        for reward_type, criteria in self.reward_criteria.items():
            if similarity_score >= criteria["min_score"]:
                return reward_type, criteria["points"]
        
        # Default to bronze if below all thresholds
        return RewardType.BRONZE, 10
    
    def generate_personalized_feedback(self, student_response: StudentResponse, 
                                     similarity_score: float, 
                                     best_matches: List[str]) -> Dict:
        """Generate personalized feedback based on analysis"""
        
        # Determine strengths and areas for improvement
        strengths = []
        improvement_areas = []
        tips = []
        
        if similarity_score >= 0.8:
            strengths.extend([
                "Demonstrates strong understanding of key concepts",
                "Uses appropriate terminology",
                "Provides clear explanations"
            ])
            tips.extend([
                "Try to add more examples to strengthen your explanations",
                "Consider exploring advanced applications of these concepts"
            ])
        elif similarity_score >= 0.6:
            strengths.extend([
                "Shows good grasp of basic concepts",
                "Attempts to explain reasoning"
            ])
            improvement_areas.extend([
                "Could use more specific terminology",
                "Explanations could be more detailed"
            ])
            tips.extend([
                "Review key vocabulary for this topic",
                "Practice explaining concepts in your own words",
                "Try to include specific examples"
            ])
        else:
            strengths.append("Shows effort in attempting the question")
            improvement_areas.extend([
                "Needs to review fundamental concepts",
                "Requires more specific and detailed responses"
            ])
            tips.extend([
                "Review the lesson materials again",
                "Ask your teacher for clarification on confusing topics",
                "Practice with similar problems",
                "Try to break down complex problems into smaller steps"
            ])
        
        # Generate main feedback text
        reward_type, points = self.determine_reward(similarity_score)
        reward_desc = self.reward_criteria[reward_type]["description"]
        
        feedback_text = f"{reward_desc} "
        
        if similarity_score >= 0.8:
            feedback_text += "You've shown excellent understanding of this topic. Your response demonstrates clear thinking and good use of relevant concepts."
        elif similarity_score >= 0.6:
            feedback_text += "You're on the right track! Your response shows good understanding, with room for more detail and precision."
        else:
            feedback_text += "Keep working on this topic. Review the key concepts and try to be more specific in your explanations."
        
        return {
            "feedback_text": feedback_text,
            "strengths": strengths,
            "improvement_areas": improvement_areas,
            "tips": tips,
            "reward_type": reward_type,
            "points": points
        }
    
    def generate_feedback(self, student_response: StudentResponse) -> Feedback:
        """Main method to generate comprehensive feedback"""
        try:
            # Analyze the response
            similarity_score, best_matches = self.analyze_response(student_response)
            
            # Generate personalized feedback
            feedback_data = self.generate_personalized_feedback(
                student_response, similarity_score, best_matches
            )
            
            # Create feedback object
            feedback = Feedback(
                response_id=f"resp_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}",
                student_id=student_response.student_id,
                similarity_score=similarity_score,
                reward_type=feedback_data["reward_type"],
                feedback_text=feedback_data["feedback_text"],
                strengths=feedback_data["strengths"],
                improvement_areas=feedback_data["improvement_areas"],
                personalized_tips=feedback_data["tips"],
                points_earned=feedback_data["points"],
                timestamp=datetime.datetime.now()
            )
            
            # Store feedback
            self.feedback_history.append(feedback)
            
            # Generate educator alerts if needed
            self._check_for_educator_alerts(student_response, similarity_score)
            
            logger.info(f"Generated feedback for student {student_response.student_id}")
            return feedback
            
        except Exception as e:
            logger.error(f"Error generating feedback: {str(e)}")
            raise
    
    def _check_for_educator_alerts(self, student_response: StudentResponse, similarity_score: float):
        """Check if educator alerts should be generated"""
        alerts = []
        
        # Low performance alert
        if similarity_score < 0.3:
            alert = EducatorAlert(
                alert_id=f"alert_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}",
                student_id=student_response.student_id,
                alert_type="low_performance",
                severity="high",
                description=f"Student showing very low understanding in {student_response.subject}",
                timestamp=datetime.datetime.now(),
                action_required=True
            )
            alerts.append(alert)
        
        # Consistent struggle alert (check recent history)
        recent_scores = [f.similarity_score for f in self.feedback_history[-5:] 
                        if f.student_id == student_response.student_id]
        
        if len(recent_scores) >= 3 and all(score < 0.5 for score in recent_scores):
            alert = EducatorAlert(
                alert_id=f"alert_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}_pattern",
                student_id=student_response.student_id,
                alert_type="consistent_struggle",
                severity="medium",
                description=f"Student showing consistent difficulties across multiple responses",
                timestamp=datetime.datetime.now(),
                action_required=True
            )
            alerts.append(alert)
        
        self.educator_alerts.extend(alerts)
    
    def get_student_progress(self, student_id: str) -> Dict:
        """Get comprehensive progress report for a student"""
        student_feedback = [f for f in self.feedback_history if f.student_id == student_id]
        
        if not student_feedback:
            return {"error": "No feedback found for this student"}
        
        # Calculate statistics
        scores = [f.similarity_score for f in student_feedback]
        total_points = sum(f.points_earned for f in student_feedback)
        
        reward_counts = {}
        for reward_type in RewardType:
            reward_counts[reward_type.value] = len([f for f in student_feedback 
                                                  if f.reward_type == reward_type])
        
        progress_report = {
            "student_id": student_id,
            "total_responses": len(student_feedback),
            "average_score": np.mean(scores),
            "latest_score": scores[-1],
            "total_points": total_points,
            "reward_distribution": reward_counts,
            "recent_improvement": scores[-1] - scores[0] if len(scores) > 1 else 0,
            "last_updated": student_feedback[-1].timestamp.isoformat()
        }
        
        return progress_report
    
    def get_educator_dashboard(self) -> Dict:
        """Generate educator dashboard with alerts and class overview"""
        # Get all unique students
        all_students = list(set(f.student_id for f in self.feedback_history))
        
        # Calculate class statistics
        all_scores = [f.similarity_score for f in self.feedback_history]
        class_average = np.mean(all_scores) if all_scores else 0
        
        # Get students needing attention
        struggling_students = []
        for student_id in all_students:
            recent_scores = [f.similarity_score for f in self.feedback_history[-3:] 
                           if f.student_id == student_id]
            if recent_scores and np.mean(recent_scores) < 0.4:
                struggling_students.append(student_id)
        
        # Get recent alerts
        recent_alerts = [alert for alert in self.educator_alerts 
                        if alert.timestamp > datetime.datetime.now() - datetime.timedelta(days=7)]
        
        dashboard = {
            "class_overview": {
                "total_students": len(all_students),
                "total_responses": len(self.feedback_history),
                "class_average_score": class_average,
                "students_needing_attention": len(struggling_students)
            },
            "recent_alerts": [asdict(alert) for alert in recent_alerts],
            "struggling_students": struggling_students,
            "last_updated": datetime.datetime.now().isoformat()
        }
        
        return dashboard
    
    def export_data(self, filename: str = None) -> str:
        """Export all feedback data to JSON file"""
        if not filename:
            filename = f"feedback_data_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        export_data = {
            "feedback_history": [asdict(f) for f in self.feedback_history],
            "educator_alerts": [asdict(a) for a in self.educator_alerts],
            "export_timestamp": datetime.datetime.now().isoformat()
        }
        
        # Convert datetime objects to strings for JSON serialization
        def convert_datetime(obj):
            if isinstance(obj, datetime.datetime):
                return obj.isoformat()
            return obj
        
        with open(filename, 'w') as f:
            json.dump(export_data, f, default=convert_datetime, indent=2)
        
        logger.info(f"Data exported to {filename}")
        return filename

# Example usage and testing
def main():
    """Example usage of the feedback generation system"""
    
    # Initialize the system
    feedback_gen = FeedbackGenerator()
    
    # Example student responses
    example_responses = [
        StudentResponse(
            student_id="student_001",
            question_id="math_001",
            response_text="To solve x + 5 = 10, I subtract 5 from both sides to get x = 5. This works because of inverse operations.",
            subject="mathematics",
            timestamp=datetime.datetime.now(),
            expected_keywords=["inverse operations", "subtract", "both sides"]
        ),
        StudentResponse(
            student_id="student_002",
            question_id="science_001",
            response_text="Gravity pulls things down",
            subject="science",
            timestamp=datetime.datetime.now(),
            expected_keywords=["force", "acceleration", "mass"]
        ),
        StudentResponse(
            student_id="student_001",
            question_id="english_001",
            response_text="The theme of the story is about friendship and how people help each other in difficult times. The author shows this through the main character's actions.",
            subject="english",
            timestamp=datetime.datetime.now(),
            expected_keywords=["theme", "character development", "literary analysis"]
        )
    ]
    
    # Generate feedback for each response
    print("=== STUDENT FEEDBACK GENERATION SYSTEM ===\n")
    
    for response in example_responses:
        print(f"Processing response from {response.student_id}...")
        feedback = feedback_gen.generate_feedback(response)
        
        print(f"\n--- Feedback for {response.student_id} ---")
        print(f"Subject: {response.subject}")
        print(f"Similarity Score: {feedback.similarity_score:.2f}")
        print(f"Reward: {feedback.reward_type.value.upper()} ({feedback.points_earned} points)")
        print(f"Feedback: {feedback.feedback_text}")
        print(f"Strengths: {', '.join(feedback.strengths)}")
        if feedback.improvement_areas:
            print(f"Areas for Improvement: {', '.join(feedback.improvement_areas)}")
        print(f"Tips: {', '.join(feedback.personalized_tips)}")
        print("-" * 50)
    
    # Show student progress
    print("\n=== STUDENT PROGRESS REPORT ===")
    progress = feedback_gen.get_student_progress("student_001")
    for key, value in progress.items():
        print(f"{key}: {value}")
    
    # Show educator dashboard
    print("\n=== EDUCATOR DASHBOARD ===")
    dashboard = feedback_gen.get_educator_dashboard()
    for key, value in dashboard.items():
        print(f"{key}: {value}")
    
    # Export data
    export_file = feedback_gen.export_data()
    print(f"\nData exported to: {export_file}")

if __name__ == "__main__":
    main()