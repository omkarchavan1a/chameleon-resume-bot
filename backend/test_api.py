"""
Chameleon Resume Bot - Comprehensive API Test Suite
Tests all endpoints including health, user registration, templates, resume generation, admin, and PDF generation.
"""
import requests
import json
import sys

# Configuration
BASE_URL = "http://localhost:8002"
TEST_EMAIL = "test.user@example.com"
TEST_PHONE = "9876543210"

# Colors for terminal output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
RESET = "\033[0m"

def print_success(msg):
    print(f"{GREEN}✅ {msg}{RESET}")

def print_error(msg):
    print(f"{RED}❌ {msg}{RESET}")

def print_warning(msg):
    print(f"{YELLOW}⚠️  {msg}{RESET}")

def print_section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

# ─── Test 1: Health Check ────────────────────────────────────────────────────
def test_health():
    """Test health endpoint"""
    try:
        r = requests.get(f"{BASE_URL}/api/health", timeout=5)
        if r.status_code == 200:
            data = r.json()
            print_success(f"Health check passed")
            print(f"   Model: {data.get('model', 'N/A')}")
            print(f"   Database: {data.get('database', 'N/A')}")
            print(f"   API Key Configured: {data.get('api_key_configured', False)}")
            return True
        else:
            print_error(f"Health check failed: HTTP {r.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print_error(f"Cannot connect to {BASE_URL}. Is the server running?")
        return False
    except Exception as e:
        print_error(f"Health check error: {e}")
        return False

# ─── Test 2: User Registration ───────────────────────────────────────────────
def test_register_user():
    """Test user registration endpoint"""
    data = {
        "email": TEST_EMAIL,
        "phone": TEST_PHONE
    }
    try:
        r = requests.post(f"{BASE_URL}/api/register-user", json=data, timeout=10)
        if r.status_code == 200:
            result = r.json()
            if result.get("success"):
                print_success(f"User registration passed")
                print(f"   Email: {result.get('email', 'N/A')}")
                return True
            else:
                print_error(f"Registration returned success=false")
                return False
        elif r.status_code == 422:
            print_warning(f"Registration validation error: {r.text}")
            return False
        else:
            print_error(f"Registration failed: HTTP {r.status_code} - {r.text}")
            return False
    except Exception as e:
        print_error(f"Registration error: {e}")
        return False

# ─── Test 3: Templates Endpoint ──────────────────────────────────────────────
def test_templates():
    """Test templates endpoint"""
    try:
        r = requests.get(f"{BASE_URL}/api/templates", timeout=5)
        if r.status_code == 200:
            data = r.json()
            templates = data.get("templates", [])
            print_success(f"Templates endpoint passed ({len(templates)} templates)")
            if templates:
                print(f"   First template: {templates[0].get('title', 'N/A')}")
            return True
        else:
            print_error(f"Templates failed: HTTP {r.status_code}")
            return False
    except Exception as e:
        print_error(f"Templates error: {e}")
        return False

# ─── Test 4: History Endpoint ─────────────────────────────────────────────────
def test_history():
    """Test history endpoint"""
    try:
        r = requests.get(f"{BASE_URL}/api/history", timeout=5)
        if r.status_code == 200:
            data = r.json()
            count = len(data) if isinstance(data, list) else 0
            print_success(f"History endpoint passed ({count} items)")
            return True
        else:
            print_error(f"History failed: HTTP {r.status_code}")
            return False
    except Exception as e:
        print_error(f"History error: {e}")
        return False

# ─── Test 5: PDF Generation ───────────────────────────────────────────────────
def test_generate_pdf():
    """Test PDF generation endpoint"""
    data = {
        "markdown": "# Test Resume\n\n**Name:** John Doe\n**Role:** Software Engineer\n\n## Skills\n- Python\n- FastAPI\n- MongoDB",
        "filename": "test.pdf"
    }
    try:
        r = requests.post(f"{BASE_URL}/api/generate-pdf", json=data, timeout=15)
        if r.status_code == 200:
            content_type = r.headers.get("content-type", "")
            if "application/pdf" in content_type:
                print_success(f"PDF generation passed ({len(r.content)} bytes)")
                return True
            else:
                print_error(f"PDF returned wrong content-type: {content_type}")
                return False
        elif r.status_code == 503:
            print_warning(f"PDF generation not available (WeasyPrint not installed)")
            return False
        else:
            print_error(f"PDF generation failed: HTTP {r.status_code} - {r.text[:100]}")
            return False
    except Exception as e:
        print_error(f"PDF generation error: {e}")
        return False

# ─── Test 6: Admin Login ─────────────────────────────────────────────────────
def test_admin_login():
    """Test admin login endpoint"""
    data = {
        "email": "omkarchavan1500@gmail.com",
        "password": "omkarchavan@1"
    }
    try:
        r = requests.post(f"{BASE_URL}/api/admin/login", json=data, timeout=5)
        if r.status_code == 200:
            result = r.json()
            if result.get("success"):
                print_success(f"Admin login passed")
                # Store cookies for next test
                return True, r.cookies
            else:
                print_error(f"Admin login returned success=false")
                return False, None
        else:
            print_error(f"Admin login failed: HTTP {r.status_code}")
            return False, None
    except Exception as e:
        print_error(f"Admin login error: {e}")
        return False, None

# ─── Test 7: Admin Check ─────────────────────────────────────────────────────
def test_admin_check(cookies):
    """Test admin check endpoint"""
    if not cookies:
        print_warning("Skipping admin check (no session)")
        return False
    try:
        r = requests.get(f"{BASE_URL}/api/admin/check", cookies=cookies, timeout=5)
        if r.status_code == 200:
            result = r.json()
            if result.get("authenticated"):
                print_success(f"Admin check passed (authenticated)")
                return True
            else:
                print_error(f"Admin check failed (not authenticated)")
                return False
        else:
            print_error(f"Admin check failed: HTTP {r.status_code}")
            return False
    except Exception as e:
        print_error(f"Admin check error: {e}")
        return False

# ─── Test 8: Admin Stats ──────────────────────────────────────────────────────
def test_admin_stats(cookies):
    """Test admin stats endpoint"""
    if not cookies:
        print_warning("Skipping admin stats (no session)")
        return False
    try:
        r = requests.get(f"{BASE_URL}/api/admin/stats", cookies=cookies, timeout=5)
        if r.status_code == 200:
            result = r.json()
            print_success(f"Admin stats passed")
            print(f"   Total Users: {result.get('total_users', 'N/A')}")
            print(f"   Total Resumes: {result.get('total_resumes', 'N/A')}")
            print(f"   Today's Users: {result.get('today_users', 'N/A')}")
            print(f"   DB Status: {result.get('database_status', 'N/A')}")
            return True
        else:
            print_error(f"Admin stats failed: HTTP {r.status_code}")
            return False
    except Exception as e:
        print_error(f"Admin stats error: {e}")
        return False

# ─── Test 9: Resume Generation (with API Key Check) ────────────────────────────
def test_generate_resume():
    """Test resume generation endpoint"""
    payload = {
        "master_data": "Software Engineer with 5 years experience in Python, FastAPI, and MongoDB.",
        "target_position": "Senior Backend Developer",
        "target_city": "Bangalore",
        "job_description": "Looking for a Senior Backend Developer with Python and FastAPI experience.",
        "theme": "bold",
        "user_email": TEST_EMAIL
    }
    try:
        r = requests.post(f"{BASE_URL}/api/generate-resume", json=payload, timeout=60)
        if r.status_code == 200:
            result = r.json()
            resume_md = result.get("resume_markdown", "")
            tokens = result.get("tokens_used", 0)
            if resume_md and len(resume_md) > 100:
                print_success(f"Resume generation passed ({tokens} tokens)")
                print(f"   Generated {len(resume_md)} characters")
                return True
            else:
                print_error(f"Resume generation returned empty content")
                return False
        elif r.status_code == 503:
            print_warning(f"Resume generation skipped: NVIDIA API key not configured")
            return False
        else:
            print_error(f"Resume generation failed: HTTP {r.status_code} - {r.text[:200]}")
            return False
    except requests.exceptions.Timeout:
        print_warning(f"Resume generation timed out (AI service may be slow)")
        return False
    except Exception as e:
        print_error(f"Resume generation error: {e}")
        return False

# ─── Main Test Runner ────────────────────────────────────────────────────────
def run_all_tests():
    """Run all tests and report results"""
    print_section("Chameleon Resume Bot API Tests")
    print(f"Testing against: {BASE_URL}\n")
    
    results = {}
    cookies = None
    
    # Test 1: Health Check
    results["health"] = test_health()
    if not results["health"]:
        print_error("\nHealth check failed. Aborting tests.")
        print("Make sure the server is running: python backend/main.py")
        return 1
    
    # Test 2: User Registration
    results["register"] = test_register_user()
    
    # Test 3: Templates
    results["templates"] = test_templates()
    
    # Test 4: History
    results["history"] = test_history()
    
    # Test 5: PDF Generation
    results["pdf"] = test_generate_pdf()
    
    # Test 6: Admin Login
    admin_ok, cookies = test_admin_login()
    results["admin_login"] = admin_ok
    
    # Test 7: Admin Check (if logged in)
    if cookies:
        results["admin_check"] = test_admin_check(cookies)
        results["admin_stats"] = test_admin_stats(cookies)
    
    # Test 8: Resume Generation (this may take a while)
    print_section("Resume Generation Test")
    print("This may take 10-30 seconds depending on the AI service...")
    results["generate_resume"] = test_generate_resume()
    
    # Print Summary
    print_section("Test Summary")
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    failed = total - passed
    
    for test_name, passed_test in results.items():
        status = f"{GREEN}PASS{RESET}" if passed_test else f"{RED}FAIL{RESET}"
        print(f"  {test_name:20s}: {status}")
    
    print(f"\n{passed}/{total} tests passed")
    
    if failed == 0:
        print_success("All tests passed!")
        return 0
    else:
        print_error(f"{failed} test(s) failed")
        return 1

if __name__ == "__main__":
    sys.exit(run_all_tests())
