# 搜索可发现性与站长统计

核对日期：2026-11-07。正式产品名称为 **DSH Mobile App**；它是配套 DeepSeek Harness（DSH）的第三方开源 Android 客户端，与 DeepSeek 官方无关联。网站英文示意不代表 App 已提供英文界面。

## SEO / GEO 实施

- 两页统一产品名称；标题与可见首段直接说明 DeepSeek Harness、Android 和第三方身份。
- 保留各自 canonical、完整绝对地址的双向 hreflang，以及直接可抓取的 HTML 正文、FAQ 和普通链接。
- `WebSite` JSON-LD 使用同一站点名称和根域 URL，帮助明确网站身份。没有虚构评分、评论或下载量；本轮不追求软件评分富媒体结果。
- `site/sitemap.xml` 只列中文、英文两个 canonical URL；`site/robots.txt` 提供 sitemap 地址并允许抓取。不添加没有维护依据的 lastmod，也不设置无效的 priority/changefreq。
- 原生 HTML/CSS、系统字体，无前端框架；站长统计由 Pages 注入。没有隐藏关键词、批量薄内容页或重复的 AI 专用文档。
- Google 的 AI Overviews / AI Mode 沿用常规搜索要求，不要求特殊 schema 或 `llms.txt`。这些改动改善可理解性与抓取条件，不保证收录、排名或 AI 引用。

本地与发布检查验证名称、语言残留、标题、description、canonical/hreflang、JSON-LD、robots、sitemap 和本地资源。检查器另有标准库回归测试：

```bash
python3 -I scripts/test_check_site.py
python3 -I scripts/check_site.py
```

Windows 使用 `python -I`。线上还需验证状态码、生产响应没有 `noindex`、正文和样式可抓取；本地通过不能证明 Google 已收录。

## 站长统计

已启用免费的 **Cloudflare Web Analytics / Pages 集成**，由 Pages 在后续部署中自动注入一次信标；仓库不复制 Token、不安装统计 SDK。查看入口为 Pages 项目 → Metrics → View Web Analytics；分析正式网站时按 Host 筛选 `fatwhale.app`，避免预览访问混入。普通 Wrangler Pages 命令没有启用开关；官方 API 创建统计站点需要 Account Settings Write，当前 Wrangler OAuth 对 RUM 接口返回权限不足，可使用已有登录的控制台一次开通。

| 指标 | 可以支持的判断 | 不能解释成 |
| --- | --- | --- |
| Visits / Page views | 流量变化、访问频次趋势 | 去重人数、App 活跃用户 |
| Host / Path | 中文与英文内容的使用比例 | App 的界面语言偏好 |
| Referer | 哪些站点带来访问 | 离站点击、GitHub 下载来源的完整归因 |
| Country / Device / Browser / OS | 内容语言、适配和性能优先级 | 某个人的身份或完整使用轨迹 |
| 页面性能 | 哪些页面或设备值得排查体验 | App 本身的性能 |

- 不使用 Cookie 或 localStorage 收集使用指标，也不以 IP / User-Agent 生成个人指纹；不据此声称整个网站或 Cloudflare“零日志”。页面页脚提供统计说明。
- 广告拦截、脚本未执行、网络失败及采样会漏计。数据用于观察趋势，不视为全部真实访问。
- 官方 FAQ 当前说明可查询过去六个月；七天后的长期数据会采样，查询本身也可能采样。需要更久的趋势时定期留存汇总。
- 不支持自定义事件或 UTM 查询参数统计。此方案不能直接统计“获取 APK”点击，更无法确认下载完成或安装；本轮不引入跳转服务或额外事件系统。

建议每周查看 `/` 与 `/en/` 的浏览量、来源主机、移动端占比和性能。结合 GitHub 问题反馈判断内容与适配方向，不用少量访问推断产品需求。

## Google 搜索效果与收录

Search Console 与 Cloudflare Web Analytics 解决不同问题：前者提供查询词、展示、点击、CTR、平均排名及索引状态，后者观察站内访问和性能。

Search Console 需要站长的 Google 账号与站点所有权验证；仓库文件不能代替验证。本轮未创建或验证 Search Console 资源，也未声称 sitemap 已提交。完成验证后：

1. 添加 `fatwhale.app` Domain property，按 Google 给出的真实 TXT 值完成 DNS 验证。
2. 提交 `https://fatwhale.app/sitemap.xml`，检查 `/` 和 `/en/` 的索引状态；必要时请求编入索引。
3. 每周观察品牌词、DeepSeek Harness 相关查询和两种语言页面的展示、点击及 CTR。Google 的 AI 搜索流量计入 Web 类型，不能从总量中直接推算 AI 引用次数。

## 验证记录

- **源码确认 / 自动检查：** 两页品牌与搜索元数据统一；英文页只保留两条中文语言切换文字；六项检查器回归测试和当前站点检查通过。
- **浏览器实测：** 在 Chromium 浏览器中，以 320、360、390、640、641、768、960、961、1024、1440 CSS px 分别验证中英文页面，共 20 组。检查文档溢出、手机框内底栏裁切和首屏标题越界，均通过；导航和语言切换目标高度均为 44px。
- 已修复复现的问题：手机示意固定比例导致底部裁切、强制单行标题越过文字列、英文会话示意撑开网格。保留现有视觉风格，窄屏导航更早换行。
- **真机实测：** 本轮未连接物理手机。浏览器尺寸模拟不证明真实设备上的字体、手指误触、性能或网络体验；自动点击旅程受浏览器工具控制状态失效阻断，没有计为通过。完整真机动线仍待验证，搜索排名、收录和后续流量效果仍需上线数据验证。

## 官方依据

- [Google：AI features and your website](https://developers.google.com/search/docs/appearance/ai-features)
- [Google：站点名称与 WebSite 结构化数据](https://developers.google.com/search/docs/appearance/site-names)
- [Google：标题链接](https://developers.google.com/search/docs/appearance/title-link)与[搜索摘要](https://developers.google.com/search/docs/appearance/snippet)
- [Google：本地化页面与 hreflang](https://developers.google.com/search/docs/specialty/international/localized-versions)
- [Google：构建和提交 sitemap](https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap)
- [Google：软件应用结构化数据](https://developers.google.com/search/docs/appearance/structured-data/software-app)
- [Cloudflare：Pages Web Analytics](https://developers.cloudflare.com/pages/how-to/web-analytics/)
- [Cloudflare：Web Analytics FAQ](https://developers.cloudflare.com/web-analytics/faq/)与[隐私说明](https://www.cloudflare.com/web-analytics/)
