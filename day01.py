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
                    "role": "system",
                    "content": (
                        "你是财税业务助手。面向财务或办税人员解释问题，"
                        "使用日常业务语言，避免程序、接口、数据库等技术术语。"
                        "先说明区别，再给出处理方向；不编造企业真实数据。"
                    ),
                },
                {
                    "role": "user",
                    "content": "请用三句话解释申报失败和缴款失败的流程区别。",
                },
                {
                    "role": "user",
                    "content": "请用一句话解释申报流程。",
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