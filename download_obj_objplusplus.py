import json
import os
import requests
from datasets import load_dataset
from urllib.parse import urlparse

# ========= 配置区 =========
ANNOTATED_JSON = "annotated_800k.json"   # 你的文件
SAVE_DIR = "objaversepp_obj"
MAX_DOWNLOAD = 2        # 先下 10 个试试
MIN_SCORE = 3            # 只要高质量（1~3）
# ==========================

os.makedirs(SAVE_DIR, exist_ok=True)

def is_obj(url):
    return isinstance(url, str) and url.lower().endswith(".obj")

def download(url):
    name = os.path.basename(urlparse(url).path)
    path = os.path.join(SAVE_DIR, name)

    if os.path.exists(path):
        print("已存在，跳过:", name)
        return

    print("下载:", url)
    r = requests.get(url, stream=True, timeout=60)
    r.raise_for_status()

    with open(path, "wb") as f:
        for chunk in r.iter_content(chunk_size=1024 * 1024):
            if chunk:
                f.write(chunk)

    print("完成:", name)

# -------- Step 1：读取 UID（来自 Objaverse++） --------
print("读取 Objaverse++ 标注文件...")
with open(ANNOTATED_JSON, "r", encoding="utf-8") as f:
    annotated = json.load(f)

uids = []
for item in annotated:
    if item.get("score", 0) >= MIN_SCORE:
        uid = item.get("UID")
        if uid:
            uids.append(uid)

uids = set(uids)
print(f"符合条件的 UID 数量: {len(uids)}")

# -------- Step 2：扫描原始 Objaverse，匹配 UID --------
print("开始流式扫描原始 Objaverse（这一步是关键）...")
dataset = load_dataset("allenai/objaverse", split="train", streaming=True)

downloaded = 0

for sample in dataset:
    # 原始 Objaverse 里的 UID 字段
    sample_uid = sample.get("uid") or sample.get("id")
    if sample_uid not in uids:
        continue

    uri = sample.get("uri") or sample.get("file_path") or sample.get("url")
    if not is_obj(uri):
        continue

    download(uri)
    downloaded += 1

    if downloaded >= MAX_DOWNLOAD:
        break

print(f"完成！成功下载 {downloaded} 个 OBJ，保存在 {SAVE_DIR}/")
