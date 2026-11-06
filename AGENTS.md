# AGENTS.md

本仓库是 DSH Mobile App 的独立静态宣传站：GitHub 仓库 `solla-h/dsh-mobile-site`，
生产分支 `main`，唯一部署目录 `site/`。App 源码在另一个仓库，只在事实层面引用。

## 当前阶段

- 中文与英文页面已上线：<https://fatwhale.app/>、<https://fatwhale.app/en/>；CI/CD、验证与回滚见 [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)。
- 修改内容前读 [docs/BRIEF.md](docs/BRIEF.md)，部署问题读 [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)。
- 网站提供简体中文和英文；App 的 i18n 和 iOS 版本都暂缓，不要宣称 iOS 可用。
- 产品对外名称固定为 **DSH Mobile App**；不要使用另一个项目的名称 DSH Mobile。英文示意须完整英文化，并注明实际 App 界面仍为简体中文。
- 搜索优化与站长统计方案见 [docs/DISCOVERY.md](docs/DISCOVERY.md)。不虚构评价、下载量或搜索排名收益。

## 事实来源（只读）

产品事实使用以下绝对地址，不复制 App 源码；宠物素材仅允许下文已授权的例外，素材来源与许可链接见 `site/media/ATTRIBUTION.txt`：

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
- **宠物素材仅限已授权的非商业展示**：用户于 2026-11-07 允许按 CC BY-NC-SA 4.0
  引入必要的大肥鱼素材，随后选择可操作的网页演示。目前使用 `site/media/da-fei-yu.webp`
  静态帧，以及 `da-fei-yu-idle.webp`、`da-fei-yu-happy.webp` 原动画；来源、改动及署名
  见 `site/media/ATTRIBUTION.txt` 和 `NOTICE`。该素材及衍生图不属于 MIT，须保持署名、
  非商业和相同方式共享条件；不得据此批量复制 App 素材或改为商业用途。
- 不虚构用户数量、评价、性能指标或未验证的能力；不宣称系统推送、后台常驻、
  永不断线、零数据留存、应用商店发行或所有机型兼容。

## 工程约定

- 静态 HTML/CSS；用户已允许宠物、插件翻页、弧形会话三项示意使用少量原生 JavaScript。
  演示只使用虚构数据，不访问真实网关、创建真实会话或修改插件；失去脚本后仍应可读。
  不引入 npm、框架或构建步骤。纯手势逻辑以 Node 内置断言检查，不需要安装依赖。
- 本地预览只用 `python -m http.server --bind 127.0.0.1 --directory site 4173`。
- 提交前运行 `python3 -I scripts/check_site.py`（Windows 用 `python -I`）。
- 未获授权时不 commit/push；push 前须获同意。已有本轮明确的提交或推送授权时，按授权范围执行。
- **没有用户明确授权，不要创建 Cloudflare Pages 项目、绑定域名或修改 DNS。**

## 许可

本仓库原创代码与文案 MIT（见 [LICENSE](LICENSE)）。App 原创代码 MIT；本站使用的
大肥鱼素材单独采用 CC BY-NC-SA 4.0，仅限非商业，不纳入 MIT；见 [NOTICE](NOTICE)。
