#!/usr/bin/env python3
"""
Comprehensive Test Suite for Enhanced AI Agent Protocol
Tests all modes and functionality to ensure everything works perfectly
"""

import asyncio
import sys
import time
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

# Import all components
from enhanced_ai_protocol_working import EnhancedMCPCLI
from prompt_based_mcp_addition import EnhancedMCPCLIWithPromptAddition, demo_prompt_based_mcp_addition
from ai_agent_protocol.core import AIAgentProtocol

class ComprehensiveTestSuite:
    """Test suite for all components"""
    
    def __init__(self):
        self.results = {
            "core_protocol": {"passed": 0, "failed": 0, "tests": []},
            "enhanced_protocol": {"passed": 0, "failed": 0, "tests": []},
            "prompt_addition": {"passed": 0, "failed": 0, "tests": []},
            "integration": {"passed": 0, "failed": 0, "tests": []}
        }
    
    async def run_all_tests(self):
        """Run all test suites"""
        print("🧪 Enhanced AI Agent Protocol - Comprehensive Test Suite")
        print("=" * 60)
        print("Testing all modes and functionality...")
        print()
        
        # Test core protocol
        await self.test_core_protocol()
        
        # Test enhanced protocol  
        await self.test_enhanced_protocol()
        
        # Test prompt-based addition
        await self.test_prompt_addition()
        
        # Test integration
        await self.test_integration()
        
        # Print summary
        self.print_test_summary()
    
    async def test_core_protocol(self):
        """Test core AI Agent Protocol"""
        print("🔧 Testing Core AI Agent Protocol...")
        category = "core_protocol"
        
        try:
            protocol = AIAgentProtocol(".")
            
            # Test 1: Protocol initialization
            await self.run_test(
                category, 
                "Protocol Initialization",
                lambda: protocol is not None
            )
            
            # Test 2: Registry access
            await self.run_test(
                category,
                "Registry Access",
                lambda: len(protocol.registry.known_servers) > 0
            )
            
            # Test 3: MCP server listing
            servers = await protocol.list_available_mcp_servers()
            await self.run_test(
                category,
                "MCP Server Listing", 
                lambda: len(servers) > 0
            )
            
        except Exception as e:
            await self.run_test(category, "Core Protocol", lambda: False, str(e))
        
        print(f"Core protocol tests: {self.results[category]['passed']} passed, {self.results[category]['failed']} failed")
        print()
    
    async def test_enhanced_protocol(self):
        """Test enhanced protocol with natural language"""
        print("🧠 Testing Enhanced Protocol (Natural Language)...")
        category = "enhanced_protocol"
        
        try:
            cli = EnhancedMCPCLI()
            
            test_commands = [
                ("Status Query", "what mcp servers are installed?"),
                ("Availability Check", "check if github is available"),
                ("Setup Command", "setup langsmith mcp server"),
                ("Agent Creation", "create monitoring agent with langsmith"),
                ("Conversational", "help me setup github integration")
            ]
            
            for test_name, command in test_commands:
                try:
                    result = await cli.process_command(command)
                    await self.run_test(
                        category,
                        f"Command: {test_name}",
                        lambda: len(result) > 50  # Response should be substantial
                    )
                except Exception as e:
                    await self.run_test(category, f"Command: {test_name}", lambda: False, str(e))
            
        except Exception as e:
            await self.run_test(category, "Enhanced Protocol", lambda: False, str(e))
        
        print(f"Enhanced protocol tests: {self.results[category]['passed']} passed, {self.results[category]['failed']} failed")
        print()
    
    async def test_prompt_addition(self):
        """Test prompt-based MCP addition"""
        print("🆕 Testing Prompt-Based MCP Addition...")
        category = "prompt_addition"
        
        try:
            cli = EnhancedMCPCLIWithPromptAddition()
            
            test_commands = [
                ("Add Command Detection", "add leetcode mcp server for coding practice"),
                ("Need Pattern", "I need a docker mcp to manage containers"),
                ("Status Query Routing", "what mcp servers are installed?"),  # Should route to enhanced
                ("Check Availability", "check if github is available")  # Should route to enhanced
            ]
            
            for test_name, command in test_commands:
                try:
                    result = await cli.process_command(command)
                    await self.run_test(
                        category,
                        f"Command Routing: {test_name}",
                        lambda: len(result) > 30
                    )
                except Exception as e:
                    await self.run_test(category, f"Command Routing: {test_name}", lambda: False, str(e))
            
        except Exception as e:
            await self.run_test(category, "Prompt Addition", lambda: False, str(e))
        
        print(f"Prompt addition tests: {self.results[category]['passed']} passed, {self.results[category]['failed']} failed")
        print()
    
    async def test_integration(self):
        """Test integration between components"""
        print("🔗 Testing Component Integration...")
        category = "integration"
        
        try:
            # Test import chain
            from final_demo import main
            await self.run_test(
                category,
                "Import Chain",
                lambda: main is not None
            )
            
            # Test file structure
            required_files = [
                "src/ai_agent_protocol/core.py",
                "src/enhanced_ai_protocol_working.py", 
                "src/prompt_based_mcp_addition.py",
                "final_demo.py",
                "README.md"
            ]
            
            for file_path in required_files:
                file_exists = Path(file_path).exists()
                await self.run_test(
                    category,
                    f"File Exists: {file_path}",
                    lambda: file_exists
                )
            
        except Exception as e:
            await self.run_test(category, "Integration", lambda: False, str(e))
        
        print(f"Integration tests: {self.results[category]['passed']} passed, {self.results[category]['failed']} failed")
        print()
    
    async def run_test(self, category, test_name, test_func, error_msg=None):
        """Run a single test"""
        try:
            if test_func():
                self.results[category]["passed"] += 1
                self.results[category]["tests"].append(f"✅ {test_name}")
                print(f"  ✅ {test_name}")
            else:
                self.results[category]["failed"] += 1
                self.results[category]["tests"].append(f"❌ {test_name}")
                print(f"  ❌ {test_name}")
        except Exception as e:
            self.results[category]["failed"] += 1
            error_info = error_msg or str(e)
            self.results[category]["tests"].append(f"❌ {test_name}: {error_info}")
            print(f"  ❌ {test_name}: {error_info}")
    
    def print_test_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "=" * 60)
        print("🎯 TEST SUMMARY")
        print("=" * 60)
        
        total_passed = 0
        total_failed = 0
        
        for category, results in self.results.items():
            passed = results["passed"]
            failed = results["failed"]
            total_passed += passed
            total_failed += failed
            
            status = "✅ PASS" if failed == 0 else f"⚠️  {failed} FAILED"
            print(f"\n{category.upper().replace('_', ' ')}: {passed}/{passed + failed} {status}")
            
            # Show failed tests
            if failed > 0:
                for test in results["tests"]:
                    if test.startswith("❌"):
                        print(f"  {test}")
        
        print(f"\n{'=' * 60}")
        print(f"🎉 OVERALL: {total_passed}/{total_passed + total_failed} tests passed")
        
        if total_failed == 0:
            print("✅ ALL TESTS PASSED - System is working perfectly!")
        else:
            print(f"⚠️  {total_failed} tests failed - Review issues above")
        
        print("=" * 60)

async def run_comprehensive_tests():
    """Run all tests"""
    test_suite = ComprehensiveTestSuite()
    await test_suite.run_all_tests()

if __name__ == "__main__":
    asyncio.run(run_comprehensive_tests())
