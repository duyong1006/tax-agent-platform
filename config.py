import os

from openai import OpenAI


def create_client():
    # 从 IDEA 运行配置读取密钥。
    api_key = os.getenv("DEEPSEEK_API_KEY", "").strip()

    # 从环境变量读取模型名；未配置时使用当前计划中的默认模型。
    model = os.getenv("DEEPSEEK_MODEL", "deepseek-flash").strip()

    if not api_key:
        raise RuntimeError("缺少 DEEPSEEK_API_KEY，请检查 IDEA 运行配置")

    if not model:
        raise RuntimeError("缺少 DEEPSEEK_MODEL，请检查 IDEA 运行配置")

    client = OpenAI(
        api_key=api_key,
        base_url="https://api.deepseek.com",
        timeout=60.0,
        # 最多额外重试一次。SDK 的重试次数可以通过 max_retries 设置。
        max_retries=1,
    )

    return client, model