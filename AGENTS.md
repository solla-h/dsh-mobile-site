# AGENTS.md

本仓库是 DSH Mobile 的独立静态宣传站：GitHub 仓库 `solla-h/dsh-mobile-site`，
生产分支 `main`，唯一部署目录 `site/`。App 源码在另一个仓库，只在事实层面引用。

## 当前阶段

- 中文与英文页面已完成，正在接通 CI/CD 与首次发布；实时部署状态见 [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)。
- 修改内容前读 [docs/BRIEF.md](docs/BRIEF.md)，部署问题读 [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)。
- 网站提供简体中文和英文；App 的 i18n 和 iOS 版本都暂缓，不要宣称 iOS 可用。

## 事实来源（只读）

页面和文档只使用以下绝对地址，不要复制 App 源码或素材：

- App 仓库：<https://github.com/solla-h/dsh-mobile-app>
- APK 唯一来源：[Releases](https://github.com/solla-h/dsh-mobile-app/releases)
  （当前为 Android 公开 alpha、侧载安装；不要写死 APK 文件名或使用 `/releases/latest`）
- 版本锁定：[compatibility.json](https://github.com/solla-h/dsh-mobile-app/blob/master/compatibility.json)、
  [docs/COMPATIBILITY.md](https://github.com/solla-h/dsh-mobile-app/blob/master/docs/COMPATIBILITY.md)
- 安装：[docs/AGENT-SETUP.md](https://github.com/solla-h/dsh-mobile-app/blob/master/docs/AGENT-SETUP.md)、
  [docs/USER-GUIDE.zh-CN.md](https://github.com/solla-h/dsh-mobile-app/blob/master/docs/USER-GUIDE.zh-CN.md)、
  [docs/USER-GUIDE.md](https://github.com/solla-h/dsh-mobile-app/blob/master/docs/USER-GUIDE.md)
- 许可：[LICENSE](https://github.com/solla-h/dsh-mobile-app/blob/master/LICENSE)、
  [NOTICE](https://github.com/solla-h/dsh-mobile-app/blob/master/NOTICE)

事实冲突时以 App 仓库当前文件和 GitHub Releases 为准；发版信息不要靠记忆补。

## 页面归属

- `site/`：网站页面、样式和未来的公开素材，只放可部署内容。
- `docs/`、`scripts/`、`.github/`：交接与工具，不进入 Pages 输出。
- Claude 可按用户任务修改本仓库页面与本地部署配置；实际发布网站、绑定域名或修改线上配置须有用户授权。
- 不要修改 App 仓库；需要新事实时提交 issue 或等待 App 侧更新链接目标。

## 内容与素材红线

- 不放真实主机地址、配对码/二维码、设备标识、账号、密钥或用户对话。
- 截图必须脱敏，并明确标注「真机截图」或「界面示意」；示意图不能冒充截图。
- **不要复制 App 的 `assets/pet/` 宠物素材**：它们是 CC BY-NC-SA 4.0，仅限非商业，
  不随本仓库的 MIT 许可。需要视觉素材时自行制作或明确授权后再用。
- 不虚构用户数量、评价、性能指标或未验证的能力；不宣称系统推送、后台常驻、
  永不断线、零数据留存、应用商店发行或所有机型兼容。

## 工程约定

- 纯静态 HTML/CSS；不引入 npm、框架或构建步骤。后续确需工具时必须说明理由。
- 本地预览只用 `python -m http.server --bind 127.0.0.1 --directory site 4173`。
- 提交前运行 `python3 -I scripts/check_site.py`（Windows 用 `python -I`）。
- 未获授权时不 commit/push；push 前须获同意。已有本轮明确的提交或推送授权时，按授权范围执行。
- **没有用户明确授权，不要创建 Cloudflare Pages 项目、绑定域名或修改 DNS。**

## 许可

本仓库内容 MIT（见 [LICENSE](LICENSE)）。App 原创代码 MIT；宠物素材
CC BY-NC-SA 4.0 仅限非商业，本网站不得复制。
