# 部署：Cloudflare Pages Git 集成

> 上线准备：已核验 Wrangler 认证及 Cloudflare GitHub 集成对本仓库的访问权限。
> Pages 项目与正式域名状态以本文「发布记录」为准。

## 仓库与产物

| 项目 | 值 |
| --- | --- |
| GitHub 仓库 | `solla-h/dsh-mobile-site` |
| 生产分支 | `main` |
| 正式域名 | `fatwhale.app`（已由用户持有并托管在 Cloudflare；尚未绑定本站） |
| 可部署目录 | `site/`（仓库根目录不是产物） |
| 构建 | 无框架、无 npm；纯静态 HTML/CSS |
| APK | 不在本仓库；继续由 App 的 GitHub Releases 分发（约 103 MB，超过 Pages 单文件上限） |

## Pages 项目配置

使用 **Git integration**（Cloudflare 的 GitHub App 授权仓库），不添加 Cloudflare API Token。

| 设置 | 值 |
| --- | --- |
| 项目名 | `dsh-mobile-site`（创建时确认可用） |
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

## 发布记录

- 本地中文和英文页面检查通过，已准备 `fatwhale.app` 的 canonical 与语言链接。
- Cloudflare GitHub 集成可以访问 `solla-h/dsh-mobile-site`；待提交页面后创建 Pages 项目。
- 正式域名尚未绑定；需授权后核查现有 DNS、Worker 路由与重定向，再绑定并验证。

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
