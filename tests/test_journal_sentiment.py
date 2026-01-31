
import pytest
from unittest.mock import MagicMock, patch
import sys

# CRITICAL: Mock app.db at the very beginning to prevent engine creation on import
mock_db = MagicMock()
sys.modules['app.db'] = mock_db

# Mock the session and context manager
mock_session = MagicMock()
mock_db.safe_db_context.return_value.__enter__.return_value = mock_session
mock_db.SessionLocal.return_value = mock_session
mock_db.get_session.return_value = mock_session

# Now we can safely import other things
from app.ui.journal import JournalFeature
from app.models import JournalEntry

class TestJournalSentimentAnalysis:
    """Test suite for journal sentiment analysis functionality (Pure Mock)"""

    @pytest.fixture
    def journal_feature(self):
        """Create a JournalFeature instance for testing"""
        mock_root = MagicMock()
        mock_app = MagicMock()
        mock_app.colors = {
            "bg": "#f0f0f0", "surface": "white", "text_primary": "black",
            "text_secondary": "#666", "primary": "#8B5CF6", "secondary": "#EC4899"
        }
        mock_app.username = "test_user"

        # Initialize feature with mocked analyzer init to prevent NLTK download
        with patch.object(JournalFeature, '_initialize_sentiment_analyzer', MagicMock()):
            feature = JournalFeature(mock_root, app=mock_app)
            
        # Manually mock sentiment analyzer after init
        feature.sia = MagicMock()
        feature.sia.polarity_scores.return_value = {'compound': 0.5}
        return feature

    def test_sentiment_analyzer_initialization(self, journal_feature):
        assert hasattr(journal_feature, 'sia')

    def test_analyze_sentiment_positive(self, journal_feature):
        journal_feature.sia.polarity_scores.return_value = {'compound': 0.8}
        assert journal_feature.analyze_sentiment("Happy") == 80.0

    def test_analyze_sentiment_negative(self, journal_feature):
        journal_feature.sia.polarity_scores.return_value = {'compound': -0.8}
        assert journal_feature.analyze_sentiment("Sad") == -80.0

    def test_analyze_sentiment_neutral(self, journal_feature):
        journal_feature.sia.polarity_scores.return_value = {'compound': 0.0}
        assert journal_feature.analyze_sentiment("Okay") == 0.0

    def test_analyze_sentiment_empty(self, journal_feature):
        assert journal_feature.analyze_sentiment("") == 0.0

    def test_analyze_sentiment_whitespace(self, journal_feature):
        assert journal_feature.analyze_sentiment("   ") == 0.0

    def test_mood_from_score_positive(self, journal_feature):
        assert journal_feature._app_mood_from_score(50) == "Positive"

    def test_mood_from_score_negative(self, journal_feature):
        assert journal_feature._app_mood_from_score(-50) == "Negative"

    def test_mood_from_score_neutral(self, journal_feature):
        assert journal_feature._app_mood_from_score(0) == "Neutral"

    @patch('app.services.journal_service.JournalService.create_entry')
    @patch('app.ui.components.loading_overlay.show_loading')
    @patch('app.ui.components.loading_overlay.hide_loading')
    def test_save_and_analyze_integration(self, mock_hide, mock_show, mock_create_entry, journal_feature):
        # Setup mocks for UI elements
        journal_feature.text_area = MagicMock()
        journal_feature.text_area.get.return_value = "Great!"
        
        for v in ['sleep_hours_var', 'sleep_quality_var', 'energy_level_var', 
                  'stress_level_var', 'work_hours_var', 'screen_time_var']:
            setattr(journal_feature, v, MagicMock())
            getattr(journal_feature, v).get.return_value = 5
            
        journal_feature.tags_entry = MagicMock()
        journal_feature.schedule_text = MagicMock()
        journal_feature.triggers_text = MagicMock()
        journal_feature.parent_root = MagicMock()
        
        # Mock internal method to avoid recursive logic execution
        journal_feature.analyze_sentiment = MagicMock(return_value=80.0)
        
        # Mock show_analysis_results to avoid popup creation
        journal_feature.show_analysis_results = MagicMock()

        journal_feature.save_and_analyze()
        
        assert mock_create_entry.called

class TestJournalServiceDatabase:
    """Mocked service tests"""
    
    def test_create_entry_success(self):
        # Already mocked app.db at module level
        from app.services.journal_service import JournalService
        
        result = JournalService.create_entry(
            username="test", content="c", sentiment_score=50, emotional_patterns=""
        )
        assert result is not None
        assert mock_session.add.called

    def test_get_entries_success(self):
        from app.services.journal_service import JournalService
        mock_query = mock_session.query.return_value
        mock_query.filter_by.return_value.order_by.return_value.all.return_value = ["e1"]
        
        result = JournalService.get_entries("test")
        assert len(result) == 1

class TestJournalModel:
    def test_journal_entry_init(self):
        entry = JournalEntry(username="u", content="c")
        assert entry.username == "u"
