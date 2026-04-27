from unittest.mock import patch
import main
import io
import sys
import os

def test_interactive():
    # Simulate user entering "Merlin", picking result #1, picking Season 2, and saving to "test_dl"
    inputs = iter(["Merlin", "1", "2", "test_dl"])
    
    with patch('builtins.input', side_effect=lambda _: next(inputs)):
        # Mocking the actual file download part
        with patch('fzseries_api.main.Download.save') as mock_save:
            # Using FileNotFoundError because the library's Auto.run breaks the retry loop on this error
            mock_save.side_effect = FileNotFoundError("Stopped after first episode download call")
            
            print("--- Starting Interactive Test ---")
            try:
                main.interactive_downloader()
            except Exception as e:
                if "Stopped after first episode" in str(e):
                    print("\nTest passed: Search, Selection, and Season setting worked.")
                else:
                    print(f"\nUnexpected error during test: {e}")
                    sys.exit(1)

if __name__ == "__main__":
    test_interactive()
