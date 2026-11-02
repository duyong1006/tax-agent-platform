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

MAX_ATTEMPTS = 2


for attempt in range(1,MAX_ATTEMPTS+1):
    stream=None
    try:
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




    except Exception as error:
        # 流读取过程中也可能出现其他传输层错误。
        print(f"流式读取失败：{type(error).__name__}: {error}")
        print("本例不对未知错误自动重试。")
        break

    finally:
        if stream is not None:
            stream.close()
client.close()

























