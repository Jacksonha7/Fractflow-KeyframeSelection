"""
TStar关键帧搜索Agent - 统一接口

本模块提供关键帧搜索与VQA的统一接口，支持多种运行模式。
"""

import os
import sys
import json
from FractFlow.agent import Agent
from FractFlow.core.tool_executor import ToolExecutor

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '../../../'))
sys.path.append(project_root)

from FractFlow.tool_template import ToolTemplate

class TStarKeyframeAgent(ToolTemplate):
    """TStar关键帧搜索Agent，基于ToolTemplate，重写推理流程"""
    SYSTEM_PROMPT = """
你是一个视频智能分析助手。用户会给你一个视频路径和一个问题（可选多选项），你需要调用TStar搜帧与VQA流程，返回答案。

# 核心能力
- 输入视频路径和问题，自动完成关键帧检索与VQA
- 输出答案、关键帧时间戳、目标物体

# 输出格式要求
你的回复应该包含：
- answer: 问题的最终答案
- frame_timestamps: 选中的关键帧时间戳列表
- grounding_objects: 搜索到的目标和线索物体
    """

    TOOLS = [
        ("tools/core/KeyframeSearch/tstar_keyframe_mcp.py", "tstar_keyframe_search")
    ]

    MCP_SERVER_NAME = "tstar_keyframe_agent"

    TOOL_DESCRIPTION = """
    输入视频路径和问题，自动完成关键帧检索与VQA，返回答案、关键帧时间戳、目标物体。
    参数:
    - video_path: str，视频文件路径
    - question: str，用户问题
    - options: str，可选，多选题选项
    返回:
    - answer: str，问题答案
    - frame_timestamps: list，关键帧时间戳
    - grounding_objects: dict，目标和线索物体
    """

    @classmethod
    def create_config(cls):
        from FractFlow.infra.config import ConfigManager
        return ConfigManager(
            provider='deepseek',
            deepseek_model='deepseek-chat',
            max_iterations=10,
            custom_system_prompt=cls.SYSTEM_PROMPT,
            tool_calling_version='turbo'
        )

#     @classmethod
#     async def process_query_with_frames(cls, video_path, question, options=""):
#         """
#         先调用tstar_keyframe_search工具获取帧图片路径、时间戳、目标物体，再用deepseek处理帧图片和问题
#         """
#         tool_executor = ToolExecutor()
#         tstar_result_str = await tool_executor.execute_tool(
#             "tstar_keyframe_search",
#             {"video_path": video_path, "question": question, "options": options}
#         )
#         tstar_result = json.loads(tstar_result_str)
#         frame_paths = tstar_result.get("frame_paths", [])
#         frame_timestamps = tstar_result.get("frame_timestamps", [])
#         grounding_objects = tstar_result.get("grounding_objects", {})

#         # 读取帧图片并拼接prompt
#         import base64
#         images_b64 = []
#         for path in frame_paths:
#             try:
#                 with open(path, "rb") as f:
#                     img_b64 = base64.b64encode(f.read()).decode("utf-8")
#                 images_b64.append(img_b64)
#             except Exception as e:
#                 images_b64.append("")
#         prompt = f"""
# 你是一个视频问答专家。请根据下列视频帧和问题，给出精准简洁的中文答案。

# 问题：{question}

# 帧图片（base64编码，顺序与时间戳对应）：
# """
#         for idx, (b64, ts) in enumerate(zip(images_b64, frame_timestamps)):
#             prompt += f"\n第{idx+1}帧（时间戳{ts:.2f}s）：data:image/jpeg;base64,{b64}"
#         prompt += "\n请直接输出答案，不要输出图片内容。"

#         # 用deepseek大模型推理
#         config = cls.create_config()
#         agent = Agent(config=config, name="deepseek_videoqa_agent")
#         await agent.initialize()
#         try:
#             answer = await agent.process_query(prompt)
#         finally:
#             await agent.shutdown()

#         return json.dumps({
#             "answer": answer,
#             "frame_timestamps": frame_timestamps,
#             "grounding_objects": grounding_objects
#         }, ensure_ascii=False)

#     @classmethod
#     async def _run_interactive(cls):
#         print(f"\n{cls.__name__} Interactive Mode")
#         print("Type 'exit', 'quit', or 'bye' to end the conversation.\n")
#         while True:
#             user_input = input("请输入：视频路径|||问题（可选|||选项）：\n")
#             if user_input.lower() in ('exit', 'quit', 'bye'):
#                 break
#             user_input = user_input.replace('｜', '|')
#             parts = user_input.split('|||')
#             video_path = parts[0].strip() if len(parts) > 0 else ""
#             question = parts[1].strip() if len(parts) > 1 else ""
#             options = parts[2].strip() if len(parts) > 2 else ""
#             print("\nProcessing...\n")
#             result = await cls.process_query_with_frames(video_path, question, options)
#             print(f"Agent: {result}")
#         print("\nAgent session ended.")

#     @classmethod
#     async def _run_single_query(cls, query: str):
#         print(f"Processing query: {query}")
#         print("\nProcessing...\n")
#         query = query.replace('｜', '|')
#         parts = query.split('|||')
#         video_path = parts[0].strip() if len(parts) > 0 else ""
#         question = parts[1].strip() if len(parts) > 1 else ""
#         options = parts[2].strip() if len(parts) > 2 else ""
#         result = await cls.process_query_with_frames(video_path, question, options)
#         print(f"Result: {result}")
#         return result

#     @classmethod
#     async def _mcp_tool_function(cls, query: str) -> str:
#         query = query.replace('｜', '|')
#         parts = query.split('|||')
#         video_path = parts[0].strip() if len(parts) > 0 else ""
#         question = parts[1].strip() if len(parts) > 1 else ""
#         options = parts[2].strip() if len(parts) > 2 else ""
#         return await cls.process_query_with_frames(video_path, question, options)

if __name__ == "__main__":
    TStarKeyframeAgent.main() 