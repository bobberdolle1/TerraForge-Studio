"""
Test script to verify desktop launcher components work
"""

import sys
from pathlib import Path

def test_imports():
    """Test that all required modules can be imported"""
    print("Testing imports...")
    
    try:
        import webview
        print(f"✓ pywebview {webview.__version__}")
    except ImportError as e:
        print(f"✗ pywebview: {e}")
        return False
    
    try:
        import PyInstaller
        print(f"✓ PyInstaller {PyInstaller.__version__}")
    except ImportError as e:
        print(f"✗ PyInstaller: {e}")
        return False
    
    try:
        from PIL import Image
        print(f"✓ Pillow")
    except ImportError as e:
        print(f"✗ Pillow: {e}")
        return False
    
    try:
        import fastapi
        print(f"✓ FastAPI {fastapi.__version__}")
    except ImportError as e:
        print(f"✗ FastAPI: {e}")
        return False
    
    try:
        import uvicorn
        print(f"✓ Uvicorn")
    except ImportError as e:
        print(f"✗ Uvicorn: {e}")
        return False
    
    return True


def test_webview():
    """Test that webview can be initialized"""
    print("\nTesting webview initialization...")
    
    try:
        import webview
        
        # Create a simple test window (won't show, just test creation)
        window = webview.create_window(
            'Test Window',
            html='<h1>Test</h1>',
            width=400,
            height=300
        )
        print("✓ Webview window created successfully")
        return True
    except Exception as e:
        print(f"✗ Webview test failed: {e}")
        return False


def test_server():
    """Test that FastAPI server can be imported and configured"""
    print("\nTesting FastAPI server...")
    
    try:
        sys.path.insert(0, str(Path(__file__).parent.parent))
        from realworldmapgen.api.main import app
        print("✓ FastAPI app imported successfully")
        return True
    except Exception as e:
        print(f"✗ FastAPI import failed: {e}")
        return False


def main():
    """Run all tests"""
    print("="*60)
    print("TerraForge Studio - Desktop Launcher Tests")
    print("="*60)
    print()
    
    tests = [
        ("Imports", test_imports),
        ("Webview", test_webview),
        ("Server", test_server),
    ]
    
    results = []
    for name, test_func in tests:
        print(f"\n--- Testing {name} ---")
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"✗ Test crashed: {e}")
            results.append((name, False))
    
    print("\n" + "="*60)
    print("Test Results:")
    print("="*60)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{name:20s} {status}")
    
    all_passed = all(result for _, result in results)
    
    print("\n" + "="*60)
    if all_passed:
        print("✓ All tests passed! Ready to build.")
    else:
        print("✗ Some tests failed. Fix issues before building.")
    print("="*60)
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
