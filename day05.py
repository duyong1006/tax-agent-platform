from datetime import date
from decimal import Decimal
import os

from openai import OpenAI
from pydantic import BaseModel, ConfigDict, Field, ValidationError


# 定义程序允许接收的发票字段和限制
class InvoiceData(BaseModel):
    # 禁止传入模型中未定义的字段 ，多传字段就会报错
    model_config = ConfigDict(extra="forbid")
    invoice_no: str = Field(min_length=1)
    seller_name: str = Field(min_length=1)
    amount: Decimal = Field(gt=0)
    invoice_date: date | None = None

api_key = os.getenv("DEEPSEEK_API_KEY", "").strip()
model = os.getenv("DEEPSEEK_MODEL", "").strip()

if not api_key:
    raise RuntimeError("没有读取到 DEEPSEEK_API_KEY，请检查 IDEA 运行配置")

if not model:
    raise RuntimeError("没有读取到 DEEPSEEK_MODEL，请检查 IDEA 运行配置")

client = OpenAI(
    api_key=api_key,
    base_url="https://api.deepseek.com",
)

fake_invoice_text="""发票号码：FP-2026-001
销售方：北方办公用品有限公司
价税合计：680.50元
开票日期：2026-10-08"""

try:
    messages=[
        {
            "role": "system",
            "content": """
你是发票字段提取助手。
请根据用户提供的模拟发票文字，输出一个 JSON 对象。
必须包含 invoice_no、seller_name、amount、invoice_date 四个字段。
没有日期时，invoice_date 输出 null。
amount 输出数字。
只输出 JSON，不要添加 Markdown 或解释。
没有发票号码时不要猜，返回空值。
例如：
{
  "invoice_no": "FP-001",
  "seller_name": "某公司",
  "amount": 100.50,
  "invoice_date": "2026-10-20"
}
""",
        },
        {
            "role": "user",
            "content": fake_invoice_text,
        },
    ]
    response=client.chat.completions.create(model=model,messages=messages, max_tokens=300,response_format={"type":"json_object"})

    raw_json=response.choices[0].message.content
    if not raw_json.strip():
        raise ValueError("模型返回内容为空，请检查提示词或 finish_reason")
    print("模型原始 JSON：")
    print(raw_json)
    #校验一下数据是否合法
    invoice=InvoiceData.model_validate_json(raw_json)

    print(invoice.model_dump_json(indent=2))

except ValidationError as error:
    print("\n模型返回的数据没有通过字段校验：")
    print(error.errors())

except ValueError as error:
    print(f"\n处理失败：{error}")