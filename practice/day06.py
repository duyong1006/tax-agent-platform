from datetime import date
from decimal import Decimal
import os

from openai import OpenAI
from pydantic import BaseModel, ConfigDict, Field, ValidationError

#Day 6：流式输出、超时和有限重试
import os
import time

from openai import (
    APIConnectionError,
    APIStatusError,
    APITimeoutError,
    OpenAI,
)

class SimulatedTimeoutError(Exception):
    """只用于课堂演示，不会真实调用 API。"""

api_key = os.getenv("DEEPSEEK_API_KEY", "").strip()
model = os.getenv("DEEPSEEK_MODEL", "").strip()

if not api_key:
    raise RuntimeError("没有读取到 DEEPSEEK_API_KEY，请检查 IDEA 运行配置")

if not model:
    raise RuntimeError("没有读取到 DEEPSEEK_MODEL，请检查 IDEA 运行配置")

client = OpenAI(
    api_key=api_key,
    base_url="https://api.deepseek.com",timeout=60.0,
    # 关闭 SDK 自动重试，由本例控制重试次数。
    max_retries=0,)

MAX_ATTEMPTS = 1

SIMULATE_TIMEOUT=False


for attempt in range(1,MAX_ATTEMPTS+1):
    stream=None
    try:
        if SIMULATE_TIMEOUT:
            raise SimulatedTimeoutError("课堂模拟：请求超时")


        stream = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": "你是财税系统学习助手。面向业务人员解释，避免技术术语。",
                },
                {
                    "role": "user",
                    "content": "请用三点说明，申报失败后业务人员可以先核对哪些信息。",
                },
            ],
            stream=True,
            stream_options={"include_usage":True},
            max_tokens=200)

        print("助手：",end="",flush=True)

        for chunk in stream:
            if chunk.choices:
                choice =chunk.choices[0]
                content = choice.delta.content
                if content:
                    print(content,end="",flush=True)
                if choice.finish_reason:
                    print(f"\n结束原因：{choice.finish_reason}")
            # include_usage 开启后，通常在最后的片段看到用量。
            if chunk.usage:
                print(
                    "\n本次用量："
                    f"输入 {chunk.usage.prompt_tokens} Token，"
                    f"输出 {chunk.usage.completion_tokens} Token，"
                    f"合计 {chunk.usage.total_tokens} Token"
                )

        print("\n流式回答完成。")
        break
    except SimulatedTimeoutError as error:
        print("模拟超时")

    except APITimeoutError as error:
        print("请求超时")

    except APIConnectionError as error:
        print("网络连接失败")

    except APIStatusError as error:
        print("HTTP 状态异常")

    except Exception as error:
        # 流读取过程中也可能出现其他传输层错误。
        print(f"流式读取失败：{type(error).__name__}: {error}")
        print("本例不对未知错误自动重试。")
        break

    finally:
        if stream is not None:
            stream.close()

client.close()

























