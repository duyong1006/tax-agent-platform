from prompts import SYSTEM_PROMPT_BUSINESS


def ask_stream(client, model, history, question):
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT_BUSINESS},
        *history,
        {"role": "user", "content": question},
    ]

    stream = client.chat.completions.create(
        model=model,
        messages=messages,
        stream=True,
        stream_options={"include_usage": True},
        max_tokens=300,
    )

    answer_parts = []
    usage = None

    print("助手：", end="", flush=True)

    try:
        for chunk in stream:
            # 流的最后一个用量片段可能没有 choices。
            if chunk.choices:
                content = chunk.choices[0].delta.content

                if content:
                    print(content, end="", flush=True)
                    answer_parts.append(content)

            if chunk.usage:
                usage = chunk.usage

        print()
    finally:
        stream.close()

    return "".join(answer_parts), usage