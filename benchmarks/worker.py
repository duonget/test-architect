"""Run unittest candidates; infrastructure errors never count as killed bugs."""
import unittest

suite = unittest.defaultTestLoader.discover(".", pattern="test_*.py")
result = unittest.TextTestRunner(verbosity=2).run(suite)
if result.errors or result.testsRun == 0 or result.skipped or result.expectedFailures or result.unexpectedSuccesses:
    raise SystemExit(3)
raise SystemExit(1 if result.failures else 0)
