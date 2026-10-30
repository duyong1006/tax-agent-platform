# 今天在 Day 1 的调用代码上加一层“调用记录”：每次请求后记录输入和输出用了多少 Token、耗时多久，以及是否成功。这些信息能帮你监控财税智能 Agent 的调用情况和费用。
import csv
from datetime import datetime
import os
import time
from pathlib import Path

from openai import APIConnectionError, APIStatusError, OpenAI

api_key = os.getenv("DEEPSEEK_API_KEY").strip()
model = os.getenv("DEEPSEEK_MODEL").strip()
if not api_key:
    raise SystemExit("没有读取到 DEEPSEEK_API_KEY，请检查 IDEA 运行配置中的环境变量")
if not model:
    raise SystemExit("没有读取到 DEEPSEEK_MODEL，请检查 IDEA 运行配置中的环境变量")

client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")

# print(Path(__file__)).
csv_path = Path(__file__).with_name("day03_usage.csv")

tests = [
    ("短输入", "请用三点总结：小企业需要按时整理收入、成本和发票。"),
    ("中输入", "请用三点总结以下模拟业务资料，不要给出确定的税务结论。\n" +
     "某小企业本月整理了销售收入、采购成本、员工报销和发票信息。" * 8),
    ("长输入", "请用三点总结以下模拟业务资料，不要给出确定的税务结论。\n" +
     "某小企业本月整理了销售收入、采购成本、员工报销和发票信息。" * 40),
]

file_exists = csv_path.exists() and csv_path.stat().st_size > 0

with csv_path.open("a", newline="", encoding="utf-8-sig") as file:
    writer = csv.writer(file)
    if not file_exists:
        writer.writerow([
            "time", "label", "model", "request_id",
            "input_chars", "prompt_tokens", "completion_tokens",
            "total_tokens", "elapsed_ms", "finish_reason"
        ])
    try:
        for label, prompt in tests:
            # print(label, prompt)
            started = time.perf_counter()
            response = client.chat.completions.create(model=model, messages=[{
                "role": "system",
                "content": "面向业务人员解释，避免技术术语。"
            },
                {
                    "role": "user",
                    "content": prompt
                }], max_tokens=150)
            elapsed_ms = round((time.perf_counter() - started) * 1000, 2)
            usage = response.usage
            prompt_tokens = usage.prompt_tokens
            completion_tokens = usage.completion_tokens
            total_tokens = usage.total_tokens
            finish_reason = response.choices[0].finish_reason
            print(f"\n【{label}】")
            print("模型回答：", response.choices[0].message.content)
            print(f"输入字符数：{len(prompt)}")
            print(f"输入 Token：{prompt_tokens}")
            print(f"输出 Token：{completion_tokens}")
            print(f"总 Token：{total_tokens}")
            print(f"耗时：{elapsed_ms} ms")
            print(f"结束原因：{finish_reason}")
            writer.writerow([
                datetime.now().isoformat(timespec="seconds"),
                label,
                response.model,
                response.id,
                len(prompt),
                prompt_tokens,
                completion_tokens,
                total_tokens,
                elapsed_ms,
                finish_reason,
            ])
    except APIStatusError as error:
        print(f"\n【{label}】接口返回 HTTP {error.status_code}")
        if error.status_code == 402:
            print("检查 DeepSeek 账户余额。")
        elif error.status_code == 429:
            print("请求可能过于频繁，请稍后再试。")
        elif error.status_code == 401:
            print("检查 API Key 是否有效。")
        else:
            print("查看错误信息和 DeepSeek 错误码文档。")
    except APIConnectionError as error:
        print(f"\n【{label}】网络连接失败：{error}")
        print("检查网络、代理和 API 地址。")
print(f"\n调用记录已保存到：{csv_path}")
