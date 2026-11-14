# ZZZOD 插件模板仓

绝区零一条龙（ZenlessZoneZero-OneDragon）第三方插件模板。用本模板创建仓库、写代码、推送 tag，GitHub Actions 会自动校验并发布 `<id>.zip`，之后到插件市场提交即可上架。本文讲从建仓到上架的流程。

- 在线插件市场：<https://onedragon-anyone.github.io/plugin-data/>
- 客户端：<https://github.com/OneDragon-Anything/ZenlessZoneZero-OneDragon>
- **模板仓**：<https://github.com/OneDragon-Anyone/plugin-template>（插件参考）
- 数据仓：<https://github.com/OneDragon-Anyone/plugin-data>（插件提交）
- 市场仓：<https://github.com/OneDragon-Anyone/plugin-market>（插件服务）

如果你只是想查包结构、字段与代码规范，请看 [CONTRIBUTING.md](CONTRIBUTING.md)。

## 目录结构

```text
your-repo/
├── README.md                  # 必需，展示在插件市场详情页
├── CONTRIBUTING.md            # 插件开发规范
├── LICENSE                    # 必需
├── .github/workflows/
│   ├── release.yml            # 推送 v* tag 时发布（只调用官方可复用工作流）
│   └── validate.yml           # 推送和 PR 时校验
├── scripts/                   # 本地校验和打包脚本
└── sample_plugin/             # 插件包，目录名 = 插件 ID，会被整体打进 zip
    ├── plugin.json            # 上架必需：网页展示用的元数据，不参与运行时身份
    ├── __init__.py            # 必需：插件包按 Python 包加载
    ├── const.py               # 运行时身份：APP_ID 等，手写
    ├── factory.py
    ├── app.py
    └── ...
```

## 第一次使用

1. 点 GitHub 上的 **Use this template**（推荐）或 Fork 本仓库。
2. **启用 Actions**：Fork 出来的仓库默认禁用工作流。进入仓库 `Actions` 页，点 *I understand my workflows, go ahead and enable them*。
3. **允许 Actions 写 Release**：`Settings → Actions → General → Workflow permissions` 选 *Read and write permissions*。
4. **推荐开启不可变 Release**：`Settings → General → Releases` 勾选 *Enable release immutability*。开启后已发布的版本无法被替换，插件市场会显示"不可变"标记。
5. 改名：把 `sample_plugin` 换成你的插件 ID，清单见 [改名清单](CONTRIBUTING.md#改名清单)。
6. 编辑 `<id>/const.py` 和 `<id>/plugin.json`，用 [本地命令](CONTRIBUTING.md#本地命令) 里的校验脚本跑一遍。
7. 提交并推送，等 `Validate Plugin` 通过。

## 发布版本

1. 修改 `plugin.json` 的 `version`，并把 `versionCode` 加 1。
2. 提交。
3. 打 tag 并推送：

```shell
git tag v0.2.0
git push origin v0.2.0
```

`Release Plugin` 工作流会：校验仓库 → 确认 tag 等于 `v<version>` → 打包 `<id>.zip` → 再次校验 zip → 创建 GitHub Release 并上传 zip。

- `version` 含 `-`（如 `0.2.0-beta.1`）时自动标记为 **pre-release**，插件市场作为 beta 版本展示。
- 发完 tag 去 Releases 页确认版本不是 Draft、附件里有 `<id>.zip`。草稿 Release 不会被收录，也不会报错，容易以为已经发出去了。
- 不要手动往 Release 上传或替换 zip。已收录版本的 sha256 一旦记录就不会再变，替换附件会被收录流程标记 `asset_changed`，并沿用首次记录的哈希。
- 同一个 `versionCode` 不能重复发布；改坏了就发一个更大的 `versionCode`。

工作流的版本跟随见 [工作流版本](CONTRIBUTING.md#工作流版本)。

## 提交到插件市场

插件市场详情页展示你插件仓库的 `README.md`。提交前把它换成插件介绍，模板里的建仓说明是给作者看的，对使用者没有用。

1. 确认已有至少一个带 `<id>.zip` 附件的 Release。
2. 打开插件市场的 **提交插件** 页，粘贴仓库地址，确认预览无误后点 **提交**。
3. 页面会打开一个预填好的 `[submission]` Issue，点 GitHub 的 *Submit new issue*。
4. 机器人自动校验并开 PR，维护者审核合并后上架。进度都在 Issue 里回复。

提交者必须是自己插件仓库的 admin。之后每次发新 Release，插件市场会在下一次定时构建时自动同步，不需要再次提交；想立刻刷新，在收录 Issue 下回复 `/sync`。

校验没过时，机器人会在 Issue 里写明原因，改完在仍开着的收录 Issue 下回复 `/recheck` 重新校验。发版后市场里一直没出现，去数据仓 Actions 的 **Build Market** 看最近一次运行的 Summary，那里逐条列出每个插件的结果和未收录原因。
