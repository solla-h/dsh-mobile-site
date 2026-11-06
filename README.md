# DSH Mobile App 宣传站

DSH Mobile App（第三方开源 Android 客户端）的独立静态宣传站仓库。
生产分支 `main`，唯一可部署目录是 `site/`。

> **已上线：<https://fatwhale.app/>（中文）· <https://fatwhale.app/en/>（英文）。**
> Cloudflare Pages Git 集成从 `main` 自动部署，检查通过后只发布 `site/`。
> 项目配置、验证边界与回滚操作见 [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)。

## 本地预览

```bash
python -m http.server --bind 127.0.0.1 --directory site 4173
```

打开 <http://127.0.0.1:4173/>（中文）或 <http://127.0.0.1:4173/en/>（英文）。不要另写开发服务器，也不要提交预览产物。

## 检查

```bash
python3 -I scripts/check_site.py   # Linux / macOS / CI
python -I scripts/check_site.py    # Windows 没有 python3 命令时
```

脚本只使用 Python 标准库：检查文档基础、本地资源、品牌名称、英文残留、
canonical/hreflang、站点名称 JSON-LD、robots 和 sitemap。检查器回归测试使用
`python3 -I scripts/test_check_site.py`（Windows 用 `python -I`）。
交互演示的纯手势逻辑使用 `node scripts/test_demo.mjs` 检查，仅用 Node 内置断言，
不需要 npm 或安装依赖；网站仍是直接部署的静态文件。
CI 在 push 到 `main`、pull request 和手动触发时执行回归测试与静态检查。
Pages 执行静态检查作为发布门槛，通过后只发布 `site/`。
搜索优化、统计指标与隐私边界见 [docs/DISCOVERY.md](docs/DISCOVERY.md)。

## 目录

```text
site/                  # 唯一部署输出；index.html（中文）、en/index.html（英文）、styles.css
scripts/check_site.py  # 本地与 CI 共用的静态检查
docs/BRIEF.md          # 内容槽位、布局、事实边界与验收
docs/DEPLOYMENT.md     # Cloudflare Pages Git 集成、更新与回滚
AGENTS.md              # 后续 Claude 的工作边界
```

## 事实来源（只读）

App 不在本仓库，不复制其源码；素材只允许下述已授权的宠物静态帧和两段原动画。页面事实统一链接到：

- App 仓库：<https://github.com/solla-h/dsh-mobile-app>
- APK 唯一分发入口：[GitHub Releases](https://github.com/solla-h/dsh-mobile-app/releases)
- 版本锁定：[compatibility.json](https://github.com/solla-h/dsh-mobile-app/blob/master/compatibility.json)、
  [兼容表](https://github.com/solla-h/dsh-mobile-app/blob/master/docs/COMPATIBILITY.md)
- 安装：[Agent 安装手册](https://github.com/solla-h/dsh-mobile-app/blob/master/docs/AGENT-SETUP.md)、
  [中文使用说明](https://github.com/solla-h/dsh-mobile-app/blob/master/docs/USER-GUIDE.zh-CN.md)
- 许可：[LICENSE](https://github.com/solla-h/dsh-mobile-app/blob/master/LICENSE)、
  [NOTICE](https://github.com/solla-h/dsh-mobile-app/blob/master/NOTICE)

不要写死 APK 文件名，也不要使用 `/releases/latest`（当前版本是 prerelease）。

## 许可

本仓库原创代码与文案采用 MIT，见 [LICENSE](LICENSE)。
`site/media/da-fei-yu.webp` 静态帧及 `da-fei-yu-idle.webp`、`da-fei-yu-happy.webp`
两段原动画，是经用户确认用于非商业展示的第三方宠物素材，
另按 **CC BY-NC-SA 4.0** 使用，不属于 MIT。署名、来源和改动说明见
[素材署名](site/media/ATTRIBUTION.txt) 与 [NOTICE](NOTICE)。
图片已经准备好，预览与部署不需要图像处理工具或额外构建步骤。
