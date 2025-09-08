import unittest
from app.email_utils import EmailManager
import pandas as pd

class TestEmailManager(unittest.TestCase):
    
    def setUp(self):
        self.email_manager = EmailManager()
    
    def test_validate_email(self):
        """Test email validation"""
        # Valid emails
        self.assertTrue(self.email_manager.validate_email("test@example.com"))
        self.assertTrue(self.email_manager.validate_email("user.name@domain.co.uk"))
        
        # Invalid emails
        self.assertFalse(self.email_manager.validate_email("invalid-email"))
        self.assertFalse(self.email_manager.validate_email("test@"))
        self.assertFalse(self.email_manager.validate_email("@domain.com"))
    
    def test_validate_email_list(self):
        """Test email list validation"""
        email_list = [
            "valid@example.com",
            "also.valid@test.org",
            "invalid-email",
            "",
            "another@valid.com"
        ]
        
        valid, invalid = self.email_manager.validate_email_list(email_list)
        
        self.assertEqual(len(valid), 3)
        self.assertEqual(len(invalid), 1)
        self.assertIn("valid@example.com", valid)
        self.assertIn("invalid-email", invalid)
    
    def test_create_email_template(self):
        """Test email template creation"""
        newsletter = self.email_manager.create_email_template('newsletter')
        promotional = self.email_manager.create_email_template('promotional')
        
        self.assertIn('subject', newsletter)
        self.assertIn('body', newsletter)
        self.assertIn('subject', promotional)
        self.assertIn('body', promotional)
        
        # Check that templates are different
        self.assertNotEqual(newsletter['subject'], promotional['subject'])
    
    def test_send_campaign(self):
        """Test campaign sending (simulation)"""
        recipients = ["test1@example.com", "test2@example.com"]
        result = self.email_manager.send_campaign(
            "Test Campaign",
            "Test Subject",
            "Test Content",
            recipients
        )
        
        # Should succeed in simulation mode
        self.assertTrue(result)
    
    def test_create_campaign_report(self):
        """Test campaign report creation"""
        report = self.email_manager.create_campaign_report()
        
        self.assertIn('total_campaigns', report)
        self.assertIn('total_recipients', report)
        self.assertIn('avg_open_rate', report)
        self.assertIn('avg_click_rate', report)
    
    def test_generate_email_analytics(self):
        """Test email analytics generation"""
        analytics = self.email_manager.generate_email_analytics()
        
        self.assertIn('performance_summary', analytics)
        self.assertIn('recommendations', analytics)

if __name__ == '__main__':
    unittest.main()
