#!/usr/bin/env python3
"""
Bilibili 转文字 Worker 设置脚本
帮助查找正确的 Vercel 地址并配置 worker
"""

import requests
import time
import sys
from pathlib import Path

def test_vercel_url(url):
    """测试 Vercel URL 是否可用"""
    try:
        response = requests.get(f"{url}/api/get-pending-task", timeout=10)
        if response.status_code == 200:
            data = response.json()
            return True, "✅ API 正常响应"
        elif response.status_code == 404:
            return False, "❌ API 端点不存在"
        else:
            return False, f"❌ 响应错误: {response.status_code}"
    except requests.exceptions.RequestException as e:
        return False, f"❌ 连接失败: {str(e)}"

def find_vercel_deployment():
    """尝试找到正确的 Vercel 部署地址"""
    print("🔍 正在查找你的 Vercel 部署地址...")
    
    # 可能的地址格式
    possible_urls = [
        "https://bilibili-transcript.vercel.app",
        "https://bilibili-transcript-turbo-ais-projects.vercel.app",
        "https://bilibili-transcript-turboaitechs-projects.vercel.app",
        "https://bilibili-transcript-git-main-turbo-ais-projects.vercel.app"
    ]
    
    for url in possible_urls:
        print(f"📡 测试: {url}")
        success, message = test_vercel_url(url)
        print(f"   {message}")
        
        if success:
            return url
        
        time.sleep(1)  # 避免请求过快
    
    return None

def configure_worker(vercel_url):
    """配置 worker 文件"""
    worker_file = Path("worker-enhanced.py")
    
    if not worker_file.exists():
        print("❌ worker-enhanced.py 文件不存在")
        return False
    
    # 读取文件
    content = worker_file.read_text()
    
    # 替换 API 地址
    old_line = 'API_BASE = "REPLACE_WITH_YOUR_VERCEL_URL/api"'
    new_line = f'API_BASE = "{vercel_url}/api"'
    
    if old_line in content:
        content = content.replace(old_line, new_line)
        worker_file.write_text(content)
        print(f"✅ 已配置 API 地址: {vercel_url}/api")
        return True
    else:
        print("⚠️  未找到需要替换的配置行")
        return False

def main():
    print("🚀 Bilibili 转文字 Worker 设置")
    print("=" * 50)
    
    # 1. 查找 Vercel 部署
    vercel_url = find_vercel_deployment()
    
    if not vercel_url:
        print("\n❌ 未找到可用的 Vercel 部署地址")
        print("\n请检查：")
        print("1. 确认已在 Vercel 成功部署项目")
        print("2. 确认环境变量已正确设置")
        print("3. 确认项目没有设置密码保护")
        print("\n手动操作：")
        print("1. 访问 https://vercel.com/dashboard")
        print("2. 找到你的 bilibili-transcript 项目")
        print("3. 复制项目的完整 URL")
        print("4. 手动编辑 worker-enhanced.py 文件，替换 API_BASE")
        return
    
    print(f"\n🎉 找到可用地址: {vercel_url}")
    
    # 2. 配置 worker
    if configure_worker(vercel_url):
        print("\n✅ Worker 配置完成！")
        print("\n下一步：")
        print("1. 运行: python3 worker-enhanced.py")
        print("2. 打开网站提交测试任务")
        print("3. 查看 iCloud Drive 的转录结果")
        print(f"\n网站地址: {vercel_url}")
    else:
        print("\n❌ Worker 配置失败")

if __name__ == "__main__":
    main()