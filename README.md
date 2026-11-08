# ZZZOD 插件模板仓

绝区零一条龙（ZenlessZoneZero-OneDragon）第三方插件模板。用本模板创建仓库、写代码、推送 tag，GitHub Actions 会自动校验并发布 `<插件ID>.zip`，再到 [插件仓库](https://onedragon-anyone.github.io/plugin-data/) 点一下提交即可上架。

写插件时的细节（改名、`plugin.json` 字段、插件数据、设置页、本地命令与调试）见 [CONTRIBUTING.md](CONTRIBUTING.md)。

## 目录结构

```text
your-repo/
├── README.md                  # 必需，展示在插件详情页
├── CONTRIBUTING.md            # 插件开发规范：改名、字段、数据存储
├── LICENSE                    # 必需
├── .github/workflows/
│   ├── release.yml            # 推送 v* tag 时发布（只调用官方可复用工作流）
│   └── validate.yml           # 推送和 PR 时校验
├── scripts/                   # 本地校验和打包脚本
└── sample_plugin/             # 插件包，目录名 = 插件 ID，会被整体打进 zip
    ├── plugin.json            # 上架商店必需：网页展示用的元数据，不参与运行时身份
    ├── __init__.py            # 必需：插件包按 Python 包加载
    ├── const.py               # 运行时身份：APP_ID 等，手写
    ├── factory.py
    ├── app.py
    └── ...
```

规则：

- 仓库根目录下**恰好一个**子目录第一层同时有 `factory.py` 和 `const.py`，该目录就是插件包。旧写法 `*_factory.py` / `*_const.py` 继续兼容，但不推荐。
- 插件 ID 匹配 `^[a-z][a-z0-9_]*$`，运行时身份只认 `const.py` 的 `APP_ID`：`APP_ID == 插件包目录名`，且 `plugin.json.id` 必须与它一致（只做比对）。
- 一个仓库只有一个插件，一个插件注册一个应用（一个工厂）。插件里的子功能写成 `Operation`，由这个应用直接调用，不需要单独做应用。只有需要在应用列表里单独出现、单独配置或单独运行的功能，才做成另一个插件。
- 根目录**不要**再放 `plugin.json`。
- 插件包内**不能**有 `requirements.txt`、`pyproject.toml`、`setup.py` 等依赖声明文件。插件只能使用一条龙主程序已有的依赖，不能引入第三方包。

## 第一次使用

1. 点 GitHub 上的 **Use this template**（推荐）或 Fork 本仓库。
2. **启用 Actions**：Fork 出来的仓库默认禁用工作流。进入仓库 `Actions` 页，点 *I understand my workflows, go ahead and enable them*。
3. **允许 Actions 写 Release**：`Settings → Actions → General → Workflow permissions` 选 *Read and write permissions*。
4. **推荐开启不可变 Release**：`Settings → General → Releases` 勾选 *Enable release immutability*。开启后已发布的版本无法被替换，插件仓库会显示"不可变"标记。
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

- `version` 含 `-`（如 `0.2.0-beta.1`）时自动标记为 **pre-release**，插件仓库作为 beta 版本展示。
- 不要手动往 Release 上传或替换 zip。已收录的版本 sha256 一旦记录就不会再变，替换附件会被插件仓库标记 `asset_changed` 并继续使用旧记录。
- 同一个 `versionCode` 不能重复发布；改坏了就发一个更大的 `versionCode`。

### 工作流版本

`release.yml` 只有几行，真正的逻辑在官方模板的可复用工作流中：

```yaml
on:
  push:
    tags:
      - "v*"
permissions:
  contents: write
jobs:
  release:
    uses: OneDragon-Anyone/plugin-template/.github/workflows/reusable-release.yml@v1
```

- `@v1` 跟随官方 v1 版本的修复，不会有破坏性变化。
- 想完全锁定，可把 `@v1` 换成具体的提交 sha，例如 `@3f2c1e...`。

> Fork 和 Use this template 创建的仓库**不会自动跟随模板更新**。旧版模板仓库里的 `release.yml` 直接运行 `softprops/action-gh-release`，不会生成 `<id>.zip`。请把 `.github/workflows/release.yml` 和 `validate.yml` 替换为本仓库的版本，并删除根目录的 `plugin.json` 和 `scripts/sync_manifest.py`。

## 提交到插件仓库

详情页展示你仓库的 `README.md`。提交前把它换成插件介绍，模板里的建仓说明是给作者看的，对使用者没有用。

1. 确认已有至少一个带 `<id>.zip` 附件的 Release。
2. 打开插件仓库的 **提交插件** 页，粘贴仓库地址，确认预览无误后点 **提交**。
3. 页面会打开一个预填好的 `[submission]` Issue，点 GitHub 的 *Submit new issue*。
4. 机器人自动校验并开 PR，维护者审核合并后上架。进度都在 Issue 里回复。

提交者必须是插件仓库的 admin。之后每次发新 Release，插件仓库会在 6 小时内自动同步，不需要再次提交。
