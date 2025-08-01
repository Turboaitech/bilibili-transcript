#!/usr/bin/env python3
"""
Bilibili 视频转文字 Worker
定期从 Vercel API 获取任务，处理后保存到 iCloud Drive
"""

import os
import re
import time
import json
import subprocess
import requests
from datetime import datetime
from pathlib import Path
import socket
import tempfile
import shutil

# 配置
API_BASE = "https://bilibili-transcript.vercel.app/api"
WORKER_ID = socket.gethostname()  # 使用机器名作为 Worker ID
CHECK_INTERVAL = 30  # 检查间隔（秒）

# iCloud Drive 路径
ICLOUD_BASE = Path.home() / "Library/Mobile Documents/com~apple~CloudDocs/bilibili transcripts"

# Whisper 配置
WHISPER_MODEL = "base"  # 可选: tiny, base, small, medium, large-v3
WHISPER_LANGUAGE = "zh"  # 中文

def setup_directories():
    """创建必要的目录结构"""
    ICLOUD_BASE.mkdir(parents=True, exist_ok=True)
    (ICLOUD_BASE / "_processing").mkdir(exist_ok=True)
    (ICLOUD_BASE / "_failed").mkdir(exist_ok=True)
    print(f"✅ iCloud 目录已准备: {ICLOUD_BASE}")

def clean_filename(title):
    """清理文件名，移除特殊字符"""
    # 移除不安全的字符
    safe_title = re.sub(r'[^\w\s\u4e00-\u9fff-]', '', title)
    # 压缩空格
    safe_title = re.sub(r'\s+', ' ', safe_title).strip()
    # 限制长度
    return safe_title[:100]

def get_video_info(url):
    """获取视频标题"""
    try:
        result = subprocess.run(
            ["yt-dlp", "--get-title", url],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except:
        return "untitled"

def download_and_transcribe(url, task_id):
    """下载视频并转换为文字"""
    temp_dir = tempfile.mkdtemp()
    
    try:
        print(f"📥 获取视频信息...")
        title = get_video_info(url)
        safe_title = clean_filename(title)
        
        # 文件名
        timestamp = datetime.now().strftime("%H-%M-%S")
        base_name = f"{timestamp}_{safe_title}_{task_id[:8]}"
        
        mp3_file = os.path.join(temp_dir, f"{base_name}.mp3")
        wav_file = os.path.join(temp_dir, f"{base_name}.wav")
        
        # 下载音频
        print(f"⬇️  下载音频: {title}")
        subprocess.run([
            "yt-dlp",
            "-x",
            "--audio-format", "mp3",
            "-o", mp3_file,
            url
        ], check=True)
        
        # 转换为 WAV
        print("🔄 转换音频格式...")
        subprocess.run([
            "ffmpeg", "-i", mp3_file,
            "-ar", "16000",
            "-ac", "1",
            "-c:a", "pcm_s16le",
            wav_file,
            "-y"
        ], check=True, capture_output=True)
        
        # Whisper 转写
        print(f"🎯 开始转写 (模型: {WHISPER_MODEL})...")
        whisper_cmd = [
            "whisper", wav_file,
            "--model", WHISPER_MODEL,
            "--language", WHISPER_LANGUAGE,
            "--output_format", "txt",
            "--output_dir", temp_dir
        ]
        subprocess.run(whisper_cmd, check=True)
        
        # 找到生成的 txt 文件
        txt_file = wav_file.replace('.wav', '.txt')
        
        # 保存到 iCloud
        date_folder = ICLOUD_BASE / datetime.now().strftime("%Y-%m-%d")
        date_folder.mkdir(exist_ok=True)
        
        final_txt = date_folder / f"{base_name}.txt"
        shutil.copy2(txt_file, final_txt)
        
        # 创建元数据
        metadata = {
            "task_id": task_id,
            "url": url,
            "title": title,
            "timestamp": datetime.now().isoformat(),
            "model": WHISPER_MODEL,
            "worker": WORKER_ID
        }
        
        meta_file = date_folder / f"{base_name}.json"
        with open(meta_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 转写完成: {final_txt}")
        
        # 发送系统通知
        send_notification("转写完成", f"{title} 已保存到 iCloud Drive")
        
        return str(final_txt), None
        
    except Exception as e:
        error_msg = str(e)
        print(f"❌ 处理失败: {error_msg}")
        
        # 保存错误信息
        error_file = ICLOUD_BASE / "_failed" / f"{task_id}_error.txt"
        with open(error_file, 'w') as f:
            f.write(f"URL: {url}\n")
            f.write(f"Error: {error_msg}\n")
            f.write(f"Time: {datetime.now()}\n")
        
        return None, error_msg
        
    finally:
        # 清理临时文件
        shutil.rmtree(temp_dir, ignore_errors=True)

def send_notification(title, message):
    """发送 macOS 系统通知"""
    try:
        subprocess.run([
            'osascript', '-e',
            f'display notification "{message}" with title "{title}" sound name "Glass"'
        ])
    except:
        pass  # 忽略通知错误

def update_task_status(task_id, status, error=None):
    """更新任务状态（这里可以扩展为上报给服务器）"""
    print(f"📝 任务 {task_id} 状态: {status}")
    if error:
        print(f"   错误: {error}")

def main():
    """主循环"""
    print("🚀 Bilibili 转文字 Worker 启动")
    print(f"📍 Worker ID: {WORKER_ID}")
    print(f"🌐 API: {API_BASE}")
    print(f"📁 输出目录: {ICLOUD_BASE}")
    
    setup_directories()
    
    while True:
        try:
            # 获取待处理任务
            print(f"\n🔍 检查新任务... ({datetime.now().strftime('%H:%M:%S')})")
            
            response = requests.get(
                f"{API_BASE}/get-pending-task",
                params={"worker_id": WORKER_ID},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("taskId"):
                    task_id = data["taskId"]
                    url = data["url"]
                    
                    print(f"\n📋 获得新任务: {task_id}")
                    print(f"🔗 URL: {url}")
                    
                    # 处理任务
                    file_path, error = download_and_transcribe(url, task_id)
                    
                    if file_path:
                        update_task_status(task_id, "completed")
                    else:
                        update_task_status(task_id, "failed", error)
                else:
                    print("💤 暂无新任务")
            else:
                print(f"⚠️  API 错误: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"⚠️  网络错误: {e}")
        except KeyboardInterrupt:
            print("\n👋 Worker 停止")
            break
        except Exception as e:
            print(f"❌ 未知错误: {e}")
        
        # 等待下一次检查
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    # 检查依赖
    dependencies = ["yt-dlp", "ffmpeg", "whisper"]
    missing = []
    
    for dep in dependencies:
        if subprocess.run(["which", dep], capture_output=True).returncode != 0:
            missing.append(dep)
    
    if missing:
        print(f"❌ 缺少依赖: {', '.join(missing)}")
        print("\n请安装:")
        print("brew install ffmpeg yt-dlp")
        print("pip install openai-whisper")
        exit(1)
    
    main()
