from openai import APIConnectionError, APIStatusError, APITimeoutError

from config import create_client
from llm_client import ask_stream


MAX_HISTORY_MESSAGES = 8


def main():
    client, model = create_client()
    history = []

    print(f"财税问答助手已启动，当前模型：{model}")
    print("输入 /clear 清空对话，输入 /exit 退出。")

    try:
        while True:
            question = input("\n你：").strip()

            if not question:
                continue

            if question == "/exit":
                print("对话结束。")
                break

            if question == "/clear":
                history.clear()
                print("对话历史已清空。")
                continue

            try:
                answer, usage = ask_stream(
                    client=client,
                    model=model,
                    history=history,
                    question=question,
                )
            except APITimeoutError:
                print("请求超时，请稍后再试。")
                continue
            except APIConnectionError:
                print("连接失败，请检查网络、代理和 API 地址。")
                continue
            except APIStatusError as error:
                print(f"接口返回 HTTP {error.status_code}，请检查错误码。")
                continue
            except Exception as error:
                # 不打印完整异常，避免日志里包含不必要的敏感信息。
                print(f"程序出现异常，错误类型：{type(error).__name__}")
                continue

            # 只有调用成功后，才把本轮问答放入历史。
            history.append({"role": "user", "content": question})
            history.append({"role": "assistant", "content": answer})

            # 每轮保留成对的用户消息和助手消息。
            if len(history) > MAX_HISTORY_MESSAGES:
                history = history[-MAX_HISTORY_MESSAGES:]

            if usage:
                print(
                    "本次 Token："
                    f"输入 {usage.prompt_tokens}，"
                    f"输出 {usage.completion_tokens}，"
                    f"合计 {usage.total_tokens}"
                )

    finally:
        client.close()


if __name__ == "__main__":
    main()