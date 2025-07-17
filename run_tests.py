import subprocess
import sys
import os

def run_tests():
    print("🧪 Running tests for Accounting application...")
    print("=" * 50)
    
    project_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(project_dir)
    
    print("📦 Installing test dependencies...")
    subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                  capture_output=True)
    
    print("\n🚀 Running tests...")
    cmd = [
        sys.executable, "-m", "pytest",
        "-v",
        "--tb=short",
        "--color=yes",
        "tests/"
    ]
    
    try:
        result = subprocess.run(cmd, check=False)
        
        if result.returncode == 0:
            print("\n✅ All tests passed!")
        else:
            print(f"\n❌ Some tests failed. Exit code: {result.returncode}")
            
        return result.returncode
        
    except KeyboardInterrupt:
        print("\n⚠️  Tests interrupted by user")
        return 1
    except Exception as e:
        print(f"\n💥 Error running tests: {e}")
        return 1

def run_specific_test(test_path):
    print(f"🎯 Running specific test: {test_path}")
    print("=" * 50)
    
    cmd = [
        sys.executable, "-m", "pytest",
        "-v",
        "--tb=short",
        "--color=yes",
        test_path
    ]
    
    result = subprocess.run(cmd, check=False)
    return result.returncode

if __name__ == "__main__":
    if len(sys.argv) > 1:
        test_path = sys.argv[1]
        exit_code = run_specific_test(test_path)
    else:
        exit_code = run_tests()
    
    sys.exit(exit_code) 