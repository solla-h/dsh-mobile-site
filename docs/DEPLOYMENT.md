# 部署：Cloudflare Pages Git 集成

> 已于 2026-11-07（UTC+8）上线：<https://fatwhale.app/>。
> Pages 使用 GitHub 集成；GitHub Actions 与 Pages 都执行仓库的静态检查。

## 仓库与产物

| 项目 | 值 |
| --- | --- |
| GitHub 仓库 | `solla-h/dsh-mobile-site` |
| 生产分支 | `main` |
| 正式域名 | `fatwhale.app`（已关联 Pages；Cloudflare DNS 的根域 CNAME 指向下列 Pages 主机名） |
| Pages 主机名 | `dsh-mobile-site-5cm.pages.dev`（注意自动分配的 `-5cm` 后缀） |
| 可部署目录 | `site/`（仓库根目录不是产物） |
| 构建 | 无框架、无 npm；纯静态 HTML/CSS |
| APK | 不在本仓库；继续由 App 的 GitHub Releases 分发（约 103 MB，超过 Pages 单文件上限） |

## Pages 项目配置

使用 **Git integration**（Cloudflare 的 GitHub App 授权仓库），不添加 Cloudflare API Token。

| 设置 | 值 |
| --- | --- |
| 项目名 | `dsh-mobile-site` |
| Production branch | `main` |
| Root directory | 留空（仓库根目录） |
| Framework preset | None |
| Build command | `python3 -I scripts/check_site.py`（只检查，不生成产物；非零退出阻止发布） |
| Build output directory | `site` |
| Build watch paths | Include `site/*`、`scripts/check_site.py`；Exclude 留空 |
| Preview deployments | 非 `main` 分支自动生成预览（默认公开、带 `X-Robots-Tag: noindex`） |

GitHub Actions 的 `site-ci / check` 在 PR、push 到 `main` 和手动触发时执行检查。
Pages 不等待 GitHub CI，因此在自己的 Build command 中重跑同一脚本：检查失败时
该次部署失败，不替换当前生产站。`main` 当前未设置分支保护；不要把 CI 当成合并限制。

## 发布记录（2026-11-07，UTC+8）

- [首次发布 PR #1](https://github.com/solla-h/dsh-mobile-site/pull/1) 已通过 CI 并合入 `main`，页面提交为 `e4850a625a99d21f94d538c093de585ade21d8dc`。
- Pages 项目已连接 `solla-h/dsh-mobile-site`，`main` 自动部署已启用；命令、输出目录和路径过滤均已回读核对。
- 首次生产部署 `490ca691-9df6-4d59-a8da-4ceb9884eaa1` 成功；同一提交的 GitHub `check` 和 `Cloudflare Pages` 检查均为 success。
- 绑定前核查：域名无 DNS 记录、Worker 路由、Single Redirect Rules 或 Page Rules。通过 Pages 自定义域名流程添加根域 CNAME，关联 `fatwhale.app`；未配置 `www`。
- **源码确认 / CLI 实测：** 本地检查通过（2 HTML、1 CSS、8 个本地引用）；临时副本删除样式后，检查按预期以非零状态退出。正式域名 `/`、`/en/`、`/styles.css` 均能通过有效 HTTPS 获取，内容与提交文件逐字节一致；HTTP `/en/` 返回 301 到对应 HTTPS 地址。
- **浏览器实测：** 正式中文首页可打开；360px 移动视口下 `scrollWidth = innerWidth = 360`，未发现横向溢出。浏览器自动化在导航阶段受控制状态失效影响，未完成整条旅程。
- **真机实测：** 本轮未执行。手机完整的「首页 → Releases → 返回 → 安装指南 → FAQ → 反馈」旅程、指尖操作体验与 200% 缩放仍待验证；浏览器视口模拟不等同于真机验收。

日常查询可使用已登录的 Wrangler（无需重复打开控制台）：

```bash
wrangler pages project list
wrangler pages deployment list --project-name dsh-mobile-site
```

首次 GitHub 连接、自定义域名与路径过滤通过控制台配置；日常发布由 Git 推送触发。
不要用 `wrangler pages deploy` 替代正常流程，否则会绕过 Pages 的 Git 构建检查。

## 首次上线顺序

1. 合并页面到 `main`，确认仓库中确实有 `site/index.html`。
2. 创建 Git 集成的 Pages 项目，按上表配置，先检查 `pages.dev` 的部署结果。
3. 走完手机和桌面浏览旅程，用户确认后再绑定正式域名。
4. 确认域名所在 zone 与 Pages 项目属于同一 Cloudflare 账号，先检查现有 DNS、
   Worker 路由和重定向。
5. 在项目 **Custom domains → Set up a domain** 中绑定域名并按引导确认 DNS；
   不要只手填指向 `pages.dev` 的 CNAME，未关联自定义域名可能出现 522。
6. 验证 HTTPS、下载/指南链接、移动端布局、分享卡片和 canonical 后，再把官网
   入口加到 App 仓库。

## 更新

修改 `site/` → 提 PR → 使用 Pages 给出的预览链接检查 → CI 通过并合并到 `main` →
Pages 自动更新正式站。小改动也走同一路径，便于定位线上内容对应的提交。
只改文档或 GitHub workflow 时跳过 Pages 构建；修改 `scripts/check_site.py` 会触发重新检查。
预览地址默认公开，`noindex` 只是防索引，不是访问控制；预览中不要放秘密。

## 搜索与统计

页面使用正式品牌 DSH Mobile App，提供 robots、sitemap 与站点名称结构化数据。
Cloudflare Web Analytics 已在 Pages 中启用，随之后的 Git 部署自动注入；不要在 HTML
再手动添加同一信标。查看 Metrics → View Web Analytics，按 Host 筛选 `fatwhale.app`。
搜索策略、指标口径、隐私边界、验证结果与 Search Console 待办见 [DISCOVERY.md](DISCOVERY.md)。

## 回滚

1. 在 Cloudflare Dashboard 打开项目的 **Deployments**。
2. 选择此前成功的一个 **production deployment**，执行 **Rollback to this deployment**。
   预览部署不是有效的回滚目标。
3. 在 Git 中 revert 出问题的提交或提交修复，正常走 PR，保证仓库与下一次部署一致。

回滚网站不需要重发 APK，也不要移动发布 tag 或替换历史 APK。

## 核对记录（2026-11-06）

- 无框架项目可以不填 Build command；非零退出码会把构建标记为失败。
- Production branch、Root directory、Build output directory、Build watch paths 都是项目级设置。
- 非生产分支生成预览部署；预览默认公开，并带 `X-Robots-Tag: noindex`。
- 回滚只接受成功构建过的 production deployment；预览部署不是有效的回滚目标。

## 边界

- 不把整个仓库作为输出目录；`docs/`、`scripts/`、`.github/` 都不发布。
- 首版不使用 Pages Functions、服务端或数据库。
- 不提交密钥、真实主机信息、配对码或用户数据。
- APK 始终以 GitHub Releases 为唯一来源；网站下载按钮链接 Releases 列表。

## 官方参考

- [部署纯静态 HTML](https://developers.cloudflare.com/pages/framework-guides/deploy-anything/)
- [GitHub 集成](https://developers.cloudflare.com/pages/configuration/git-integration/github-integration/)
- [构建配置](https://developers.cloudflare.com/pages/configuration/build-configuration/)
- [构建路径过滤](https://developers.cloudflare.com/pages/configuration/build-watch-paths/)
- [预览部署](https://developers.cloudflare.com/pages/configuration/preview-deployments/)
- [自定义域名](https://developers.cloudflare.com/pages/configuration/custom-domains/)
- [回滚](https://developers.cloudflare.com/pages/configuration/rollbacks/)
