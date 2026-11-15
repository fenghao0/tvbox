# -*- coding: utf-8 -*-
"""
把上游 cmstv.json（自定义 cmstv/1 结构，只有 name/api）
转换成影视壳 / TVBox 能直接吃掉的配置，并做一轮验活。

产出：
  config/tvbox-all.json  全部非成人源
  config/tvbox-ok.json   只保留当前能返回 CMS 数据的源
  LINKS.md               可粘贴进壳的地址清单
"""
import concurrent.futures as cf
import json
import os
import re
import sys
import urllib.request
from datetime import datetime, timezone, timedelta

SRC = "cmstv.json"
OUT_DIR = "config"
ALL_OUT = os.path.join(OUT_DIR, "tvbox-all.json")
OK_OUT = os.path.join(OUT_DIR, "tvbox-ok.json")
LINKS_OUT = "LINKS.md"
UA = {"User-Agent": "Mozilla/5.0 (tvbox-mirror)"}

SLUG = os.environ.get("GITHUB_REPOSITORY", "fenghao0/tvbox")
BRANCH = "main"
FLAGS = ["youku", "qq", "iqiyi", "qiyi", "letv", "sohu", "tudou", "pptv", "mgtv", "wasu", "bilibili"]


def load_sites():
    data = json.load(open(SRC, encoding="utf-8"))
    raw = data["sites"]
    out, seen = [], set()
    for i, s in enumerate(raw, 1):
        if s.get("adult") is True:
            continue
        api = (s.get("api") or "").strip()
        if not api or api in seen:
            continue
        seen.add(api)
        out.append({
            "key": "c%03d" % (len(out) + 1),
            "name": s.get("name") or api,
            "type": 1,
            "api": api,
            "searchable": 1,
            "quickSearch": 1,
            "filterable": 1,
            "ext": "",
            "group": "采集源",
        })
    return data.get("updated", ""), len(raw), out


def probe(site):
    url = site["api"] + "?ac=list"
    try:
        r = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=10)
        body = r.read(400).decode("utf-8", "ignore").strip()
        if body.startswith("{") and ('"list"' in body or '"class"' in body):
            return site, "JSON"
        if body.startswith("<?xml") and "<list" in body:
            return site, "XML"
        return site, "HTML"
    except Exception:
        return site, "DEAD"


def build(sites, name):
    return {
        "name": name,
        "spider": "",
        "wallpaper": "",
        "sites": sites,
        "lives": [],
        "parses": [],
        "flags": FLAGS,
    }


def main() -> int:
    os.makedirs(OUT_DIR, exist_ok=True)
    updated, total, sites = load_sites()
    print(f"上游更新时间: {updated}  原始 {total} 条  非成人去重后 {len(sites)} 条")

    with open(ALL_OUT, "w", encoding="utf-8", newline="\n") as f:
        json.dump(build(sites, "CineNest 全量非成人版"), f, ensure_ascii=False, indent=2)

    with cf.ThreadPoolExecutor(24) as ex:
        results = list(ex.map(probe, sites))
    ok_sites = [s for s, k in results if k in ("JSON", "XML")]
    dead = [s["name"] for s, k in results if k not in ("JSON", "XML")]
    print(f"验活: {len(ok_sites)}/{len(sites)} 可用，{len(dead)} 不可用")

    with open(OK_OUT, "w", encoding="utf-8", newline="\n") as f:
        json.dump(build(ok_sites, "CineNest 验活版"), f, ensure_ascii=False, indent=2)

    now = datetime.now(timezone.utc).astimezone(timezone(timedelta(hours=8)))
    base = f"https://cdn.jsdelivr.net/gh/{SLUG}@{BRANCH}"
    raw = f"https://raw.githubusercontent.com/{SLUG}/{BRANCH}"

    lines = [
        "# 可用接口地址（自动生成，勿手改）",
        "",
        f"生成时间：{now:%Y-%m-%d %H:%M} (UTC+8)　上游数据更新：{updated or '未知'}",
        "",
        f"源数量：合计 {len(sites)} 个，其中当前可用 {len(ok_sites)} 个。",
        "",
        "## 直接填进影视壳 / TVBox 的配置地址",
        "",
        "推荐（只含当前可用源）：",
        "",
        "```",
        f"{base}/config/tvbox-ok.json",
        "```",
        "",
        "全量（含暂时不通的源，壳里会看到空白条目）：",
        "",
        "```",
        f"{base}/config/tvbox-all.json",
        "```",
        "",
        "上游原始配置（已经是 TVBox 结构，可直接用）：",
        "",
        "```",
        f"{base}/tvbox.json",
        f"{base}/multi.json",
        "```",
        "",
        "备用直链（jsdelivr 抽风时可用，走 GitHub 源站，无 CDN 缓存）：",
        "",
        "```",
        f"{raw}/config/tvbox-ok.json",
        "```",
        "",
        "## 更新说明",
        "",
        "- 本仓库每天北京时间 **08:00** 自动从上游 `zknjjjx/tvbox` 拉取最新 `cmstv.json` 并重建以上配置",
        "- jsdelivr 有缓存，改动后最迟数小时生效；急用可在地址后加 `?t=时间戳`",
        "- 可用性判定标准：`接口地址?ac=list` 能返回 CMS JSON/XML。返回 HTML（被拦截）或连接失败记为不可用",
        "",
    ]
    if dead:
        lines += ["## 本轮不可用的源", "", "| 源 | 结果 |", "|---|---|"]
        for s, k in results:
            if k not in ("JSON", "XML"):
                lines.append(f"| {s['name']} | {k} |")
        lines.append("")

    with open(LINKS_OUT, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines))
    print(f"写出 {ALL_OUT} / {OK_OUT} / {LINKS_OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
