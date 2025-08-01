#!/usr/bin/env python3
"""
简化的测试脚本
"""

import subprocess
import sys
import os

def install_requests():
    """安装 requests 包"""
    try:
        import requests
        print("✅ requests 已安装")
        return True
    except ImportError:
        print("📦 正在安装 requests...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "--break-system-packages", "requests"], 
                         check=True, capture_output=True)
            print("✅ requests 安装成功")
            return True
        except subprocess.CalledProcessError:
            print("❌ requests 安装失败")
            return False

def test_api():
    """测试 API"""
    try:
        import requests
        
        print("🔍 测试 API 连接...")
        url = "https://bilibili-transcript.vercel.app/api/get-pending-task"
        
        response = requests.get(url, timeout=10)
        print(f"📡 响应状态: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ API 正常工作")
            print(f"📋 响应数据: {data}")
            return True
        else:
            print("⚠️  API 返回错误状态")
            print(f"📄 响应内容: {response.text[:200]}...")
            return False
            
    except Exception as e:
        print(f"❌ API 测试失败: {e}")
        return False

def main():
    print("🚀 Bilibili 转文字 Worker 测试")
    print("=" * 40)
    
    # 1. 安装依赖
    if not install_requests():
        return
    
    # 2. 测试 API
    test_api()
    
    print("\n📋 下一步：")
    print("1. 确认 Vercel 环境变量已设置")
    print("2. 在 Vercel 重新部署项目")
    print("3. 运行: python3 worker-enhanced.py")

if __name__ == "__main__":
    main()