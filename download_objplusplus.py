from utils import *

# ========= 配置区 =========
ANNOTATED_JSON = "annotated_800k.json"   # 你的文件
SAVE_DIR = "./objaversepp_obj"
MAX_DOWNLOAD = 2        # 先下 10 个试试
MIN_SCORE = 2            # 只要高质量（1~3）
# ==========================

if os.path.exists(SAVE_DIR):
    shutil.rmtree(SAVE_DIR)
    print(f"Removed existing directory: {SAVE_DIR}")
os.makedirs(SAVE_DIR)

# -------- Step 1：读取 UID（来自 Objaverse++） --------
print("读取 Objaverse++ 标注文件...")
objpp_annotation_raw = load_json(ANNOTATED_JSON)

uids = []
objpp_annotation = dict()
for item in objpp_annotation_raw:
    if item["score"] >= MIN_SCORE and item["is_scene"] == "false": # high score and not a scene
        uid = item["UID"]
        if uid:
            uids.append(uid)
            objpp_annotation[uid] = item
print(f"符合条件的 UID 数量: {len(uids)}")

# -------- Step 2：扫描原始 Objaverse，匹配 UID --------
for i in range(len(uids)):
    if(i >= MAX_DOWNLOAD):
        break
    uid = uids[i]

    # Download mesh
    print("Downloading:", uid)
    obj = objaverse.load_objects([uid])
    
    # Get default dirs
    obj_original_fname = obj[uid]
    default_save_folder = os.path.join("/", *(obj_original_fname.split("/")[:-1]))
    default_parent_folder = os.path.join("/", *(obj_original_fname.split("/")[:-2]))
    
    # Save annotation
    annotation = objaverse.load_annotations([uid])
    annotation_fname = os.path.join(default_save_folder, "annotation.json")
    obj_annotation_objpp = objpp_annotation[uid]
    for key in obj_annotation_objpp.keys(): # fill in additional annotations
        if(key not in annotation):
            annotation[key] = obj_annotation_objpp[key]
    write_json(annotation, annotation_fname)
    

# Move downloaded files to the specified dir
file_names = os.listdir(default_parent_folder)
for file_name in file_names:
    try:
        shutil.move(os.path.join(default_parent_folder, file_name), SAVE_DIR)
    except:
        shutil.rmtree(os.path.join(default_parent_folder, file_name))

print(f"完成！成功下载 {i} 个 GLB，保存在 {SAVE_DIR}/")
