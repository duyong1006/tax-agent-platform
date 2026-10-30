import os

from openai import OpenAI


def main():
    # 从环境变量读取密钥，不把密钥写进源码
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        raise SystemExit("请先设置 DEEPSEEK_API_KEY")

    # 可以通过环境变量更换模型
    model = os.getenv("DEEPSEEK_MODEL", "deepseek-flash")

    # 使用OpenAI客户端库，实际连接DeepSeek服务
    with OpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com",
            timeout=60.0,
            max_retries=0,
    ) as client:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": (
                        "你是财税系统学习助手。"
                        "面向Java后端开发者，用中文解释。"
                        "仅讨论软件业务流程，不编造企业真实数据。"
                    ),
                },
                {
                    "role": "user",
                    "content": "财税 Agent 能帮助 TMS 用户完成哪三类工作？",
                },
            ],
            # 今天先使用普通文本生成，关闭思考模式
            extra_body={"thinking": {"type": "disabled"}},
        )

    print("模型：", model)
    print("回答：", response.choices[0].message.content)
    print("响应ID：", response.id)


if __name__ == "__main__":
    main()