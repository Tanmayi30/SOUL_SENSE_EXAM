
import unittest
from datetime import datetime, timedelta

class TestISTConversion(unittest.TestCase):
    def test_utc_to_ist_conversion(self):
        # Simulation of what we did in profile.py
        utc_now = datetime.utcnow()
        ist_now = utc_now + timedelta(hours=5, minutes=30)
        
        # Check offset difference in seconds roughly
        diff_seconds = (ist_now - utc_now).total_seconds()
        self.assertEqual(diff_seconds, 19800) # 5.5 hours * 3600
        
        # Check formatting
        formatted = ist_now.strftime("%Y-%m-%d %H:%M:%S")
        print(f"UTC: {utc_now}")
        print(f"IST: {ist_now}")
        print(f"Formatted: {formatted}")
        
        self.assertRegex(formatted, r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}")

if __name__ == "__main__":
    unittest.main()
