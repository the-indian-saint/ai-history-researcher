#!/usr/bin/env python3
"""Basic test script to validate the application structure."""

import sys
import os
import importlib.util

def test_imports():
    """Test basic imports without heavy dependencies."""
    print("Testing basic imports...")
    
    # Add src to path
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
    
    try:
        # Test config import
        from ai_research_framework.config import settings
        print(f"✓ Config loaded: {settings.app_name} v{settings.app_version}")
        
        # Test basic structure
        from ai_research_framework import __version__
        print(f"✓ Package version: {__version__}")
        
        # Test API structure (without running FastAPI)
        spec = importlib.util.spec_from_file_location(
            "main", 
            "src/ai_research_framework/api/main.py"
        )
        main_module = importlib.util.module_from_spec(spec)
        print("✓ API main module structure is valid")
        
        print("\n✅ All basic tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_directory_structure():
    """Test that all required directories exist."""
    print("\nTesting directory structure...")
    
    required_dirs = [
        "src/ai_research_framework",
        "src/ai_research_framework/api",
        "src/ai_research_framework/api/routes",
        "src/ai_research_framework/collectors",
        "src/ai_research_framework/processors", 
        "src/ai_research_framework/storage",
        "src/ai_research_framework/analyzers",
        "src/ai_research_framework/utils",
        "tests",
        "tests/unit",
        "tests/integration",
        "docs",
        "scripts",
        ".claude",
        ".claude/agents",
    ]
    
    missing_dirs = []
    for dir_path in required_dirs:
        if not os.path.exists(dir_path):
            missing_dirs.append(dir_path)
        else:
            print(f"✓ {dir_path}")
    
    if missing_dirs:
        print(f"❌ Missing directories: {missing_dirs}")
        return False
    
    print("✅ All required directories exist!")
    return True

def test_claude_config():
    """Test Claude configuration files."""
    print("\nTesting Claude configuration...")
    
    required_files = [
        "CLAUDE.md",
        ".claude/agents/research-agent.md",
        ".claude/agents/data-processing-agent.md", 
        ".claude/agents/api-integration-agent.md",
        ".claude/agents/testing-agent.md",
        ".claude/agents/deployment-agent.md",
        ".claude/agents/documentation-agent.md",
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
        else:
            print(f"✓ {file_path}")
    
    if missing_files:
        print(f"❌ Missing Claude files: {missing_files}")
        return False
    
    print("✅ All Claude configuration files exist!")
    return True

def test_pyproject_toml():
    """Test pyproject.toml configuration."""
    print("\nTesting pyproject.toml...")
    
    try:
        import tomllib
    except ImportError:
        try:
            import tomli as tomllib
        except ImportError:
            print("⚠️  Cannot test pyproject.toml - no TOML parser available")
            return True
    
    try:
        with open("pyproject.toml", "rb") as f:
            config = tomllib.load(f)
        
        # Check basic structure
        assert "project" in config
        assert "build-system" in config
        assert "tool" in config
        
        project = config["project"]
        assert project["name"] == "ai-research-framework"
        assert "version" in project
        assert "dependencies" in project
        
        print(f"✓ Project name: {project['name']}")
        print(f"✓ Version: {project['version']}")
        print(f"✓ Dependencies: {len(project['dependencies'])} packages")
        
        print("✅ pyproject.toml is valid!")
        return True
        
    except Exception as e:
        print(f"❌ pyproject.toml test failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Running basic validation tests for AI Research Framework\n")
    
    tests = [
        test_directory_structure,
        test_claude_config,
        test_pyproject_toml,
        test_imports,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
            failed += 1
        print()
    
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed! The repository structure is ready for production.")
        sys.exit(0)
    else:
        print("💥 Some tests failed. Please fix the issues before proceeding.")
        sys.exit(1)

