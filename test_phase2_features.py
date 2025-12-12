"""
Comprehensive tests for Phase 2 features
Tests all new functionality including insights, learning, automation, and more
"""
import unittest
import jdatetime
from pathlib import Path
import os
import tempfile
import shutil

# Import Phase 2 modules
from intelligence.productivity_analyzer import ProductivityAnalyzer
from intelligence.learning_engine import LearningEngine
from intelligence.pattern_detector import PatternDetector
from intelligence.automation_engine import AutomationEngine
from intelligence.rag_enhancements.multi_document_synthesizer import MultiDocumentSynthesizer
from intelligence.rag_enhancements.contradiction_detector import ContradictionDetector
from intelligence.rag_enhancements.role_based_summarizer import RoleBasedSummarizer
from intelligence.rag_enhancements.action_extractor import ActionExtractor
from intelligence.meeting_prep.agenda_analyzer import AgendaAnalyzer
from intelligence.meeting_prep.briefing_generator import BriefingGenerator
from intelligence.meeting_prep.talking_point_suggester import TalkingPointSuggester
from intelligence.meeting_prep.question_predictor import QuestionPredictor
from intelligence.document_generator import DocumentGenerator
from database import DatabaseManager


class TestPhase2Features(unittest.TestCase):
    """Test suite for Phase 2 features"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Create temporary database
        self.test_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.test_db_path = self.test_db.name
        self.test_db.close()
        
        # Initialize components
        self.db = DatabaseManager(self.test_db_path)
        self.productivity_analyzer = ProductivityAnalyzer(self.test_db_path)
        self.learning_engine = LearningEngine(self.test_db_path)
        self.pattern_detector = PatternDetector(self.test_db_path)
        self.automation_engine = AutomationEngine(self.test_db_path)
        
        # Create test data
        self._create_test_data()
    
    def tearDown(self):
        """Clean up test fixtures"""
        # Remove temporary database
        if os.path.exists(self.test_db_path):
            os.unlink(self.test_db_path)
    
    def _create_test_data(self):
        """Create test data in database"""
        today = jdatetime.date.today()
        
        # Create some events
        for i in range(5):
            date = (today + jdatetime.timedelta(days=i)).strftime('%Y-%m-%d')
            self.db.create_event(
                date=date,
                title=f"Test Meeting {i+1}",
                attendee=f"Person {i+1}",
                location="Office"
            )
        
        # Create some tasks
        for i in range(5):
            due_date = (today + jdatetime.timedelta(days=i)).strftime('%Y-%m-%d')
            self.db.create_task(
                due_date=due_date,
                description=f"Test Task {i+1}",
                project="Test Project",
                status="done" if i % 2 == 0 else "undone"
            )
    
    # ===================== Phase 2.1: Productivity Analysis =====================
    
    def test_productivity_patterns(self):
        """Test productivity pattern analysis"""
        patterns = self.productivity_analyzer.analyze_productivity_patterns(days_back=30)
        
        self.assertIsInstance(patterns, dict)
        self.assertIn('analysis_period_days', patterns)
        self.assertIn('total_tasks_completed', patterns)
        self.assertIn('peak_hours', patterns)
    
    def test_stress_detection(self):
        """Test stress signal detection"""
        stress = self.productivity_analyzer.detect_stress_signals(days_back=14)
        
        self.assertIsInstance(stress, dict)
        self.assertIn('stress_level', stress)
        self.assertIn('signals', stress)
    
    def test_weekly_insights(self):
        """Test weekly insights generation"""
        insights = self.productivity_analyzer.generate_weekly_insights()
        
        self.assertIsInstance(insights, dict)
        self.assertIn('week_start', insights)
        self.assertIn('tasks_completed', insights)
        self.assertIn('recommendations', insights)
    
    # ===================== Phase 2.2: Learning Engine =====================
    
    def test_learn_preference(self):
        """Test learning user preferences"""
        self.learning_engine.learn_preference(
            'category',
            'meeting_type',
            'team_meeting',
            confidence=0.8
        )
        
        value = self.learning_engine.get_preference('category', 'meeting_type')
        self.assertEqual(value, 'team_meeting')
    
    def test_suggest_category(self):
        """Test category suggestion"""
        # Learn some patterns
        self.learning_engine.learn_categorization("team meeting", "meetings")
        self.learning_engine.learn_categorization("team standup", "meetings")
        
        category = self.learning_engine.suggest_category("team sync")
        # Should suggest 'meetings' based on learned patterns
        self.assertIsNotNone(category)
    
    def test_frequent_values(self):
        """Test frequent values tracking"""
        self.learning_engine.learn_frequently_used_value('event', 'location', 'Office')
        self.learning_engine.learn_frequently_used_value('event', 'location', 'Office')
        self.learning_engine.learn_frequently_used_value('event', 'location', 'Conference Room')
        
        values = self.learning_engine.get_frequent_values('event', 'location')
        self.assertIn('Office', values)
    
    # ===================== Phase 2.3: Pattern Detection & Automation =====================
    
    def test_recurring_pattern_detection(self):
        """Test recurring pattern detection"""
        # Create recurring events
        today = jdatetime.date.today()
        for i in range(5):
            date = (today + jdatetime.timedelta(days=i*7)).strftime('%Y-%m-%d')
            self.db.create_event(
                date=date,
                title="Weekly Team Meeting",
                location="Office"
            )
        
        patterns = self.pattern_detector.detect_recurring_events(days_back=60, min_frequency=3)
        self.assertGreater(len(patterns), 0)
    
    def test_automation_opportunities(self):
        """Test automation opportunity detection"""
        opportunities = self.pattern_detector.detect_automation_opportunities(days_back=60)
        
        self.assertIsInstance(opportunities, list)
        # Each opportunity should have required fields
        if opportunities:
            opp = opportunities[0]
            self.assertIn('type', opp)
            self.assertIn('suggestion', opp)
    
    # ===================== Phase 2.4: Multi-Document Synthesis =====================
    
    def test_multi_document_synthesis(self):
        """Test multi-document synthesis"""
        synthesizer = MultiDocumentSynthesizer()
        
        documents = [
            {'content': 'Document 1 about project A', 'metadata': {'document_id': 'doc1'}},
            {'content': 'Document 2 about project A', 'metadata': {'document_id': 'doc2'}}
        ]
        
        result = synthesizer.synthesize_documents(
            documents=documents,
            query="What is project A about?",
            max_documents=2
        )
        
        self.assertIsInstance(result, dict)
        self.assertIn('answer', result)
        self.assertIn('sources', result)
    
    # ===================== Phase 2.7: Role-Based Summarization =====================
    
    def test_role_based_summary(self):
        """Test role-based summarization"""
        summarizer = RoleBasedSummarizer()
        
        document = "This is a test document with financial data: $100,000 budget. Technical requirements: Python 3.9+. Action items: Review by Friday."
        
        summary = summarizer.summarize_for_role(
            document_content=document,
            role='ceo',
            summary_length='brief'
        )
        
        self.assertIsInstance(summary, dict)
        self.assertIn('summary', summary)
        self.assertIn('role', summary)
    
    def test_action_extraction(self):
        """Test action item extraction"""
        extractor = ActionExtractor()
        
        document = "Action items: 1. Review proposal by Friday. 2. Contact John by Monday. 3. Submit report by end of week."
        
        actions = extractor.extract_actions(document)
        
        self.assertIsInstance(actions, list)
        # Should extract at least some actions
        if actions:
            self.assertIn('description', actions[0])
    
    # ===================== Phase 2.8: Meeting Preparation =====================
    
    def test_agenda_analysis(self):
        """Test agenda analysis"""
        analyzer = AgendaAnalyzer()
        
        agenda = """
        Meeting Agenda:
        1. Review Q4 results
        2. Discuss budget for next quarter
        3. Team updates
        4. Action items
        
        Participants: John, Jane, Bob
        """
        
        analysis = analyzer.analyze_agenda(agenda)
        
        self.assertIsInstance(analysis, dict)
        self.assertIn('agenda_items', analysis)
        self.assertIn('participants', analysis)
    
    def test_briefing_generation(self):
        """Test briefing packet generation"""
        generator = BriefingGenerator(db_path=self.test_db_path)
        
        briefing = generator.generate_briefing_packet(
            agenda_text="Meeting: Review project status. Participants: Team",
            meeting_title="Project Review",
            meeting_date=jdatetime.date.today().strftime('%Y-%m-%d')
        )
        
        self.assertIsInstance(briefing, dict)
        self.assertIn('executive_summary', briefing)
        self.assertIn('preparation_checklist', briefing)
    
    def test_talking_points(self):
        """Test talking point suggestion"""
        suggester = TalkingPointSuggester()
        
        agenda = "Meeting: Budget discussion. Topics: Q4 review, Next quarter planning."
        
        points = suggester.suggest_talking_points(
            agenda_text=agenda,
            user_role="manager"
        )
        
        self.assertIsInstance(points, dict)
        self.assertIn('talking_points_by_topic', points)
    
    def test_question_prediction(self):
        """Test question prediction"""
        predictor = QuestionPredictor()
        
        agenda = "Meeting: Product launch. Topics: Timeline, Budget, Resources."
        
        questions = predictor.predict_questions(
            agenda_text=agenda,
            participant_roles=["manager", "developer"]
        )
        
        self.assertIsInstance(questions, dict)
        self.assertIn('questions_by_role', questions)
    
    # ===================== Phase 2.10: Document Generation =====================
    
    def test_document_generation(self):
        """Test document generation"""
        generator = DocumentGenerator()
        
        data = {
            'title': 'Test Report',
            'sections': ['Section 1', 'Section 2'],
            'summary': 'This is a test report'
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            output_path = f.name
        
        try:
            result = generator.generate_report(
                data=data,
                report_type='summary',
                format='markdown',
                output_path=output_path
            )
            
            self.assertTrue(result.get('success'))
            self.assertTrue(os.path.exists(output_path))
        finally:
            if os.path.exists(output_path):
                os.unlink(output_path)
    
    def test_weekly_report_generation(self):
        """Test weekly report generation"""
        generator = DocumentGenerator()
        
        week_data = {
            'week': '2024-01-01 to 2024-01-07',
            'tasks_completed': 10,
            'meetings': 5,
            'metrics': {'productivity': 0.8}
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            output_path = f.name
        
        try:
            result = generator.generate_weekly_report(
                week_data=week_data,
                format='markdown',
                output_path=output_path
            )
            
            self.assertTrue(result.get('success'))
            self.assertTrue(os.path.exists(output_path))
        finally:
            if os.path.exists(output_path):
                os.unlink(output_path)


class TestPhase2Integration(unittest.TestCase):
    """Integration tests for Phase 2 features"""
    
    def test_tools_import(self):
        """Test that all Phase 2 tools can be imported"""
        try:
            from intelligence.tools.insight_tools import ALL_INSIGHT_TOOLS
            from intelligence.tools.learning_tools import ALL_LEARNING_TOOLS
            from intelligence.tools.automation_tools import ALL_AUTOMATION_TOOLS
            from intelligence.tools.document_tools import ALL_DOCUMENT_TOOLS
            
            self.assertGreater(len(ALL_INSIGHT_TOOLS), 0)
            self.assertGreater(len(ALL_LEARNING_TOOLS), 0)
            self.assertGreater(len(ALL_AUTOMATION_TOOLS), 0)
            self.assertGreater(len(ALL_DOCUMENT_TOOLS), 0)
        except ImportError as e:
            self.fail(f"Failed to import Phase 2 tools: {e}")
    
    def test_tools_integration(self):
        """Test that tools are integrated into main tools module"""
        try:
            from tools import ALL_TOOLS
            
            # Check that Phase 2 tools are included
            tool_names = [tool.name for tool in ALL_TOOLS if hasattr(tool, 'name')]
            
            # Should have insight tools
            has_insight = any('insight' in name.lower() for name in tool_names)
            # Should have learning tools
            has_learning = any('learn' in name.lower() or 'preference' in name.lower() for name in tool_names)
            # Should have automation tools
            has_automation = any('automation' in name.lower() or 'pattern' in name.lower() for name in tool_names)
            
            # At least some Phase 2 tools should be present
            self.assertTrue(has_insight or has_learning or has_automation, 
                          "Phase 2 tools not found in ALL_TOOLS")
        except Exception as e:
            self.fail(f"Failed to test tools integration: {e}")


if __name__ == '__main__':
    # Run tests
    unittest.main(verbosity=2)

