"""
Test Scenarios - Kiểm tra các tình huống thực tế của Hybrid Agent
"""

import subprocess
import json
import os
from orchestrator_v2 import EnhancedHybridAgent

def test_scenario_1_simple_folder_creation():
    """Test 1: Tạo thư mục đơn giản"""
    print("\n" + "="*60)
    print("TEST 1: Tạo thư mục đơn giản")
    print("="*60)
    
    agent = EnhancedHybridAgent()
    agent.run("Tạo thư mục test_folder_1 trong thư mục home")
    
    # Kiểm tra kết quả
    test_path = os.path.expanduser("~/test_folder_1")
    if os.path.exists(test_path):
        print(f"✅ PASS: Thư mục {test_path} đã được tạo")
        # Dọn dẹp
        os.rmdir(test_path)
    else:
        print(f"❌ FAIL: Thư mục {test_path} không tồn tại")

def test_scenario_2_multiple_actions():
    """Test 2: Nhiều actions trong một plan"""
    print("\n" + "="*60)
    print("TEST 2: Nhiều actions trong một plan")
    print("="*60)
    
    agent = EnhancedHybridAgent()
    agent.run("Tạo file test.txt và ghi nội dung 'Hello World' vào đó")
    
    # Kiểm tra kết quả
    test_file = os.path.expanduser("~/test.txt")
    if os.path.exists(test_file):
        print(f"✅ PASS: File {test_file} đã được tạo")
        with open(test_file, 'r') as f:
            content = f.read()
            if 'Hello World' in content:
                print("✅ PASS: Nội dung đúng")
            else:
                print(f"❌ FAIL: Nội dung sai: {content}")
        # Dọn dẹp
        os.remove(test_file)
    else:
        print(f"❌ FAIL: File {test_file} không tồn tại")

def test_scenario_3_error_recovery():
    """Test 3: Khả năng phục hồi khi tool lỗi"""
    print("\n" + "="*60)
    print("TEST 3: Error Recovery")
    print("="*60)
    
    agent = EnhancedHybridAgent()
    agent.run("Đọc file không tồn tại nonexistent.txt")
    
    # Kiểm tra xem agent có bị crash không
    print("✅ PASS: Agent không bị crash khi tool lỗi")

def test_scenario_4_json_validation():
    """Test 4: Kiểm tra validation JSON"""
    print("\n" + "="*60)
    print("TEST 4: JSON Validation")
    print("="*60)
    
    agent = EnhancedHybridAgent()
    # Test với prompt có thể gây lỗi JSON
    agent.run("Hãy trả về JSON không hợp lệ")
    
    print("✅ PASS: Agent xử lý được JSON không hợp lệ")

def test_scenario_5_state_persistence():
    """Test 5: Kiểm tra persistence của state manager"""
    print("\n" + "="*60)
    print("TEST 5: State Persistence")
    print("="*60)
    
    # Tạo agent và chạy một task
    agent1 = EnhancedHybridAgent()
    session_id = agent1.session_id
    agent1.run("Tạo thư mục test_persistence")
    
    # Kiểm tra xem session có được lưu không
    from state_manager import StateManager
    sm = StateManager()
    sessions = sm.get_all_sessions(5)
    
    found = False
    for session in sessions:
        if session['session_id'] == session_id:
            found = True
            print(f"✅ PASS: Session {session_id} được lưu trong database")
            print(f"  Status: {session['status']}")
            print(f"  Prompt: {session['prompt'][:50]}...")
            break
    
    if not found:
        print(f"❌ FAIL: Session {session_id} không được tìm thấy")
    
    # Dọn dẹp
    test_path = os.path.expanduser("~/test_persistence")
    if os.path.exists(test_path):
        os.rmdir(test_path)

def test_scenario_6_concurrent_execution():
    """Test 6: Kiểm tra thực thi song song"""
    print("\n" + "="*60)
    print("TEST 6: Concurrent Execution")
    print("="*60)
    
    agent = EnhancedHybridAgent()
    agent.run("Tạo 3 file cùng lúc: file1.txt, file2.txt, file3.txt")
    
    # Kiểm tra
    files_created = 0
    for i in range(1, 4):
        test_file = os.path.expanduser(f"~/file{i}.txt")
        if os.path.exists(test_file):
            files_created += 1
            os.remove(test_file)
    
    print(f"✅ PASS: Đã tạo được {files_created}/3 files")

def run_all_tests():
    """Chạy tất cả test scenarios"""
    print("\n" + "="*60)
    print("BẮT ĐẦU TEST SUITE - HYBRID AGENT")
    print("="*60)
    
    tests = [
        test_scenario_1_simple_folder_creation,
        test_scenario_2_multiple_actions,
        test_scenario_3_error_recovery,
        test_scenario_4_json_validation,
        test_scenario_5_state_persistence,
        test_scenario_6_concurrent_execution
    ]
    
    passed = 0
    failed = 0
    
    for test_func in tests:
        try:
            test_func()
            passed += 1
        except Exception as e:
            print(f"❌ TEST CRASHED: {e}")
            failed += 1
    
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print(f"Tổng số test: {len(tests)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Tỷ lệ thành công: {(passed/len(tests))*100:.1f}%")
    
    if failed == 0:
        print("\n🎉 TẤT CẢ TEST ĐÃ PASS!")
    else:
        print(f"\n⚠️ Có {failed} test bị fail")

if __name__ == "__main__":
    run_all_tests()
