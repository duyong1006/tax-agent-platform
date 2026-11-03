import os

from openai import APIConnectionError, APIStatusError, OpenAI


def main():
    # 从环境变量读取密钥，不把密钥写进源码
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        raise SystemExit("请先设置 DEEPSEEK_API_KEY")

    # 可以通过环境变量更换模型
    model = os.getenv("DEEPSEEK_MODEL", "deepseek-flash")

    client = OpenAI(api_key=api_key,base_url="https://api.deepseek.com")

    system_message={  "role": "system",
                      "content": "你是财税系统学习助手。面向业务人员解释，避免技术术语；不编造真实业务数据。",
                      }


    # 只保留最近 4 轮问答，也就是最多 8 条 user/assistant 消息。
    MAX_HISTORY_MESSAGES = 8


    # 对话历史存在本地程序内存中；每次 API 请求都会重新发送。
    conversation_history=[]
    print("财税助手已启动。输入 /clear 清空对话，输入 /exit 退出。")

    while True:
        user_input=input("\n你：").strip()
        if user_input=="/exit":
            print("对话结束")
            break
        if user_input=="/clear":
            print("对话结束")
            conversation_history.clear()
            continue

        user_input= {
            "role": "user",
            "content": user_input
        }
        conversation_history.append(user_input)


        messages=[system_message]+(conversation_history)

        try:
            #print(f"打印参数:{messages}")
            response=client.chat.completions.create(model=model,messages= messages,max_tokens=200)

        except APIStatusError as error:
            conversation_history.pop()
            print(f"接口返回 HTTP {error.status_code}，请检查错误信息和配置。")
            continue
        except APIConnectionError as error:
            conversation_history.pop()
            print(f"网络连接失败：{error}")
            print("请检查网络、代理和 API 地址。")
            continue

        answer = response.choices[0].message.content or ""

        conversation_history.append(
            {
                "role": "assistant",
                "content":  answer,
            }
        )

        print(f"助手回答:{answer}")
        # 裁剪成最近若干条消息。
        if len(conversation_history) > MAX_HISTORY_MESSAGES:
            conversation_history = conversation_history[-MAX_HISTORY_MESSAGES:]


if __name__ == "__main__":
    main()