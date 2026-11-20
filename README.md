# tvbox

`zknjjjx/tvbox` 的镜像仓库，每天自动同步并转换成影视壳 / TVBox 可直接使用的配置。

## 接口地址（推荐）

只含当前可用源：

```
https://cdn.jsdelivr.net/gh/fenghao0/tvbox@main/config/tvbox-ok.json
```

全量（含暂时不通的源）：

```
https://cdn.jsdelivr.net/gh/fenghao0/tvbox@main/config/tvbox-all.json
```

最新地址清单和本轮失效源，见 [`LINKS.md`](LINKS.md)（每天自动重写）。

## 更新机制

`.github/workflows/sync.yml` 每天 **北京时间 20:00**（UTC 12:00）运行：

1. `sync.py` 下载上游 `zknjjjx/tvbox` main 分支压缩包，镜像 `cmstv.json`、`tvbox.json`、`niuniu.json`、`multi.json`、`upstream/`、`assets/` 到本仓库（上游 README 另存为 `README-upstream.md`，不覆盖本文件；不镜像上游 `.github`，避免运行上游自己的采集工作流）
2. `build_config.py` 把 `cmstv.json`（上游自定义 `cmstv/1` 结构，源只有 `name`/`api`）转成标准 TVBox 结构：补 `type:1`、唯一 `key`、`searchable/quickSearch/filterable`，补齐 `parses`/`lives` 空数组
3. **并入单仓直连源**：读取已镜像的 `upstream/*.json`（上游从饭太硬、老刘备、肥猫等 13 个单仓抓取的配置快照），只取 `type:1` 且是 http 地址的源。`type:3` 是各仓专有解析器（`api` 形如 `csp_XXXGuard`），必须配该仓自己的 spider jar，搬过来只会播放失败，因此丢弃
4. **按人气排序**：`cmstv.json` 的 `hot` 字段表示该源被多少个上游清单收录（1~7），高的排前面，同人气时按存在时间排序。这能让客户端全局搜索更快命中
5. 对每个源请求 `接口地址?ac=list`，只保留能返回 CMS JSON/XML 的源，生成 `config/tvbox-ok.json`（48 并发、12 秒超时、指数退避重试）
6. 重写 `LINKS.md`，提交并推送

> 说明：本项目**不按 `adult` 字段过滤**，成人源保留。若需纯净版，改动 `build_config.py` 的 `load_sites()` 中对应分支即可。
>
> 上游 `repos.py` 的 `REPOS` 列表有 17 个单仓，本仓库 `upstream/` 只有 13 个——缺 OK、巧技、小米、宝盒，系上游自身拉取失败所致（实测 OK/巧技/小米 目前均已 502 或连不通）。

也可在仓库 **Actions → 同步上游并重建配置 → Run workflow** 手动触发。

## 文件说明

| 路径 | 说明 |
|---|---|
| `cmstv.json` | 上游源清单原始文件（自定义结构，壳不能直接用） |
| `tvbox.json` / `multi.json` | 上游已生成的 TVBox 结构配置 |
| `niuniu.json` | 上游附带的一份配置 |
| `upstream/` | 上游收录的其他作者配置 |
| `config/tvbox-ok.json` | **本仓库产物**，验活后的标准 TVBox 配置 |
| `config/tvbox-all.json` | **本仓库产物**，全部去重源（含未通过验活的） |
| `LINKS.md` | **本仓库产物**，地址清单 + 失效源列表 |
| `sync.py` / `build_config.py` | 同步与转换脚本 |

## 注意

- jsdelivr 对 `@main` 有缓存，更新后可能延迟生效；急用可在地址后加 `?t=时间戳`
- 备用直链走 GitHub 源站：`https://raw.githubusercontent.com/fenghao0/tvbox/main/config/tvbox-ok.json`
- GitHub 定时任务可能有几分钟排队延迟；长期无提交的公开仓库（约 60 天）会被暂停定时工作流，届时在 Actions 页面点一次 Enable 即可恢复
- 源均为第三方影视采集站，内容版权归原站，仅供自用；请勿用于分发或商用
