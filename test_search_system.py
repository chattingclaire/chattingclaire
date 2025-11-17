#!/usr/bin/env python3
"""
Test script for Memory & Context Engineering system

Run this after installing dependencies:
    pip install -r requirements.txt

Usage:
    python test_search_system.py
"""

import os
import sys
from datetime import datetime


def test_imports():
    """Test all required imports"""
    print("=" * 60)
    print("Testing imports...")
    print("=" * 60)

    try:
        from langchain.memory import ConversationBufferMemory
        print("✓ langchain.memory")
    except ImportError as e:
        print(f"✗ langchain.memory: {e}")
        return False

    try:
        from langchain_openai import OpenAIEmbeddings, ChatOpenAI
        print("✓ langchain_openai")
    except ImportError as e:
        print(f"✗ langchain_openai: {e}")
        return False

    try:
        from langchain_community.vectorstores import SupabaseVectorStore
        print("✓ langchain_community.vectorstores")
    except ImportError as e:
        print(f"✗ langchain_community.vectorstores: {e}")
        return False

    try:
        from supabase import create_client
        print("✓ supabase")
    except ImportError as e:
        print(f"✗ supabase: {e}")
        return False

    try:
        from fastapi import FastAPI
        print("✓ fastapi")
    except ImportError as e:
        print(f"✗ fastapi: {e}")
        return False

    print("\nAll imports successful!\n")
    return True


def test_env_variables():
    """Test required environment variables"""
    print("=" * 60)
    print("Testing environment variables...")
    print("=" * 60)

    required_vars = [
        "OPENAI_API_KEY",
        "SUPABASE_URL",
        "SUPABASE_KEY",
        "ANTHROPIC_API_KEY",
        "TUSHARE_TOKEN"
    ]

    all_present = True
    for var in required_vars:
        value = os.getenv(var)
        if value:
            masked = value[:10] + "..." if len(value) > 10 else value
            print(f"✓ {var}: {masked}")
        else:
            print(f"✗ {var}: NOT SET")
            all_present = False

    print()
    return all_present


def test_enhanced_context():
    """Test EnhancedContextManager"""
    print("=" * 60)
    print("Testing EnhancedContextManager...")
    print("=" * 60)

    try:
        from memory.enhanced_context import get_enhanced_context_manager

        print("Creating context manager...")
        ctx = get_enhanced_context_manager()
        print("✓ Context manager created")

        # Test query rewriting
        print("\nTesting query rewriting...")
        original_query = "它的业绩怎么样"
        rewritten = ctx.rewrite_query(original_query)
        print(f"  Original: {original_query}")
        print(f"  Rewritten: {rewritten}")
        print("✓ Query rewriting works")

        # Test search (may return empty if no data indexed yet)
        print("\nTesting semantic search...")
        results = ctx.search_similar_content(
            query="贵州茅台",
            limit=5,
            threshold=0.5
        )
        print(f"✓ Search completed (found {len(results)} results)")

        return True

    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_api_structure():
    """Test API structure"""
    print("=" * 60)
    print("Testing API structure...")
    print("=" * 60)

    try:
        from dashboard.backend.search_api import router
        print("✓ search_api router loaded")

        from dashboard.backend.api import app
        print("✓ main api app loaded")

        # Check routes
        routes = [route.path for route in app.routes]
        print(f"\nRegistered routes ({len(routes)}):")
        for route in sorted(routes):
            print(f"  - {route}")

        return True

    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_data_sources():
    """Test data source integrations"""
    print("=" * 60)
    print("Testing data sources...")
    print("=" * 60)

    try:
        from tools.datasources.tushare_tool import tushare_api
        print("✓ Tushare API initialized")

        from tools.datasources.akshare_tool import akshare_api
        print("✓ AKShare API initialized")

        import yfinance as yf
        print("✓ yfinance imported")

        return True

    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("MEMORY & CONTEXT ENGINEERING SYSTEM TEST")
    print("=" * 60)
    print(f"Time: {datetime.now().isoformat()}")
    print()

    # Load .env if exists
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("✓ Loaded .env file\n")
    except ImportError:
        print("⚠ python-dotenv not installed (optional)\n")

    results = {
        "imports": test_imports(),
        "env_vars": test_env_variables(),
        "data_sources": test_data_sources(),
        "enhanced_context": test_enhanced_context(),
        "api_structure": test_api_structure(),
    }

    # Summary
    print("=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    passed = sum(results.values())
    total = len(results)

    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status} - {test_name.replace('_', ' ').title()}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed! System is ready.")
        return 0
    else:
        print("\n⚠ Some tests failed. Check errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
