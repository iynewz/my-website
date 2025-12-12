import requests
import json
import os
from dotenv import load_dotenv
load_dotenv()

APP_ID = os.environ["FEISHU_APP_ID"]
APP_SECRET = os.environ["FEISHU_APP_SECRET"]
APP_TOKEN = os.environ["FEISHU_APP_TOKEN"]
TABLE_ID = os.environ["FEISHU_TABLE_ID"]

# 获取 tenant_access_token
resp = requests.post(
    "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
    json={"app_id": APP_ID, "app_secret": APP_SECRET},
)
token_resp = resp.json()
print(token_resp)  # ✅ debug 输出
token = token_resp.get("tenant_access_token")
if not token:
    raise ValueError("获取 token 失败，请检查 APP_ID 和 APP_SECRET")

headers = {"Authorization": f"Bearer {token}"}

# 获取表格数据
url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}/tables/{TABLE_ID}/records"
resp = requests.get(url, headers=headers)
data = resp.json()
print(json.dumps(data, ensure_ascii=False, indent=2))  # ✅ debug 输出

if data.get("code") != 0:
    raise ValueError(f"请求失败: {data.get('msg')}")

items = data["data"]["items"]

def get_text_field(field):
    """处理 table 的 field，可以是 str 或 list[{"text": ...}]"""
    if not field:
        return ""
    if isinstance(field, str):
        return field
    if isinstance(field, list) and len(field) > 0:
        return field[0].get("text", "")
    return ""

# 处理 quotes
quotes = []

for item in items:
    fields = item.get("fields", {})

    # quote 是必需的
    quote_text = get_text_field(fields.get("quote"))
    if not quote_text:
        continue

    # optional fields
    source_field = fields.get("source")
    source_text = get_text_field(source_field.get("text")) if source_field else ""

    author_field = fields.get("author")
    author_text = get_text_field(author_field) if author_field else ""

    quotes.append({
        "quote": quote_text,
        "source": source_text,
        "author": author_text
    })


with open("docs/quotes.json", "w", encoding="utf-8") as f:
    json.dump(quotes, f, ensure_ascii=False, indent=2)

print("quotes.json generated")