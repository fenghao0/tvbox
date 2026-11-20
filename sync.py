# -*- coding: utf-8 -*-
"""
拉取上游 zknjjjx/tvbox 的最新内容，镜像到本仓库。
由 .github/workflows/sync.yml 每天 05:30（北京时间）调用，
以上游 collect.yml 的 cron（UTC 19:30）为基准顺延 2 小时。
"""
import io
import os
import shutil
import sys
import urllib.request
import zipfile

UPSTREAM = "zknjjjx/tvbox"
BRANCH = "main"
ZIP_URL = f"https://codeload.github.com/{UPSTREAM}/zip/refs/heads/{BRANCH}"

# 需要镜像的文件/目录（相对仓库根）
MIRROR_FILES = ["cmstv.json", "tvbox.json", "niuniu.json", "multi.json"]
MIRROR_DIRS = ["upstream", "assets"]
# 上游 README 改名保存，避免覆盖本仓库自己的说明
README_SRC = "README.md"
README_DST = "README-upstream.md"
# 不镜像 .github（避免运行上游自己的采集工作流）和 .gitignore


def download_zip() -> zipfile.ZipFile:
    req = urllib.request.Request(ZIP_URL, headers={"User-Agent": "tvbox-mirror"})
    data = urllib.request.urlopen(req, timeout=60).read()
    print(f"下载上游压缩包 {len(data)} 字节")
    return zipfile.ZipFile(io.BytesIO(data))


def main() -> int:
    zf = download_zip()
    root = zf.namelist()[0].split("/")[0]          # e.g. tvbox-main
    tmp = "_upstream_tmp"
    shutil.rmtree(tmp, ignore_errors=True)
    zf.extractall(tmp)
    base = os.path.join(tmp, root)

    copied = []
    for name in MIRROR_FILES:
        src = os.path.join(base, name)
        if os.path.exists(src):
            shutil.copy2(src, name)
            copied.append(name)
        else:
            print(f"警告：上游缺少 {name}")

    for d in MIRROR_DIRS:
        src = os.path.join(base, d)
        if os.path.isdir(src):
            shutil.rmtree(d, ignore_errors=True)
            shutil.copytree(src, d)
            copied.append(d + "/")

    rsrc = os.path.join(base, README_SRC)
    if os.path.exists(rsrc):
        shutil.copy2(rsrc, README_DST)
        copied.append(README_DST)

    shutil.rmtree(tmp, ignore_errors=True)
    print("已镜像: " + ", ".join(copied))
    return 0


if __name__ == "__main__":
    sys.exit(main())
