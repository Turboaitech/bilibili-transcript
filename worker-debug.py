#!/usr/bin/env python3
"""
调试版本的 Worker
"""

import requests
import time
import sys
from datetime import datetime

API_BASE = "https://bilibili-transcript.vercel.app/api"

def test_connection():
    """测试连接"""
    print(f"🔍 测试连接: {API_BASE}")
    
    try:
        response = requests.get(f"{API_BASE}/get-pending-task", timeout=10)
        print(f"📡 状态码: {response.status_code}")
        print(f"📄 响应头: {dict(response.headers)}")
        print(f"📝 响应内容: {response.text[:500]}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"📋 JSON 数据: {data}")
            return True
        else:
            return False
            
    except Exception as e:
        print(f"❌ 连接错误: {e}")
        return False

def main():
    print("🚀 Worker 调试模式")
    print("=" * 40)
    
    # 测试连接
    if test_connection():
        print("✅ API 连接正常")
        
        # 开始轮询
        print("\n🔄 开始轮询任务...")
        count = 0
        while count < 5:  # 只测试 5 次
            print(f"\n⏰ 第 {count + 1} 次检查 ({datetime.now().strftime('%H:%M:%S')})")
            
            try:
                response = requests.get(f"{API_BASE}/get-pending-task", timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    if data.get("task"):
                        print(f"📋 发现任务: {data}")
                        break
                    else:
                        print("💤 暂无任务")
                else:
                    print(f"⚠️  API 错误: {response.status_code}")
                    
            except Exception as e:
                print(f"❌ 请求失败: {e}")
            
            count += 1
            if count < 5:
                print("⏳ 等待 10 秒...")
                time.sleep(10)
                
    else:
        print("❌ API 连接失败")
        print("\n可能的原因:")
        print("1. Vercel 环境变量未设置")
        print("2. 项目未正确部署")
        print("3. API 路由配置错误")

if __name__ == "__main__":
    main()