# 搜索可发现性与站长统计

核对日期：2026-11-07。正式产品名称为 **DSH Mobile App**；它是配套 DeepSeek Harness（DSH）的第三方开源 Android 客户端，与 DeepSeek 官方无关联。网站英文示意不代表 App 已提供英文界面。

## SEO / GEO 实施

- 两页统一产品名称；标题与可见首段直接说明 DeepSeek Harness、Android、第三方身份，并带上可独占的站点品牌「大肥鱼 / FatWhale」。
- 保留各自 canonical、完整绝对地址的双向 hreflang，以及直接可抓取的 HTML 正文、FAQ 和普通链接。
- `WebSite` JSON-LD 使用同一站点名称和根域 URL；两页另有 `SoftwareApplication` JSON-LD，说明 `operatingSystem: Android`、`applicationCategory: DeveloperApplication` 与指向 GitHub Releases 的 `downloadUrl`。没有虚构评分、评论、软件版本或下载量，也不追求软件评分富媒体结果。
- `site/sitemap.xml` 列六个 canonical URL（中英首页 + 四个中文专题页）；`site/robots.txt` 提供 sitemap 地址并允许抓取。不添加没有维护依据的 lastmod，也不设置无效的 priority/changefreq。
- 原生 HTML/CSS、系统字体，无前端框架；站长统计由 Pages 注入。没有隐藏关键词、批量薄内容页或重复的 AI 专用文档。
- Google 的 AI Overviews / AI Mode 沿用常规搜索要求，不要求特殊 schema 或 `llms.txt`。这些改动改善可理解性与抓取条件，不保证收录、排名或 AI 引用。

### 2026-11-10：一轮 SEO / GEO 核对

按 GitHub 开源 skill 与 Google 官方文档交叉核对，只做内容层改进，不引入新的抓取协议文件：

- [Google：AI optimization guide](https://developers.google.com/search/docs/fundamentals/ai-optimization-guide) 明确「为生成式 AI 搜索优化仍就是 SEO」，并把 `llms.txt`、内容「分块」、为 AI 改写文案、刷不真实提及、为 AI 功能过度投入结构化数据列为不需要做的事；准入条件只是页面已收录、可带摘要展示，且站点在 Search Console 中包含于生成式 AI 功能。
- 开源 skill 参考：[AgriciDaniel/claude-seo](https://github.com/AgriciDaniel/claude-seo)、[aaron-he-zhu/seo-geo-claude-skills](https://github.com/aaron-he-zhu/seo-geo-claude-skills)、[onvoyage-ai/gtm-engineer-skills](https://github.com/onvoyage-ai/gtm-engineer-skills)、[amplifying-ai/awesome-generative-engine-optimization](https://github.com/amplifying-ai/awesome-generative-engine-optimization)。与官方不冲突的可操作项是：前置自包含定义、可引用的事实块、列表/表格、问答结构、实体身份与消歧、指向一手来源。这些 skill 自身也标注 FAQPage 富媒体结果已对多数站点退役、评分只是启发式、不得承诺快速被引用、不得把估算当作实测。
- 基线实测：两页 title/description/canonical/hreflang/单个 h1/WebSite JSON-LD/OG/无 noindex/正文深度与层级合格；`robots.txt` 的 `Allow: /` 对 GPTBot、OAI-SearchBot、Claude-SearchBot、PerplexityBot、Googlebot、Bingbot 均返回 200，AI 爬虫没有被拦截。装饰性图片的空 `alt` 是无障碍设计，不为通过检查补写替代文本。
- 据此新增两页「一眼看清 / At a glance」段：一句自包含定义、逐条可核对的关键事实、身份与边界声明，以及指向 App 仓库、兼容说明和 Releases 的一手来源链接。事实全部来自 [BRIEF.md](BRIEF.md) 与仓库约定的事实边界，没有新增数字、日期、作者或评价。
- 当日刻意不做：`llms.txt`、AI 专用 schema（FAQPage / HowTo / SoftwareApplication）、批量页面、隐藏关键词、虚构引用或署名、为凑指标补写图片 alt。理由见上。
- **2026-11-11 调整**：按用户要求改为「四个有实质内容的中文专题页 + 两页 SoftwareApplication 结构化数据」。这不是推翻上一条的判断依据，而是把目标从「只做内容层」扩展到「按查询意图拆页 + 明确软件实体」：专题页各自回答安装、兼容、FAQ、下载四类问题，不是复制首页段落或批量薄内容；SoftwareApplication 只写可核对的系统、类别和下载入口，不补评分、评论、软件版本或下载量。仍然不做 `llms.txt`、FAQPage / HowTo 富媒体 schema、隐藏关键词和虚构引用；不承诺收录、排名或 AI 引用收益。

本地与发布检查验证名称、语言残留、标题、description、canonical/hreflang、JSON-LD、robots、sitemap 和本地资源。检查器另有标准库回归测试：

```bash
python3 -I scripts/test_check_site.py
python3 -I scripts/check_site.py
```

Windows 使用 `python -I`。线上还需验证状态码、生产响应没有 `noindex`、正文和样式可抓取；本地通过不能证明 Google 已收录。

### 2026-11-11：专题页与软件实体

| 页面 | 对准的查询意图 | 主要一手来源 |
| --- | --- | --- |
| `/` `/en/` | 品牌与产品定位 | 本站 BRIEF.md |
| `/install/` | DSH Mobile App 安装教程 / 配对 | AGENT-SETUP.md、USER-GUIDE.zh-CN.md |
| `/compatibility/` | DSH Mobile App 版本兼容 | compatibility.json、COMPATIBILITY.md |
| `/faq/` | DSH Mobile App 常见问题 | USER-GUIDE.zh-CN.md、BRIEF.md |
| `/download/` | DeepSeek Harness 安卓客户端 / APK 下载 | GitHub Releases |

页面主题词是定位，不是搜索量数据；GSC 实测查询词见上文。四个专题页只有中文版，英文页通过标注语言的链接给出入口，不设置会误导的 hreflang 配对。
`SoftwareApplication` 的 `downloadUrl` 指向 Releases 列表页而非某个 APK 文件，因为项目约定禁止写死文件名或使用 `/releases/latest`；因此不追求软件评分富媒体结果。
sitemap 扩为六个 URL；已提交的 sitemap 会由搜索引擎自行重抓，不重复提交，也不对已收录页面重复请求编入索引。
本地检查器新增内容页、SoftwareApplication 与品牌词校验，回归用例从 7 项增至 15 项；`python -I scripts/check_site.py`、`python -I scripts/test_check_site.py`、`node scripts/test_demo.mjs` 均通过，六个页面本地预览均返回 200。上线与收录效果仍需发布后观察。

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

2026-11-07 用户反馈已在 Edge 登录 Search Console 并提交网站，两个语言页面的“网址检查”
均显示未被索引；该结论来自用户反馈，当时未直接读取控制台。2026-11-10 改用本机 `bsk`
配合 Edge 扩展直接核对控制台，状态已经变化，以下均为实测结果：

- 资源为网域资源 `sc-domain:fatwhale.app`。`/` 与 `/en/` 均显示“网址已收录到 Google /
  网页已编入索引”，HTTPS 正常；界面已有“已请求编入索引 / 再次提交请求”，说明此前请求已生效。
  本轮**没有**再次请求编入索引：页面已收录，重复请求不会加速抓取。
- 站点地图起初“已提交的站点地图”为 0 行，本轮提交 `https://fatwhale.app/sitemap.xml` 后
  状态“成功”、已发现 2 个网页、上次读取 2026-11-10；已成功则不重复提交。
- “效果”报告（2026-11-05 至 2026-11-08，约 4 小时前更新）：总点击 0、总展示 12、CTR 0%、
  平均排名 9.8；查询 `dsh mobile` 6 次展示、`dsh mobile app` 2 次、`dsh-mobile` 1 次。
  站点已被收录但展示极少，搜索品牌词时经常不出现在结果页；这是新域名权重与同名项目竞争，
  不再是收录或技术抓取问题。GSC 数据约滞后两天，不能据此推断 AI 引用次数或未来排名。

Bing 是独立索引，Google Search Console 的提交不影响它。“Import from Google Search Console”
返回“未找到站点”，改用 XML 文件验证：`site/BingSiteAuth.xml` 已部署，线上
`https://fatwhale.app/BingSiteAuth.xml` 返回 200 / `application/xml`，内容与下载文件逐字节一致。
仍需在 Bing Webmaster Tools 点“Verify”并提交 sitemap；Bing 的抓取与收录尚待其自身完成。

后续跟踪：

1. 不重复提交 sitemap，也不再对已收录页面请求编入索引。
2. 每周观察品牌词、DeepSeek Harness 相关查询和两种语言页面的展示、点击及 CTR；Google 的
   AI 搜索流量计入 Web 类型，不能从总量中直接推算 AI 引用次数。
3. Bing 侧确认验证与 sitemap 提交成功，并单独跟踪其收录情况；不以少量展示推断产品需求。

## 验证记录

- **源码确认 / 自动检查：** 两页品牌与搜索元数据统一；英文页只保留两条中文语言切换文字；七项检查器回归测试和当前站点检查通过。交互版的键盘旅程与验证边界见 [BRIEF.md](BRIEF.md#宠物与手势展示)。
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
