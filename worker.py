#!/usr/bin/env python3
"""
Bilibili Video Transcript Worker
本地 Python 脚本，用于轮询获取任务并处理视频转文字
"""

import requests
import time
import json
import sys
import os
from typing import Optional, Dict, Any
import logging
from datetime import datetime

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('worker.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

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
        self.session.timeout = 30
        
        # 统计信息
        self.stats = {
            'total_processed': 0,
            'successful': 0,
            'failed': 0,
            'start_time': datetime.now()
        }
        
    def get_pending_task(self) -> Optional[Dict[str, Any]]:
        """获取待处理任务"""
        try:
            response = self.session.get(f"{self.api_base_url}/api/get-pending-task")
            response.raise_for_status()
            
            data = response.json()
            return data.get('task')
            
        except requests.exceptions.RequestException as e:
            logger.error(f"获取任务失败: {e}")
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
            logger.error(f"更新任务失败: {e}")
            return False
            
    def process_video(self, video_url: str, video_id: str) -> str:
        """
        处理视频转文字
        
        注意：这是示例实现，实际使用时需要集成真实的转录服务
        推荐集成方案：
        1. 使用 yt-dlp 下载视频
        2. 使用 ffmpeg 提取音频
        3. 使用 whisper 或讯飞语音 API 进行语音识别
        4. 后处理文本（去除重复、格式化等）
        """
        logger.info(f"开始处理视频: {video_id}")
        logger.info(f"视频URL: {video_url}")
        
        try:
            # 模拟下载和处理过程
            logger.info("步骤 1/4: 下载视频...")
            time.sleep(1)  # 模拟下载时间
            
            logger.info("步骤 2/4: 提取音频...")
            time.sleep(1)  # 模拟音频提取
            
            logger.info("步骤 3/4: 语音识别...")
            time.sleep(2)  # 模拟语音识别过程
            
            logger.info("步骤 4/4: 文本后处理...")
            time.sleep(0.5)  # 模拟文本处理
            
            # 生成示例转录结果
            mock_transcript = f"""
=== Bilibili 视频转录结果 ===
视频ID: {video_id}
处理时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

[00:00:00] 大家好，欢迎观看这个视频
[00:00:05] 这是一个关于技术分享的内容
[00:00:10] 我们将深入探讨相关的技术细节
[00:00:15] 希望对大家有所帮助

--- 转录文本 ---
各位观众朋友们大家好，欢迎来到今天的分享。在这个视频中，我们将为大家带来精彩的内容。
首先让我们来了解一下今天要讨论的主题...

【注意】这是演示版本的转录结果。在实际使用中，此处应该包含真实的视频转录文本。

=== 处理统计 ===
视频时长: 模拟数据
处理用时: 4.5秒（实际会更长）
识别准确率: 模拟数据

=== 技术实现建议 ===
1. 使用 yt-dlp 下载 Bilibili 视频
2. 使用 ffmpeg 提取高质量音频
3. 集成 OpenAI Whisper 或讯飞语音 API
4. 实现文本后处理和格式化
5. 添加时间戳和字幕功能

更多信息请查看项目文档。
            """.strip()
            
            logger.info("视频处理完成！")
            return mock_transcript
            
        except Exception as e:
            error_msg = f"处理视频时发生错误: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)
            
        # 实际实现示例代码（注释掉）：
        """
        实际使用时的参考代码：
        
        import yt_dlp
        import whisper
        import subprocess
        
        # 1. 下载视频
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': f'downloads/{video_id}.%(ext)s',
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])
        
        # 2. 转换为音频
        audio_file = f'downloads/{video_id}.wav'
        subprocess.run([
            'ffmpeg', '-i', f'downloads/{video_id}.webm', 
            '-ar', '16000', '-ac', '1', audio_file
        ])
        
        # 3. 语音识别
        model = whisper.load_model("base")
        result = model.transcribe(audio_file)
        
        # 4. 返回转录文本
        return result["text"]
        """
        
    def print_stats(self):
        """打印统计信息"""
        runtime = datetime.now() - self.stats['start_time']
        print(f"\n{'='*50}")
        print(f"📊 工作器统计信息")
        print(f"{'='*50}")
        print(f"运行时间: {runtime}")
        print(f"总处理任务: {self.stats['total_processed']}")
        print(f"成功处理: {self.stats['successful']}")
        print(f"处理失败: {self.stats['failed']}")
        if self.stats['total_processed'] > 0:
            success_rate = (self.stats['successful'] / self.stats['total_processed']) * 100
            print(f"成功率: {success_rate:.1f}%")
        print(f"{'='*50}\n")
        
    def run(self):
        """运行工作器主循环"""
        print(f"🚀 启动 Bilibili 转录工作器")
        print(f"🌐 API URL: {self.api_base_url}")
        print(f"⏱️  轮询间隔: {self.poll_interval}秒")
        print(f"📝 日志文件: worker.log")
        print(f"{'='*60}")
        
        logger.info("工作器启动成功")
        
        consecutive_failures = 0
        max_failures = 5
        
        while True:
            try:
                # 获取待处理任务
                task = self.get_pending_task()
                
                if not task:
                    logger.info("暂无待处理任务，等待中...")
                    time.sleep(self.poll_interval)
                    consecutive_failures = 0  # 重置失败计数
                    continue
                    
                task_id = task['taskId']
                video_url = task['videoUrl']
                video_id = task['videoId']
                
                logger.info(f"📋 获取到新任务: {task_id}")
                logger.info(f"📺 视频ID: {video_id}")
                
                self.stats['total_processed'] += 1
                
                try:
                    # 处理视频
                    result = self.process_video(video_url, video_id)
                    
                    # 更新任务结果
                    if self.update_task(task_id, result=result):
                        logger.info(f"✅ 任务完成: {task_id}")
                        self.stats['successful'] += 1
                        consecutive_failures = 0
                    else:
                        logger.warning(f"⚠️ 任务结果更新失败: {task_id}")
                        self.stats['failed'] += 1
                        
                except Exception as e:
                    error_msg = f"处理视频时出错: {str(e)}"
                    logger.error(f"❌ {error_msg}")
                    
                    # 更新任务错误状态
                    self.update_task(task_id, error=error_msg)
                    self.stats['failed'] += 1
                    
                # 定期打印统计信息
                if self.stats['total_processed'] % 10 == 0:
                    self.print_stats()
                    
            except KeyboardInterrupt:
                logger.info("收到中断信号，正在退出...")
                self.print_stats()
                print("\n👋 工作器已安全退出")
                break
                
            except Exception as e:
                consecutive_failures += 1
                logger.error(f"工作器运行错误: {e}")
                
                if consecutive_failures >= max_failures:
                    logger.critical(f"连续失败 {max_failures} 次，工作器退出")
                    break
                    
                logger.info(f"等待 {self.poll_interval * 2} 秒后重试...")
                time.sleep(self.poll_interval * 2)


def main():
    """主函数"""
    print("🎬 Bilibili 视频转文字工作器")
    print("=" * 40)
    
    # 从环境变量或命令行参数获取配置
    api_url = os.getenv('API_BASE_URL')
    
    if not api_url and len(sys.argv) > 1:
        api_url = sys.argv[1]
        
    if not api_url:
        print("❌ 请提供 API URL")
        print("\n使用方法:")
        print("1. 命令行参数:")
        print("   python worker.py https://your-app.vercel.app")
        print("2. 环境变量:")
        print("   export API_BASE_URL=https://your-app.vercel.app")
        print("   python worker.py")
        print("\n示例:")
        print("   python worker.py https://bilibili-transcript.vercel.app")
        sys.exit(1)
        
    # 轮询间隔
    poll_interval = int(os.getenv('POLL_INTERVAL', '5'))
    
    # 验证 URL 格式
    if not api_url.startswith(('http://', 'https://')):
        print("❌ 无效的 URL 格式，请使用 http:// 或 https:// 开头")
        sys.exit(1)
    
    print(f"✅ API URL: {api_url}")
    print(f"✅ 轮询间隔: {poll_interval}秒")
    print()
    
    # 创建并运行工作器
    try:
        worker = BilibiliTranscriptWorker(api_url, poll_interval)
        worker.run()
    except Exception as e:
        logger.critical(f"工作器启动失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()