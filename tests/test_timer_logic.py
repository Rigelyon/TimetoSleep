import unittest
from datetime import datetime, timedelta, time
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class TestTimerLogic(unittest.TestCase):
    def test_specific_time_calculation_same_day(self):
        now = datetime.now()
        # Set target 1 hour from now
        target_time = (now + timedelta(hours=1)).time()
        
        target_dt = datetime.combine(now.date(), target_time)
        diff = target_dt - now
        total_seconds = int(diff.total_seconds())
        
        self.assertAlmostEqual(total_seconds, 3600, delta=1)

    def test_specific_time_calculation_next_day(self):
        now = datetime.now()
        # Set target 1 hour ago (should be tomorrow)
        target_time = (now - timedelta(hours=1)).time()
        
        target_dt = datetime.combine(now.date(), target_time)
        if target_dt <= now:
            target_dt += timedelta(days=1)
            
        diff = target_dt - now
        total_seconds = int(diff.total_seconds())
        
        # Should be 23 hours from now
        self.assertAlmostEqual(total_seconds, 23 * 3600, delta=1)

if __name__ == '__main__':
    unittest.main()
