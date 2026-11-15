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

`.github/workflows/sync.yml` 每天 **北京时间 08:00** 运行：

1. `scripts/sync.py` 下载上游 `zknjjjx/tvbox` 的 main 分支压缩包，镜像 `cmstv.json`、`tvbox.json`、`niuniu.json`、`multi.json`、`upstream/`、`assets/` 到本仓库（上游 README 另存为 `README-upstream.md`，不覆盖本文件）
2. `scripts/build_config.py` 把 `cmstv.json`（上游自定义 `cmstv/1` 结构，源只有 `name`/`api`）转成标准 TVBox 结构：补 `type:1`、唯一 `key`、`searchable/quickSearch/filterable`，补齐 `parses`/`lives` 空数组，剔除 `adult:true` 源
3. 对每个源请求 `接口地址?ac=list`，只保留能返回 CMS JSON/XML 的源，生成 `config/tvbox-ok.json`
4. 重写 `LINKS.md`，提交并推送

也可以在仓库 **Actions → 同步上游并重建配置 → Run workflow** 手动触发。

## 文件说明

| 路径 | 说明 |
|---|---|
| `cmstv.json` | 上游源清单原始文件（自定义结构，壳不能直接用） |
| `tvbox.json` / `multi.json` | 上游已生成的 TVBox 结构配置 |
| `niuniu.json` | 上游附带的一份配置 |
| `upstream/` | 上游收录的其他作者配置 |
| `config/tvbox-ok.json` | **本仓库产物**，验活后的标准 TVBox 配置 |
| `config/tvbox-all.json` | **本仓库产物**，全部非成人源 |
| `LINKS.md` | **本仓库产物**，地址清单 + 失效源列表 |
| `scripts/` | 同步与转换脚本 |

## 注意

- jsdelivr 对 `@main` 有缓存，更新后可能延迟生效；急用可在地址后加 `?t=时间戳`
- 备用直链走 GitHub 源站：`https://raw.githubusercontent.com/fenghao0/tvbox/main/config/tvbox-ok.json`
- GitHub 对长期无提交的公开仓库会暂停定时工作流（约 60 天），届时在 Actions 页面点一次 Enable 即可恢复
- 源均为第三方影视采集站，内容版权归原站，仅供自用；请勿用于分发或商用
