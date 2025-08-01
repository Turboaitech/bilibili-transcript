#!/usr/bin/env python3
"""
Bilibili Video Transcript Worker
本地 Python 脚本，用于轮询获取任务并处理
"""

import requests
import time
import json
import sys
import os
from typing import Optional, Dict, Any

class BilibiliTranscriptWorker:
    def __init__(self, api_base_url: str, poll_interval: int = 5):
        """
        初始化工作器
        
        Args:
            api_base_url: API 基础URL (例如: https://your-app.vercel.app)
            poll_interval: 轮询间隔（秒）
        """
        self.api_base_url = api_base_url.rstrip('/')
        self.poll_interval = poll_interval
        self.session = requests.Session()
        
    def get_pending_task(self) -> Optional[Dict[str, Any]]:
        """获取待处理任务"""
        try:
            response = self.session.get(f"{self.api_base_url}/api/get-pending-task")
            response.raise_for_status()
            
            data = response.json()
            return data.get('task')
            
        except requests.exceptions.RequestException as e:
            print(f"❌ 获取任务失败: {e}")
            return None
            
    def update_task(self, task_id: str, result: str = None, error: str = None) -> bool:
        """更新任务结果"""
        try:
            payload = {"taskId": task_id}
            if result:
                payload["result"] = result
            if error:
                payload["error"] = error
                
            response = self.session.post(
                f"{self.api_base_url}/api/get-pending-task",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            
            data = response.json()
            return data.get('success', False)
            
        except requests.exceptions.RequestException as e:
            print(f"❌ 更新任务失败: {e}")
            return False
            
    def process_video(self, video_url: str, video_id: str) -> str:
        """
        处理视频转文字
        
        这里是示例实现，实际使用时需要集成真实的转录服务
        比如使用 whisper、讯飞语音等
        """
        print(f"🔄 开始处理视频: {video_id}")
        print(f"📺 视频URL: {video_url}")
        
        # 模拟处理过程
        import time
        time.sleep(2)
        
        # 这里应该是真实的视频下载和转录逻辑
        # 示例返回
        mock_transcript = f"""
这是视频 {video_id} 的转录文本示例。

实际使用时，这里应该包含：
1. 视频下载逻辑
2. 音频提取
3. 语音转文字（使用 whisper 或其他服务）
4. 文本后处理

时间戳: {time.strftime('%Y-%m-%d %H:%M:%S')}
        """.strip()
        
        return mock_transcript
        
    def run(self):
        """运行工作器主循环"""
        print(f"🚀 启动 Bilibili 转录工作器")
        print(f"🌐 API URL: {self.api_base_url}")
        print(f"⏱️  轮询间隔: {self.poll_interval}秒")
        print(f"{'='*50}")
        
        while True:
            try:
                # 获取待处理任务
                task = self.get_pending_task()
                
                if not task:
                    print("⏳ 暂无待处理任务，等待中...")
                    time.sleep(self.poll_interval)
                    continue
                    
                task_id = task['taskId']
                video_url = task['videoUrl']
                video_id = task['videoId']
                
                print(f"\n📋 获取到新任务: {task_id}")
                print(f"📺 视频ID: {video_id}")
                
                try:
                    # 处理视频
                    result = self.process_video(video_url, video_id)
                    
                    # 更新任务结果
                    if self.update_task(task_id, result=result):
                        print(f"✅ 任务完成: {task_id}")
                    else:
                        print(f"⚠️  任务结果更新失败: {task_id}")
                        
                except Exception as e:
                    error_msg = f"处理视频时出错: {str(e)}"
                    print(f"❌ {error_msg}")
                    
                    # 更新任务错误状态
                    self.update_task(task_id, error=error_msg)
                    
            except KeyboardInterrupt:
                print("\n\n👋 收到中断信号，正在退出...")
                break
                
            except Exception as e:
                print(f"❌ 工作器运行错误: {e}")
                time.sleep(self.poll_interval)


def main():
    """主函数"""
    # 从环境变量或命令行参数获取配置
    api_url = os.getenv('API_BASE_URL')
    
    if not api_url and len(sys.argv) > 1:
        api_url = sys.argv[1]
        
    if not api_url:
        print("❌ 请提供 API URL")
        print("使用方法:")
        print("1. 命令行参数: python worker.py https://your-app.vercel.app")
        print("2. 环境变量: export API_BASE_URL=https://your-app.vercel.app")
        sys.exit(1)
        
    # 轮询间隔
    poll_interval = int(os.getenv('POLL_INTERVAL', '5'))
    
    # 创建并运行工作器
    worker = BilibiliTranscriptWorker(api_url, poll_interval)
    worker.run()


if __name__ == "__main__":
    main()