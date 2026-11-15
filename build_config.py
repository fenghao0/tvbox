# -*- coding: utf-8 -*-
"""
CineNest TVBox 配置构建脚本。
不根据 adult 字段过滤源。全量版保留所有有非空 API 地址的去重源；
验活版仅保留检测到有效 CMS JSON/XML 结构的源。
"""
import concurrent.futures as cf
import http.client
import json
import os
import socket
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone

SRC = "cmstv.json"
OUT_DIR = "config"
ALL_OUT = os.path.join(OUT_DIR, "tvbox-all.json")
OK_OUT = os.path.join(OUT_DIR, "tvbox-ok.json")
LINKS_OUT = "LINKS.md"
SLUG = os.environ.get("GITHUB_REPOSITORY", "fenghao0/tvbox")
BRANCH = "main"
WORKERS = 24
TIMEOUT = 12
RETRIES = 2
RETRY_DELAY = 1
MAX_RESPONSE_BYTES = 8 * 1024 * 1024

UA = {
    "User-Agent": "Mozilla/5.0 (compatible; CineNest-TVBox-Mirror/1.0)",
    "Accept": "application/json, application/xml, text/xml, */*",
    "Connection": "close",
}
FLAGS = [
    "youku", "qq", "iqiyi", "qiyi", "letv", "sohu",
    "tudou", "pptv", "mgtv", "wasu", "bilibili",
]
VALID_STATUSES = ("JSON", "XML")


def normalize_api(api):
    """规范化去重键，不改变最终写入配置的 API 原文。"""
    api = str(api or "").strip()
    if not api:
        return ""
    try:
        p = urllib.parse.urlsplit(api)
        if p.scheme and p.netloc:
            return urllib.parse.urlunsplit((
                p.scheme.lower(), p.netloc.lower(),
                p.path.rstrip("/"), p.query, ""
            ))
    except ValueError:
        pass
    return api.rstrip("/")


def make_probe_url(api):
    """兼容已有查询参数，正确添加 ac=list。"""
    p = urllib.parse.urlsplit(api)
    query = urllib.parse.parse_qsl(p.query, keep_blank_values=True)
    query = [(k, v) for k, v in query if k.lower() != "ac"]
    query.append(("ac", "list"))
    return urllib.parse.urlunsplit((
        p.scheme, p.netloc, p.path,
        urllib.parse.urlencode(query), ""
    ))


def load_sites():
    with open(SRC, "r", encoding="utf-8-sig") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        raise ValueError("上游 cmstv.json 顶层必须是 JSON 对象")

    raw = data.get("sites", [])
    if not isinstance(raw, list):
        raise ValueError("上游 cmstv.json 的 sites 必须是数组")

    sites, seen = [], set()
    skipped_empty = skipped_duplicate = 0

    for item in raw:
        if not isinstance(item, dict):
            continue
        # 不判断 adult 字段，所有源统一处理。
        api = str(item.get("api") or "").strip()
        if not api:
            skipped_empty += 1
            continue

        normalized = normalize_api(api)
        if normalized in seen:
            skipped_duplicate += 1
            continue
        seen.add(normalized)

        name = str(item.get("name") or api).strip() or api
        sites.append({
            "key": "c%03d" % (len(sites) + 1),
            "name": name,
            "type": 1,
            "api": api,
            "searchable": 1,
            "quickSearch": 1,
            "filterable": 1,
            "ext": "",
            "group": "采集源",
        })

    return (
        str(data.get("updated") or ""), len(raw), sites,
        skipped_empty, skipped_duplicate
    )


def check_response(body):
    """解析响应内容，避免仅凭字符串包含 list/class 就误判。"""
    body = body.lstrip(chr(0xfeff) + " " + chr(13) + chr(10) + chr(9))
    if not body:
        return "EMPTY"

    if body.startswith("{") or body.startswith("["):
        try:
            obj = json.loads(body)
        except (json.JSONDecodeError, ValueError):
            return "INVALID_JSON"
        if isinstance(obj, dict) and ("list" in obj or "class" in obj):
            return "JSON"
        return "INVALID_JSON"

    if body.startswith("<"):
        if body[:256].lower().lstrip().startswith(
            ("<!doctype html", "<html", "<!doctype")
        ):
            return "HTML"
        try:
            root = ET.fromstring(body)
        except ET.ParseError:
            return "INVALID_XML"
        for node in root.iter():
            if isinstance(node.tag, str) and node.tag.split("}")[-1].lower() == "list":
                return "XML"
        return "INVALID_XML"

    return "UNKNOWN"


def probe(site):
    api = site["api"]
    try:
        parts = urllib.parse.urlsplit(api)
        if parts.scheme.lower() not in ("http", "https") or not parts.netloc:
            return site, "INVALID_URL"
        url = make_probe_url(api)
    except (TypeError, ValueError):
        return site, "INVALID_URL"

    for attempt in range(RETRIES + 1):
        try:
            request = urllib.request.Request(url, headers=UA, method="GET")
            with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
                status = getattr(response, "status", 200)
                if status != 200:
                    result = "HTTP_%s" % status
                else:
                    body = response.read(MAX_RESPONSE_BYTES + 1)
                    if len(body) > MAX_RESPONSE_BYTES:
                        return site, "TOO_LARGE"
                    charset = response.headers.get_content_charset() or "utf-8"
                    return site, check_response(body.decode(charset, errors="replace"))

            if attempt < RETRIES and (
                result in ("HTTP_408", "HTTP_425", "HTTP_429")
                or result.startswith("HTTP_5")
            ):
                time.sleep(RETRY_DELAY * (attempt + 1))
                continue
            return site, result

        except urllib.error.HTTPError as error:
            code = error.code
            if attempt < RETRIES and (code in (408, 425, 429) or code >= 500):
                time.sleep(RETRY_DELAY * (attempt + 1))
                continue
            return site, "HTTP_%s" % code
        except (socket.timeout, TimeoutError):
            if attempt < RETRIES:
                time.sleep(RETRY_DELAY * (attempt + 1))
                continue
            return site, "TIMEOUT"
        except urllib.error.URLError as error:
            reason = str(getattr(error, "reason", error)).lower()
            if attempt < RETRIES:
                time.sleep(RETRY_DELAY * (attempt + 1))
                continue
            if "timed out" in reason or "timeout" in reason:
                return site, "TIMEOUT"
            return site, "CONNECTION_ERROR"
        except http.client.IncompleteRead:
            if attempt < RETRIES:
                time.sleep(RETRY_DELAY * (attempt + 1))
                continue
            return site, "INCOMPLETE_RESPONSE"
        except Exception as error:
            if attempt < RETRIES:
                time.sleep(RETRY_DELAY * (attempt + 1))
                continue
            print("[验活异常] %s: %s" % (site["name"], str(error)[:160]))
            return site, "ERROR"

    return site, "ERROR"


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


def save_json(path, data):
    """先写临时文件，再原子替换，避免中断时留下不完整 JSON。"""
    temp_path = path + ".tmp"
    with open(temp_path, "w", encoding="utf-8", newline=chr(10)) as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write(chr(10))
    os.replace(temp_path, path)


def save_links(updated, sites, results):
    ok_sites = [site for site, status in results if status in VALID_STATUSES]
    failed = [(site, status) for site, status in results if status not in VALID_STATUSES]
    now = datetime.now(timezone.utc).astimezone(timezone(timedelta(hours=8)))
    base = "https://cdn.jsdelivr.net/gh/%s@%s" % (SLUG, BRANCH)
    raw = "https://raw.githubusercontent.com/%s/%s" % (SLUG, BRANCH)
    fence = chr(96) * 3

    lines = [
        "# TVBox 配置地址（自动生成）",
        "",
        "生成时间：%s (UTC+8)　上游数据更新：%s" % (
            now.strftime("%Y-%m-%d %H:%M"), updated or "未知"
        ),
        "",
        "源数量：去重后共 %d 个，当前可用 %d 个，不可用 %d 个。" % (
            len(sites), len(ok_sites), len(failed)
        ),
        "",
        "## 推荐：验活版",
        "",
        fence,
        base + "/config/tvbox-ok.json",
        fence,
        "",
        "## 全量版（包含暂时不可用的源）",
        "",
        fence,
        base + "/config/tvbox-all.json",
        fence,
        "",
        "## GitHub 原始直链（备用）",
        "",
        fence,
        raw + "/config/tvbox-ok.json",
        fence,
        "",
        "## 上游原始 TVBox 配置",
        "",
        fence,
        base + "/tvbox.json",
        base + "/multi.json",
        fence,
        "",
        "## 更新与验活说明",
        "",
        "- 不根据 adult 字段过滤源；所有有非空 API 地址的源均参与构建。",
        "- 空 API 和重复 API 不重复写入；全量版保留验活失败的源。",
        "- 验活请求使用接口地址的 ac=list 参数，兼容原地址已有查询参数。",
        "- 只有解析出 CMS JSON（包含 list/class）或 XML（包含 list 节点）才进入验活版。",
        "- 网络超时、HTTP 错误、HTML 页面及无效数据不会进入验活版。",
        "- 定时更新频率由仓库现有 GitHub Actions 工作流决定。",
        "",
    ]

    if failed:
        lines.extend([
            "## 本轮未通过验活的源",
            "",
            "| 源 | 结果 |",
            "|---|---|",
        ])
        for site, status in failed:
            name = site["name"].replace("|", "\\|").replace(chr(10), " ")
            lines.append("| %s | %s |" % (name, status))
        lines.append("")

    with open(LINKS_OUT, "w", encoding="utf-8", newline=chr(10)) as f:
        f.write(chr(10).join(lines))


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    updated, total, sites, skipped_empty, skipped_duplicate = load_sites()

    print("=" * 60)
    print("CineNest TVBox 配置构建")
    print("=" * 60)
    print("上游更新时间：%s" % (updated or "未知"))
    print("上游原始数量：%d" % total)
    print("有效 API 去重后：%d" % len(sites))
    print("跳过空 API：%d" % skipped_empty)
    print("跳过重复 API：%d" % skipped_duplicate)
    print("adult 字段过滤：关闭")
    print("=" * 60)

    # 全量版包含所有有效 API 源，不受验活结果影响。
    save_json(ALL_OUT, build(sites, "CineNest 全量采集源"))
    print("[完成] %s" % ALL_OUT)

    with cf.ThreadPoolExecutor(max_workers=WORKERS) as executor:
        results = list(executor.map(probe, sites))

    ok_sites = [site for site, status in results if status in VALID_STATUSES]
    failed = [(site, status) for site, status in results if status not in VALID_STATUSES]

    for index, (site, status) in enumerate(results, 1):
        print("[%d/%d] %-30s %s" % (
            index, len(results), site["name"][:30], status
        ))

    save_json(OK_OUT, build(ok_sites, "CineNest 验活版"))
    save_links(updated, sites, results)

    print()
    print("=" * 60)
    print("构建完成")
    print("总源数量：%d" % len(sites))
    print("可用源数量：%d" % len(ok_sites))
    print("未通过验活：%d" % len(failed))
    if sites:
        print("可用率：%.2f%%" % (len(ok_sites) * 100.0 / len(sites)))
    print("输出：%s / %s / %s" % (ALL_OUT, OK_OUT, LINKS_OUT))
    print("=" * 60)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as error:
        print("[构建失败] %s" % error, file=sys.stderr)
        sys.exit(1)
