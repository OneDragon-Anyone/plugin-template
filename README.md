# ZZZOD 插件模板仓

绝区零一条龙（ZenlessZoneZero-OneDragon）第三方插件模板。用本模板创建仓库、写代码、推送 tag，GitHub Actions 会自动校验并发布 `<插件ID>.zip`，再到 [插件仓库](https://onedragon-anyone.github.io/plugin-data/) 点一下提交即可上架。

## 目录结构

```text
your-repo/
├── README.md                  # 必需，展示在插件详情页
├── LICENSE                    # 必需
├── .github/workflows/
│   ├── release.yml            # 推送 v* tag 时发布（只调用官方可复用工作流）
│   └── validate.yml           # 推送和 PR 时校验
├── scripts/                   # 本地调试用的生成和校验脚本
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
- 一个仓库只有一个插件，一个插件只有一个应用。需要由父应用调用的子功能，做成另一个插件，并在其 `const.py` 里写 `INTERNAL_APP = True`。
- 根目录**不要**再放 `plugin.json`。
- 插件包内**不能**有 `requirements.txt`、`pyproject.toml`、`setup.py` 等依赖声明文件。插件只能使用一条龙主程序已有的依赖，不能引入第三方包。

## 第一次使用

1. 点 GitHub 上的 **Use this template**（推荐）或 Fork 本仓库。
2. **启用 Actions**：Fork 出来的仓库默认禁用工作流。进入仓库 `Actions` 页，点 *I understand my workflows, go ahead and enable them*。
3. **允许 Actions 写 Release**：`Settings → Actions → General → Workflow permissions` 选 *Read and write permissions*。
4. **推荐开启不可变 Release**：`Settings → General → Releases` 勾选 *Enable release immutability*。开启后已发布的版本无法被替换，插件仓库会显示"不可变"标记。
5. 改名：把 `sample_plugin` 换成你的插件 ID（见下文改名清单）。
6. 编辑 `<id>/const.py` 和 `<id>/plugin.json`，运行校验脚本。
7. 提交并推送，等 `Validate Plugin` 通过。

## 改名清单

假设插件 ID 为 `coffee_route_plus`：

```text
sample_plugin/    -> coffee_route_plus/
```

文件名都是固定的（`const.py`、`factory.py`、`app.py`、`app_setting.py`），不用改。需要同步修改 `const.py` 里的 `APP_ID`、Python 导入、类名，以及 `plugin.json` 里的 `id`、`homepage`、`author`。

## plugin.json

```json
{
  "id": "sample_plugin",
  "name": "示例插件",
  "summary": "展示第三方插件模板的最小结构。",
  "version": "0.1.0",
  "versionCode": 1,
  "author": {
    "name": "Your Name",
    "url": "https://github.com/your-name"
  },
  "homepage": "https://github.com/your-name/sample-plugin",
  "cover": "cover.png",
  "risk": ["automation"],
  "compatibility": {
    "minAppVersion": "0.0.0",
    "minCoreApiVersion": 1,
    "python": ">=3.11"
  }
}
```

| 字段 | 说明 |
| --- | --- |
| `id` | 必须等于插件包目录名和 `const.py` 的 `APP_ID`，匹配 `^[a-z][a-z0-9_]*$` |
| `name`、`summary` | 非空字符串，商店列表里展示 |
| `version` | 版本号，例如 `0.1.0`。发版 tag 必须是 `v` + `version`；客户端拿它和已装插件的 `PLUGIN_VERSION` 比较，决定要不要提示更新 |
| `versionCode` | 正整数，**每次发版必须递增**，不能重复或回退。插件仓库用它判断这次发布是否比已收录的新，不大于就会被拒收 |
| `author.name`、`author.url` | 两个都必须填，`url` 要带 `http://` 或 `https://` |
| `homepage` | 插件仓库地址，**必须带 `http://` 或 `https://`** |
| `cover` | 可选。插件包内的相对路径，png / jpg / webp，不超过 512 KB，推荐 16:9 |
| `risk` | 必须是数组，取值只能是 `filesystem` `network` `account` `automation` `ocr` `yolo` `clipboard` `process`；没有风险时写 `[]` |
| `compatibility` | 三个子字段都必填：`minAppVersion`（如 `0.0.0`）、`minCoreApiVersion`（整数）、`python`（如 `>=3.11`） |

`plugin.json` 是上架商店的**必需文件**，商店网页的元数据（名称、简介、版本、作者、风险、兼容性、封面）都从它读取；客户端运行时不靠它判断身份。`defaultGroup`、`needNotify` 等运行行为只写在 `const.py`，`plugin.json` 里不要放，也不再有 `apps`。

json 和 const 里有几个字段重复，按下面分工，避免漂移：

| 字段 | 来源 | 说明 |
| --- | --- | --- |
| `APP_ID` ↔ `id` | const 手写 | 运行时身份。CI 比对 `APP_ID == 目录名 == plugin.json.id` |
| `APP_NAME` ↔ `name` | const 手写 | CI 比对，不一致报 `NAME_MISMATCH` |
| `PLUGIN_VERSION` ↔ `version` | **从 json 生成** | 客户端用它判断已安装版本，必须与 json 一致 |
| `PLUGIN_AUTHOR` ↔ `author.name` | **从 json 生成** | 客户端列表展示 |
| `PLUGIN_HOMEPAGE` ↔ `homepage` | **从 json 生成** | 客户端把已安装插件对应到商店条目 |
| `PLUGIN_DESCRIPTION` ↔ `summary` | **从 json 生成** | 客户端展示 |
| `DEFAULT_GROUP`、`NEED_NOTIFY`、`INTERNAL_APP`、`PRIORITY`、`KEY_SIM_DIR` | const 手写 | 运行行为，json 里没有 |

`scripts/generate_const.py` 把「从 json 生成」的四项写进 `const.py` 末尾的标记块，标记块外的内容不动；CI 用 `--check` 检查，过期报 `CONST_OUTDATED`。改完 `plugin.json` 后运行一次即可。`const.py` 示例：

```python
APP_ID = "sample_plugin"
APP_NAME = "示例插件"
DEFAULT_GROUP = False
NEED_NOTIFY = False
# 可选：INTERNAL_APP、PRIORITY、KEY_SIM_DIR

# >>> generated from plugin.json (scripts/generate_const.py), do not edit
PLUGIN_VERSION = "0.1.0"
PLUGIN_AUTHOR = "Your Name"
PLUGIN_HOMEPAGE = "https://github.com/your-name/sample-plugin"
PLUGIN_DESCRIPTION = "展示第三方插件模板的最小结构。"
# <<< generated
```

## 本地命令

```shell
# 把 plugin.json 里重复的元数据生成到 const.py（改完 plugin.json 后运行）
python scripts/generate_const.py

# 校验仓库
python scripts/validate_plugin.py --strict

# 本地打包，输出 dist/<id>.zip 和 sha256
python scripts/build_zip.py
```

打包有体积上限：`<id>.zip` 不超过 50 MB，解压后总量不超过它的 10 倍。超过会被校验拒绝。

CI 不使用你仓库里的 `scripts/`，而是使用官方模板对应版本的脚本，所以本地脚本过旧时可从模板复制最新版。

## 本地调试

把插件包目录复制到主程序：

```text
ZenlessZoneZero-OneDragon/plugins/<插件ID>/
```

启动主程序后刷新插件注册。加载失败时查看插件管理页。

## 发布版本

1. 修改 `plugin.json` 的 `version`，并把 `versionCode` 加 1。
2. 运行 `python scripts/generate_const.py` 同步 `const.py` 的 `PLUGIN_VERSION` 等字段，提交。
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
    uses: OneDragon-Anyone/plugin-template/.github/workflows/reusable-release.yml@v2
```

- `@v2` 指向官方发布的 v2（一个 tag，内容固定），之后官方的修复不会自动包含进来。需要拿到新修复时，把 `@v2` 换成官方发布的新 tag。
- 想完全锁定，可把 `@v2` 换成具体的提交 sha，例如 `@3f2c1e...`。

> Fork 和 Use this template 创建的仓库**不会自动跟随模板更新**。旧版模板仓库里的 `release.yml` 直接运行 `softprops/action-gh-release`，不会生成 `<id>.zip`。请把 `.github/workflows/release.yml` 和 `validate.yml` 替换为本仓库的版本，并删除根目录的 `plugin.json` 和 `scripts/sync_manifest.py`。

## 提交到插件仓库

1. 确认已有至少一个带 `<id>.zip` 附件的 Release。
2. 打开插件仓库的 **提交插件** 页，粘贴仓库地址，确认预览无误后点 **提交**。
3. 页面会打开一个预填好的 `[submission]` Issue，点 GitHub 的 *Submit new issue*。
4. 机器人自动校验并开 PR，维护者审核合并后上架。进度都在 Issue 里回复。

提交者必须是插件仓库的 admin。之后每次发新 Release，插件仓库会在 6 小时内自动同步，不需要再次提交。

## 设置页

`app_setting.py` 提供 `AppSettingProvider` 示例。接入真实设置界面时，把 `get_setting_cls()` 中的占位导入替换为自己的 `BaseInterface` 或 `AppSettingFlyout` 类。
