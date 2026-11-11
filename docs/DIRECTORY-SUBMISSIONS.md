# 目录站收录提交清单（第三阶段）

> 核对日期：2026-11-11。本文件记录**已核实的入口、可复制文案**与执行约束（见文末）。
> 这些入口需要登录、人机验证或人工审核，属于以账号身份进行的外部公开动作，须由用户本人操作或明确授权。
> 不承诺收录、外链权重或排名收益；目录站链接是否 `nofollow` / UGC 未核实。价值首先是让正在搜同类词的人能找到项目。

## 先分清提交哪个仓库

用户列的四个入口里，**只有 DSH Hub 明确同时收「插件和客户端」**，其余插件目录按「可用 `dsh plugin add` 安装的插件」审核。
因此不要拿 App 仓库去投插件目录，大概率因「不是插件」被拒：

| 目标 | 建议提交仓库 | 理由 |
| --- | --- | --- |
| dsh.plus | `solla-h/dsh-plugin-mobile-gateway` | 该站收的是 DSH 插件；网关插件有可验证的安装命令 |
| DSH Hub | `solla-h/dsh-mobile-app` | 该站明确收 client，分类可用 Interface |
| DSH 插件目录（awesome list） | `solla-h/dsh-plugin-mobile-gateway` | 数据驱动列表要求 `dsh.bundle` / 可安装插件 |
| DeepSeek Harness Discussions | 以项目整体介绍为主 | 社区发布帖，不受插件/客户端分类限制 |

产品名始终是 **DSH Mobile App**；「大肥鱼 / FatWhale」只是本站的独立项目品牌，用于消歧，不能写成官方组织或暗示与 DeepSeek 有关联。

---

## 1. dsh.plus

- 提交页：<https://dsh.plus/zh/submit>　审核标准：<https://dsh.plus/zh/guides/submit-to-dsh-plus>
- 表单字段（带 `*` 必填）：插件名称 `*`、GitHub 链接 `*`、分类 `*`、一句话简介 `*`、投稿者邮箱 `*`、补充说明；提交前有 Turnstile 人机验证，邮箱仅用于审核联系、不公开展示。
- 分类选项：Agent 增强 / 工具集成 / UI 主题 / 自动化工作流 / 开发工具 / 其他。建议选「工具集成」或「开发工具」。
- 人工审核四条标准：原创有价值、真实可用、文档齐全、与 DSH 生态相关；隐含要求是宽松开源许可（MIT / Apache-2.0 等）。同一仓库重复投稿会被查重拦截。
- 常见被拒原因：README 语焉不详、安装命令不可验证、与 DSH 无关或只是薄封装、已被收录或高度重复、无许可或禁止再分发、仓库归档或 404。

**一句话简介（可直接粘贴）：**

> DSH Mobile App 的配套手机网关插件，让 Android 客户端连上自托管的 DeepSeek Harness 宿主，查看会话进度、处理审批与提问；版本按 compatibility.json 锁定。

**补充说明：**

> 安装命令见 App 仓库 `compatibility.json` 的 `recommended.gateway.install`，形如 `dsh plugin --profile web add github:solla-h/dsh-plugin-mobile-gateway#<锁定 tag>`。本项目维护的 fork 与上游同名 npm 包是不同发布线，请勿混装。客户端为第三方开源 Android 公开 alpha，与 DeepSeek 官方无关联；官网 <https://fatwhale.app/>，安装教程 <https://fatwhale.app/install/>，版本说明 <https://fatwhale.app/compatibility/>。

## 2. DSH Hub（dsh-hub.org）

- 提交页：<https://dsh-hub.org/submit>，需先 **Sign in**（verified account），未登录只能看到说明。
- 页面明确写「Share a DeepSeek Harness plugin or client」；流程为公开 GitHub 仓库 → 自动检查 → 人工审核。
- 列出要求：公开仓库；README 清楚说明与 DeepSeek Harness 的关系；包含 setup / build / installation 说明；归档、停用、私有或无关仓库会被拒。
- 目录分类含 Marketplace、Vision、Terminal、Interface、Workflow、Productivity；客户端建议归 **Interface**。首页未给出联系邮箱或独立投稿表单。

**项目描述（英文，可直接粘贴）：**

> FatWhale / DSH Mobile App is a third-party, open-source Android client for self-hosted DeepSeek Harness (DSH) hosts. With the companion mobile gateway plugin, it lets you check session progress, handle approvals and questions, and continue conversations from a phone. The agent keeps running on your own host; the phone runs no model. Public Android alpha, sideloaded from GitHub Releases — no app-store build, iOS deferred and unverified. Not affiliated with DeepSeek or Expo. Website: https://fatwhale.app/ · Setup: https://fatwhale.app/install/ · Source: https://github.com/solla-h/dsh-mobile-app

## 3. DSH 插件目录（awesome list）

用户说的「DSH 插件目录」在生态里对应多个数据驱动的列表，按 PR 提交、README 由脚本生成，**不要手改生成出来的 README**。优先选第一个：

| 列表 | 提交方式 | 关键要求 |
| --- | --- | --- |
| `awesome-dsh-plugin/awesome-dsh-plugin` | 新增 `data/plugins/<owner>__<repo>.yml` 后提 PR；字段 `url`、`name`、`category`、`description.en`、`description.zh` | `package.json` 声明 `dsh.bundle`、能用 `dsh plugin add` 安装、仓库公开且创建满 1 天、有 `dsh-plugin` topic、描述与代码相符、仓库活跃 |
| `cccakeee/awesome-dsh-plugins`（同步到 deepseekharnessplugins.com） | PR 在对应分类下加一行 `- [name](url) — 一句话描述`，合并后最多 6 小时同步 | 相关、真实、无密钥/推广链接、README 诚实；建议加 `dsh-plugin` topic |
| `dsh-plugin.org`（DSH Plugin Hub） | 公开仓库 + `dsh-plugin` topic + 安装命令 + 导出 `apply(ctx)`，由扫描自动收录 | 新条目初始为 `unconfirmed`，社区核实后才变 `verified` |

`awesome-dsh-plugin` 的 YAML 示例（提交网关插件时按实际 `category` 取值核对）：

```yaml
url: https://github.com/solla-h/dsh-plugin-mobile-gateway
name: solla-h/dsh-plugin-mobile-gateway
category: remote
description:
  en: Mobile gateway plugin that pairs DSH Mobile App with a self-hosted DeepSeek Harness host.
  zh: 让 DSH Mobile App 与自托管 DeepSeek Harness 宿主配对的手机网关插件。
```

`category` 必须取上游 `contributing.md` 列出的固定值之一，提交前核对；不要凭本文示例直接合入。

## 4. DeepSeek Harness GitHub Discussions

- 入口：<https://github.com/deepseek-ai/deepseek-harness/discussions>；社区项目发布用 **Show Your Plugins!** 分类（slug `show-your-plugins`），同分类已有 `dsh-task-dispatch`、`dsh-design-studio` 等发布帖。
- 需 GitHub 登录才能发帖/投票。官方仓库不接受外部 PR，社区通过 Discussions、插件、文章参与；措辞须写明是社区项目，不声称官方收录、认证或推荐。

**标题（英文）：**

> [Community] FatWhale / DSH Mobile App — an Android client for self-hosted DeepSeek Harness

**正文（英文，可直接粘贴）：**

> Hi everyone — sharing a community project, not an official DeepSeek release.
>
> DSH Mobile App (site brand: FatWhale / 大肥鱼) is a third-party, open-source Android client for a DeepSeek Harness host that you run yourself. With the companion mobile gateway plugin, the phone shows what is running and what is waiting on you, lets you answer approvals and questions, and lets you continue a conversation. The agent and the model stay on the host; the phone runs no model and hosts no service.
>
> What you need: a host running DSH Web, the mobile gateway plugin in the matching profile, an Android phone, and a network path to the gateway. App, gateway, DSH and the optional voice bundle are pinned to an exact combination in `compatibility.json` — a mismatch means stop and check, not auto-upgrade.
>
> Current state: public Android alpha, sideloaded from GitHub Releases. There is no app-store build; iOS is deferred and unverified. No system push notifications, no promise of background always-on, and not verified on every Android device.
>
> Links: website https://fatwhale.app/ · install guide https://fatwhale.app/install/ · compatibility https://fatwhale.app/compatibility/ · FAQ https://fatwhale.app/faq/ · APK https://fatwhale.app/download/ · source https://github.com/solla-h/dsh-mobile-app
>
> Feedback and issue reports are welcome via GitHub Issues. This is an independent project, not affiliated with DeepSeek or Expo.

---

## 提交前检查清单

- [ ] 两个仓库都是公开、未归档、根目录有 LICENSE；README 写清「解决什么问题 / 怎么装 / 怎么用」。
- [ ] 插件仓库已加 `dsh-plugin` topic；安装命令可直接复制验证，且指向锁定 tag 而非 `@latest`。
- [ ] 所有文案都写明「第三方开源项目，与 DeepSeek 官方无关联」「Android 公开 alpha、侧载安装」。
- [ ] 不写死 APK 文件名、不用 `/releases/latest`，不写用户数、star 数、评价、性能数字或未验证能力。
- [ ] 不宣称 iOS 可用、应用商店发行、稳定版、所有机型兼容、系统推送或永不断线。
- [ ] 同一仓库不要向同一站点重复投稿；被拒后按理由修正再提交。

## 执行约束

- 本站改动按仓库约定需用户授权后才能 commit / push 到 `main`；push 会触发 Cloudflare Pages 自动部署。
- dsh.plus 的 Turnstile、DSH Hub 的登录态属于账号级人机/身份校验，只能由账号本人在已登录环境完成；可程序化的通道仅限 GitHub Discussions（`gh` / GraphQL）与列表 PR。
- 投稿文案中的站内链接（`fatwhale.app/install/` 等）必须先确认线上已发布，否则会留下 404 外链。
- 收录、外链与流量效果都要在提交并发布之后观察，不从此清单推断排名收益。

## 执行记录（2026-11-11）

经用户明确授权后执行；发布与线上验证先于投稿完成，站内链接均已生效。

| 渠道 | 结果 | 链接 |
| --- | --- | --- |
| DeepSeek Harness Discussions | 已发布到「Show Your Plugins!」分类，社区项目口径，发文前全库查重无重复 | <https://github.com/deepseek-ai/deepseek-harness/discussions/12942> |
| DSH 插件目录（awesome list） | 已提 PR，仅新增 `data/plugins/solla-h__dsh-plugin-mobile-gateway.yml`；PR 正文已披露该仓库是上游 `Clarklevis1995` 条目的 fork，可能被判重复 | <https://github.com/awesome-dsh-plugin/awesome-dsh-plugin/pull/14265> |
| dsh.plus | 未提交：表单有 Turnstile 人机验证且投稿者邮箱必填，须由账号本人填写 | <https://dsh.plus/zh/submit> |
| DSH Hub | 未提交：需先 Sign In（verified account）才能看到提交表单；`hello@dsh-hub.org` 是联系邮箱而非投稿入口 | <https://dsh-hub.org/submit> |

配套动作：按列表规则给 `solla-h/dsh-plugin-mobile-gateway` 补了 `dsh-plugin` topic；站点已 push 到 `main` 并由 Cloudflare Pages 部署（提交 `c5e418f`）。

> 重复投稿提醒：以上两个编号就是「已投过」的凭据，后续不要再向同一站点提交同一仓库；PR 若被合并或关闭，回来更新本表状态。
