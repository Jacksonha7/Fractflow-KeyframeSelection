#!/usr/bin/env python3
import os
import sys
import json
import traceback
from mcp.server.fastmcp import FastMCP

# 保证TStar包可导入
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '../../..'))
tstar_dir = os.path.join(current_dir, 'TStar')
if project_root not in sys.path:
    sys.path.insert(0, project_root)
if tstar_dir not in sys.path:
    sys.path.insert(0, tstar_dir)

from TStar.TStarFramework import run_tstar

# 初始化MCP服务
mcp = FastMCP("tstar_keyframe_search_tool")

print("[MCP] tstar_keyframe_mcp.py 启动成功，等待请求...")

@mcp.tool()
async def tstar_keyframe_search(
    video_path: str,
    question: str,
    options: str = ""
) -> str:
    """
    tstar_keyframe_search
    关键帧检索与VQA工具
    参数:
        video_path: 视频文件路径
        question: 用户问题
        options: 可选，多选题选项
    返回:
        JSON字符串，包含frame_timestamps、frame_paths、grounding_objects
    """
    try:
        if not video_path or not question:
            return json.dumps({"error": "参数缺失：video_path和question为必填项。"})
        result = run_tstar(video_path, question, options)
        # 获取帧图片路径
        frame_dir = os.path.join(
            './output',
            os.path.basename(video_path).split('.')[0],
            question[:-1],
            'frames'
        )
        frame_paths = []
        if os.path.exists(frame_dir):
            frame_paths = [os.path.join(frame_dir, f) for f in sorted(os.listdir(frame_dir)) if f.endswith('.jpg')]
        return json.dumps({
            "frame_timestamps": result.get("Frame Timestamps"),
            "frame_paths": frame_paths,
            "grounding_objects": result.get("Grounding Objects")
        }, ensure_ascii=False)
    except Exception as e:
        return json.dumps({
            "error": f"TStar流程执行失败: {str(e)}",
            "traceback": traceback.format_exc()
        }, ensure_ascii=False)

print("[MCP] tstar_keyframe_search 工具已注册")

if __name__ == "__main__":
    mcp.run(transport='stdio') 