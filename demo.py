import sys
import os
from datetime import datetime
import time

# Add the current directory to path to import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from feedback_system import FeedbackGenerator, StudentResponse

def print_header(title):
    """Print a formatted header"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def print_section(title):
    """Print a formatted section header"""
    print(f"\n--- {title} ---")

def demo_feedback_generation():
    """Demonstrate the feedback generation capabilities"""
    print_header("STUDENT FEEDBACK GENERATION SYSTEM DEMO")
    
    # Initialize the system
    print("🔧 Initializing AI-powered feedback system...")
    feedback_gen = FeedbackGenerator()
    print("✅ System initialized with sentence-transformers model")
    
    # Sample student responses covering different performance levels
    sample_responses = [
        {
            "student": "Alice Johnson",
            "response": StudentResponse(
                student_id="alice_001",
                question_id="math_algebra_01",
                response_text="To solve the equation 2x + 6 = 14, I need to isolate x. First, I subtract 6 from both sides to get 2x = 8. Then I divide both sides by 2 to get x = 4. This works because I'm using inverse operations to undo what was done to x.",
                subject="mathematics",
                timestamp=datetime.now(),
                expected_keywords=["inverse operations", "isolate", "subtract", "divide"]
            ),
            "level": "High Performance"
        },
        {
            "student": "Bob Smith",
            "response": StudentResponse(
                student_id="bob_002",
                question_id="science_physics_01",
                response_text="Newton's first law says objects at rest stay at rest and objects in motion stay in motion unless a force acts on them.",
                subject="science",
                timestamp=datetime.now(),
                expected_keywords=["force", "motion", "rest", "inertia"]
            ),
            "level": "Good Performance"
        },
        {
            "student": "Carol Davis",
            "response": StudentResponse(
                student_id="carol_003",
                question_id="english_theme_01",
                response_text="The story is about friendship and the main character learns something.",
                subject="english",
                timestamp=datetime.now(),
                expected_keywords=["theme", "character development", "literary analysis"]
            ),
            "level": "Needs Improvement"
        },
        {
            "student": "David Wilson",
            "response": StudentResponse(
                student_id="david_004",
                question_id="math_geometry_01",
                response_text="The Pythagorean theorem is a fundamental principle in geometry that states that in a right triangle, the square of the length of the hypotenuse (the side opposite the right angle) is equal to the sum of squares of the lengths of the other two sides. This can be written as a² + b² = c², where c represents the hypotenuse and a and b represent the other two sides.",
                subject="mathematics",
                timestamp=datetime.now(),
                expected_keywords=["Pythagorean theorem", "right triangle", "hypotenuse", "squares"]
            ),
            "level": "Excellent Performance"
        }
    ]
    
    print_section("PROCESSING STUDENT RESPONSES")
    
    all_feedback = []
    for i, sample in enumerate(sample_responses, 1):
        print(f"\n📝 Processing Response {i}/4 - {sample['student']} ({sample['level']})")
        print(f"Subject: {sample['response'].subject.title()}")
        print(f"Response: {sample['response'].response_text[:100]}...")
        
        # Generate feedback
        start_time = time.time()
        feedback = feedback_gen.generate_feedback(sample['response'])
        processing_time = time.time() - start_time
        
        all_feedback.append(feedback)
        
        # Display results
        print(f"⚡ Processing time: {processing_time:.2f} seconds")
        print(f"🎯 Similarity Score: {feedback.similarity_score:.3f} ({feedback.similarity_score*100:.1f}%)")
        print(f"🏆 Reward: {feedback.reward_type.value.upper()}")
        print(f"⭐ Points Earned: {feedback.points_earned}")
        print(f"💬 Feedback: {feedback.feedback_text}")
        
        if feedback.strengths:
            print(f"✅ Strengths: {', '.join(feedback.strengths[:2])}...")
        
        if feedback.improvement_areas:
            print(f"📈 Improvements: {', '.join(feedback.improvement_areas[:2])}...")
        
        print(f"💡 Tips: {feedback.personalized_tips[0] if feedback.personalized_tips else 'Keep up the good work!'}")
    
    return feedback_gen, all_feedback

def demo_student_progress(feedback_gen):
    """Demonstrate student progress tracking"""
    print_section("STUDENT PROGRESS TRACKING")
    
    # Get progress for different students
    students = ["alice_001", "bob_002", "carol_003", "david_004"]
    
    for student_id in students:
        progress = feedback_gen.get_student_progress(student_id)
        
        if "error" not in progress:
            print(f"\n📊 Progress Report for {student_id}:")
            print(f"   📝 Total Responses: {progress['total_responses']}")
            print(f"   📈 Average Score: {progress['average_score']*100:.1f}%")
            print(f"   🎯 Latest Score: {progress['latest_score']*100:.1f}%")
            print(f"   ⭐ Total Points: {progress['total_points']}")
            
            # Show reward distribution
            rewards = progress['reward_distribution']
            reward_summary = []
            if rewards['platinum'] > 0: reward_summary.append(f"💎{rewards['platinum']}")
            if rewards['gold'] > 0: reward_summary.append(f"🥇{rewards['gold']}")
            if rewards['silver'] > 0: reward_summary.append(f"🥈{rewards['silver']}")
            if rewards['bronze'] > 0: reward_summary.append(f"🥉{rewards['bronze']}")
            
            print(f"   🏆 Rewards: {' | '.join(reward_summary) if reward_summary else 'None yet'}")

def demo_educator_dashboard(feedback_gen):
    """Demonstrate educator dashboard functionality"""
    print_section("EDUCATOR DASHBOARD")
    
    dashboard = feedback_gen.get_educator_dashboard()
    
    print("🎓 Class Overview:")
    overview = dashboard['class_overview']
    print(f"   👥 Total Students: {overview['total_students']}")
    print(f"   📝 Total Responses: {overview['total_responses']}")
    print(f"   📊 Class Average: {overview['class_average_score']*100:.1f}%")
    print(f"   ⚠️  Students Needing Attention: {overview['students_needing_attention']}")
    
    if dashboard['recent_alerts']:
        print("\n🚨 Recent Alerts:")
        for alert in dashboard['recent_alerts']:
            severity_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}
            print(f"   {severity_emoji.get(alert['severity'], '⚪')} {alert['alert_type'].replace('_', ' ').title()}")
            print(f"      Student: {alert['student_id']}")
            print(f"      Description: {alert['description']}")
    else:
        print("\n✅ No recent alerts - all students performing well!")
    
    if dashboard['struggling_students']:
        print(f"\n📉 Students needing support: {', '.join(dashboard['struggling_students'])}")

def demo_api_features(feedback_gen):
    """Demonstrate additional API features"""
    print_section("ADDITIONAL FEATURES")
    
    print("💾 Data Export:")
    try:
        export_file = feedback_gen.export_data("demo_export.json")
        print(f"   ✅ Data exported to: {export_file}")
        
        # Check file size
        file_size = os.path.getsize(export_file) if os.path.exists(export_file) else 0
        print(f"   📦 File size: {file_size} bytes")
        
    except Exception as e:
        print(f"   ❌ Export failed: {str(e)}")
    
    print("\n🔧 System Capabilities:")
    print("   ✅ Real-time feedback generation")
    print("   ✅ Multi-subject support (Math, Science, English)")
    print("   ✅ Personalized learning tips")
    print("   ✅ Automated reward system")
    print("   ✅ Progress tracking and analytics")
    print("   ✅ Educator alerts and notifications")
    print("   ✅ Data export and reporting")
    print("   ✅ Web interface and REST API")

def performance_benchmark(feedback_gen):
    """Benchmark system performance"""
    print_section("PERFORMANCE BENCHMARK")
    
    # Test response for benchmarking
    test_response = StudentResponse(
        student_id="benchmark_test",
        question_id="perf_test_01",
        response_text="This is a sample response for performance testing of the feedback generation system.",
        subject="mathematics",
        timestamp=datetime.now(),
        expected_keywords=["test", "performance", "benchmark"]
    )
    
    # Run multiple iterations
    iterations = 5
    total_time = 0
    
    print(f"🚀 Running {iterations} feedback generations...")
    
    for i in range(iterations):
        start_time = time.time()
        feedback = feedback_gen.generate_feedback(test_response)
        end_time = time.time()
        
        iteration_time = end_time - start_time
        total_time += iteration_time
        print(f"   Iteration {i+1}: {iteration_time:.3f}s")
    
    avg_time = total_time / iterations
    print(f"\n📊 Performance Results:")
    print(f"   ⚡ Average processing time: {avg_time:.3f} seconds")
    print(f"   🔥 Throughput: ~{60/avg_time:.1f} responses per minute")
    print(f"   💪 Total time for {iterations} iterations: {total_time:.3f}s")

def main():
    """Main demo function"""
    try:
        print("🎓 Welcome to the Student Feedback Generation System Demo!")
        print("This demo will showcase all the system capabilities.")
        
        # Run the main demo
        feedback_gen, all_feedback = demo_feedback_generation()
        
        # Show additional features
        demo_student_progress(feedback_gen)
        demo_educator_dashboard(feedback_gen)
        demo_api_features(feedback_gen)
        performance_benchmark(feedback_gen)
        
        print_header("DEMO COMPLETED SUCCESSFULLY!")
        print("🎉 The Student Feedback Generation System is ready for use!")
        print("\n🚀 Next Steps:")
        print("1. Run 'python app.py' to start the web interface")
        print("2. Open http://localhost:5000 in your browser")
        print("3. Try submitting student responses through the web interface")
        print("4. Explore the educator dashboard and progress reports")
        print("\n📖 Integration ready for:")
        print("• Behavior detection system (Florence2 model)")
        print("• Teacher feedback system (PEGASUS model)")
        print("• Learning Management Systems (LMS)")
        print("• Mobile applications")
        
    except Exception as e:
        print(f"\n❌ Demo failed with error: {str(e)}")
        print("Please check your installation and try again.")
        print("Make sure all required packages are installed:")
        print("pip install -r requirements.txt")

if __name__ == "__main__":
    main()