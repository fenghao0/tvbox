# TVBox 配置地址（自动生成）

生成时间：2026-11-24 13:24 (UTC+8)　上游数据更新：2026-11-24 04:21 UTC

源数量：去重后共 138 个，当前可用 84 个，不可用 54 个。

## 推荐：验活版

```
https://cdn.jsdelivr.net/gh/fenghao0/tvbox@main/config/tvbox-ok.json
```

## 全量版（包含暂时不可用的源）

```
https://cdn.jsdelivr.net/gh/fenghao0/tvbox@main/config/tvbox-all.json
```

## GitHub 原始直链（备用）

```
https://raw.githubusercontent.com/fenghao0/tvbox/main/config/tvbox-ok.json
```

## 上游原始 TVBox 配置

```
https://cdn.jsdelivr.net/gh/fenghao0/tvbox@main/tvbox.json
https://cdn.jsdelivr.net/gh/fenghao0/tvbox@main/multi.json
```

## 更新与验活说明

- 不根据 adult 字段过滤源；所有有非空 API 地址的源均参与构建。
- 空 API 和重复 API 不重复写入；全量版保留验活失败的源。
- 验活请求使用接口地址的 ac=list 参数，兼容原地址已有查询参数。
- 只有解析出 CMS JSON（包含 list/class）或 XML（包含 list 节点）才进入验活版。
- 网络超时、HTTP 错误、HTML 页面及无效数据不会进入验活版。
- 定时更新频率由仓库现有 GitHub Actions 工作流决定。

## 本轮未通过验活的源

| 源 | 结果 |
|---|---|
| 飘零资源 | HTTP_403 |
| 卧龙资源·wolongzyw | INVALID_XML |
| 旺旺短剧 | HTML |
| 卧龙点播 | INVALID_XML |
| 魔爪资源 | INVALID_XML |
| AV-AIvin | HTTP_502 |
| 细胞采集黄色 | CONNECTION_ERROR |
| 旺旺资源 | HTML |
| 豆瓣资源·caiji | CONNECTION_ERROR |
| 豆瓣资源·dbzy | CONNECTION_ERROR |
| AV-百万资源 | CONNECTION_ERROR |
| AV-色嗨国 | CONNECTION_ERROR |
| caiji.dbzy5.com | CONNECTION_ERROR |
| zy.jinchancaiji.com | CONNECTION_ERROR |
| 七七影视 | CONNECTION_ERROR |
| 华为吧资源 | TIMEOUT |
| 卧龙资源·collect | CONNECTION_ERROR |
| 小猫咪资源 | CONNECTION_ERROR |
| 快播资源网站 | CONNECTION_ERROR |
| 蜂巢片库 | CONNECTION_ERROR |
| 金马资源网 | TIMEOUT |
| 黑木耳 | HTML |
| 黑木耳点播 | HTML |
| a.uezy.pw | HTML |
| fqzy4.me | CONNECTION_ERROR |
| to.to-long.com | CONNECTION_ERROR |
| vs.okcdn100.top | HTTP_404 |
| www.fantuan.tv | CONNECTION_ERROR |
| www.heimuer.tv | CONNECTION_ERROR |
| www.yyzywcj.com | CONNECTION_ERROR |
| zy.sh0o.cn | CONNECTION_ERROR |
| 三九影視 | HTTP_523 |
| 四九资源 | CONNECTION_ERROR |
| 奇虎资源 | CONNECTION_ERROR |
| 快云资源 | HTML |
| 快车资源 | CONNECTION_ERROR |
| 每天资源 | HTTP_404 |
| 海外看 | CONNECTION_ERROR |
| 熊掌资源 | CONNECTION_ERROR |
| 种子短剧 | HTML |
| 飘花影院 | HTTP_404 |
| 飞速资源 | CONNECTION_ERROR |
| 91av.cyou | TIMEOUT |
| 91jpzyw.com | HTML |
| siwazyw.tv | CONNECTION_ERROR |
| www.avre06.com | CONNECTION_ERROR |
| www.xiangjiaozyw.com | CONNECTION_ERROR |
| xxavs.com | TIMEOUT |
| xzybb2.com | CONNECTION_ERROR |
| 老刘备·👒┃小胡┃资源┃ | ERROR |
| 老刘备·🦁┃四九┃资源 | CONNECTION_ERROR |
| 老刘备·🛰️飞速┃采集 | CONNECTION_ERROR |
| 老刘备·⛱┃可可┃采集 | CONNECTION_ERROR |
| 老刘备·🎶明星┃MV | HTTP_401 |

## 每日接口状态变化

检查时间：2026-11-24 13:24:21 (UTC+8)

与上一次成功检查相比：新增可用 **0** 个；本次失效 **0** 个。

### 新增可用接口

| 源 | API |
|---|---|
| 无 | - |

### 本次失效接口

| 源 | API |
|---|---|
| 无 | - |
