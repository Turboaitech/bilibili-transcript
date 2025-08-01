#!/usr/bin/env python3
"""
API 状态监控脚本
"""

import requests
import time

def check_api():
    """检查 API 状态"""
    endpoints = [
        "/api/test",
        "/api/get-pending-task", 
        "/api/submit-task"
    ]
    
    base_url = "https://bilibili-transcript.vercel.app"
    
    print(f"🔍 检查 {base_url} 的 API 状态...")
    
    for endpoint in endpoints:
        url = base_url + endpoint
        try:
            if endpoint == "/api/submit-task":
                # POST 请求
                response = requests.post(url, json={"videoUrl": "test"}, timeout=5)
            else:
                # GET 请求
                response = requests.get(url, timeout=5)
                
            if response.status_code == 200:
                print(f"✅ {endpoint}: 工作正常")
                try:
                    data = response.json()
                    print(f"   📋 响应: {data}")
                except:
                    print(f"   📝 响应: {response.text[:100]}")
            else:
                print(f"❌ {endpoint}: {response.status_code}")
                
        except Exception as e:
            print(f"❌ {endpoint}: 连接失败 ({e})")
    
    print("-" * 50)

def main():
    print("🚀 API 状态监控")
    print("按 Ctrl+C 停止监控")
    print("=" * 50)
    
    try:
        while True:
            check_api()
            print("⏳ 等待 30 秒...")
            time.sleep(30)
    except KeyboardInterrupt:
        print("\n👋 监控已停止")

if __name__ == "__main__":
    main()