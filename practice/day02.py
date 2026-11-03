import os
from openai import OpenAI
from prompts import SYSTEM_PROMPT_DEVELOPER, SYSTEM_PROMPT_BUSINESS


def ask(client, model, system_prompt, question):
    response = client.chat.completions.create(model=model, messages=[{"role": "system", "content": system_prompt},
                                                                     {"role": "user", "content": question}],
                                              extra_body={"thinking": {"type": "disabled"}}, )
    return response.choices[0].message.content


def main():
    # 读取本地环境
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        raise SystemExit("请先在 IDEA 运行配置中设置 DEEPSEEK_API_KEY")
    model = os.getenv("DEEPSEEK_MODEL", "deepseek-flash")

    question = "把问题换成“申报已经成功，但缴款没成功，下一步怎么处理？"

    base_url = "https://api.deepseek.com"
    with OpenAI(api_key=api_key, base_url=base_url, timeout=60.0, max_retries=0,) as client:
        developer_answer = ask(client, model, SYSTEM_PROMPT_DEVELOPER, question)
        business_answer = ask(client, model, SYSTEM_PROMPT_BUSINESS, question)
    print("=== 面向 Java 开发者 ===")
    print(developer_answer)
    print("=== 面向财务或办税人员 ===")
    print(business_answer)


# system   定规则的   user  提问题 assistant记录 AI 的回答。
#system 定义Ai 身份和行为规范  user 负责提出具体的问题和任务的


if __name__ == "__main__":
    main()
