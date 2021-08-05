import importlib
import os
import unittest

import pytest


class PreliminariesTest(unittest.TestCase):
    def test_PYTHONHASHSEED_is_zero(self) -> None:
        self.assertEqual(
            os.getenv("PYTHONHASHSEED"),
            "0",
            "CrossHair tests should be run with the PYTHONHASHSEED "
            "environement variable set to 0. Some other tests rely on this "
            "for deterministic behavior.",
        )

    def test_no_modules_named_foo(self) -> None:
        # Try to ensure no leaked autogenerated files are on the path.
        with pytest.raises(ImportError):
            importlib.import_module("foo")


if __name__ == "__main__":
    unittest.main()
