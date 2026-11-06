# DSH Mobile 宣传站

DSH Mobile（第三方开源 Android 客户端）的独立静态宣传站仓库。
生产分支 `main`，唯一可部署目录是 `site/`。

> **当前状态：开发骨架，尚未上线。**
> 目前只有一个中性占位页；拟使用 `fatwhale.app`，尚未创建 Cloudflare Pages 项目或绑定网站域名。
> 页面设计与正式文案由后续 Claude 完成，先读
> [docs/BRIEF.md](docs/BRIEF.md)。

## 本地预览

```bash
python -m http.server --bind 127.0.0.1 --directory site 4173
```

打开 <http://127.0.0.1:4173/>。不要另写开发服务器，也不要提交预览产物。

## 检查

```bash
python3 -I scripts/check_site.py   # Linux / macOS / CI
python -I scripts/check_site.py    # Windows 没有 python3 命令时
```

脚本只使用 Python 标准库：检查 `site/` 下每个 HTML 的 `lang`、`<title>` 和
viewport，并验证 HTML/CSS 引用的本地资源与链接确实存在。
CI 在 push 到 `main` 和 pull request 时运行同一条命令。

## 目录

```text
site/                  # 唯一部署输出；index.html + styles.css
scripts/check_site.py  # 本地与 CI 共用的静态检查
docs/BRIEF.md          # 内容槽位、布局、事实边界与验收
docs/DEPLOYMENT.md     # Cloudflare Pages Git 集成、更新与回滚
AGENTS.md              # 后续 Claude 的工作边界
```

## 事实来源（只读）

App 不在本仓库，也不要在本仓库复制其源码或素材。页面事实统一链接到：

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

本仓库自身内容采用 MIT，见 [LICENSE](LICENSE)。
App 的原创代码是 MIT；`assets/pet/` 宠物素材是 CC BY-NC-SA 4.0，仅限非商业使用，
不得复制进本网站。
