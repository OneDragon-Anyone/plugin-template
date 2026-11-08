# 插件开发规范

写插件的细节都在这。建仓、发版、上架看 [README.md](README.md)。

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
| `version` | 版本号，例如 `0.1.0`。发版 tag 必须是 `v` + `version`；客户端读取它，和商店的最新版本比较，决定要不要提示更新 |
| `versionCode` | 正整数，**每次发版必须递增**，不能重复或回退。插件仓库用它判断这次发布是否比已收录的新，不大于就会被拒收 |
| `author.name`、`author.url` | 两个都必须填，`url` 要带 `http://` 或 `https://` |
| `homepage` | 插件仓库地址，**必须带 `http://` 或 `https://`** |
| `cover` | 可选。插件包内的相对路径，png / jpg / webp，不超过 512 KB，推荐 16:9 |
| `risk` | 必须是数组，取值只能是 `filesystem` `network` `account` `automation` `ocr` `yolo` `clipboard` `process`；没有风险时写 `[]` |
| `compatibility` | 三个子字段都必填：`minAppVersion`（如 `0.0.0`）、`minCoreApiVersion`（整数）、`python`（如 `>=3.11`） |

`plugin.json` 是上架商店的**必需文件**，商店网页的元数据（名称、简介、版本、作者、风险、兼容性、封面）都从它读取；客户端运行时不靠它判断身份。`defaultGroup`、`needNotify`、`apps` 是**已废弃**的旧字段：新插件不要写，运行行为（`DEFAULT_GROUP`、`NEED_NOTIFY` 等）只写在 `const.py`；已上架插件的 json 里还带着也不会被拒绝，校验只给 `WARN DEPRECATED_FIELD` 提示，取值不再校验，客户端也不读取。

客户端直接读 `plugin.json` 的 `version`、`author.name`、`homepage`、`summary` 作为界面展示、更新比对和商店条目匹配的依据；`const.py` 只放身份和运行行为，两边没有重复需要维护的字段：

| 文件 | 内容 |
| --- | --- |
| `plugin.json` | 元数据：`version`、`author`、`homepage`、`summary`、`cover`、`risk`、`compatibility` 等 |
| `const.py` | `APP_ID`、`APP_NAME`、`DEFAULT_GROUP`、`NEED_NOTIFY`，可选 `INTERNAL_APP`、`PRIORITY`、`KEY_SIM_DIR` |

只有 `id` / `name` 是两边都出现的：CI 比对 `APP_ID == 目录名 == plugin.json.id`、`APP_NAME == plugin.json.name`，不一致会失败。旧版 const 里的 `PLUGIN_VERSION` 等字段不再被客户端读取，也不被检查，可以删掉。`const.py` 示例：

```python
APP_ID = "sample_plugin"
APP_NAME = "示例插件"
DEFAULT_GROUP = False
NEED_NOTIFY = False
# 可选：INTERNAL_APP、PRIORITY、KEY_SIM_DIR
```

## 本地命令

```shell
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

## 插件数据

插件自己的持久化数据放 `plugin_data/<APP_ID>/`。主程序只给到这一层，路径里没有实例号：全局共享的数据直接放这里，要按实例分开就自己在下面再分一层。

取目录：

```python
data_dir = self.ctx.get_plugin_data_dir(const.APP_ID)   # 应用里：Application 上没有 data_dir
data_dir = self.data_dir                                # 工厂里：ApplicationFactory 的属性
```

返回 `Path`，目录不存在时自动创建。位置在插件代码之外，插件更新覆盖代码不会丢。

按实例再分一层（编号和本体 `config/<NN>/` 一致）：

```python
instance_dir = data_dir / f"{self.ctx.current_instance_idx:02d}"   # 应用里，与取运行记录用的是同一个
```

存 yml 用 `YamlOperator`，不用在外面包一层类：

```python
from one_dragon.base.config.yaml_operator import YamlOperator

data = YamlOperator(str(data_dir / "run_record.yml"))   # 按实例分的话换成 instance_dir
data.update("run_count", int(data.get("run_count", 0) or 0) + 1)
```

用户可调的设置不要走这里，用 `ApplicationConfig`，落在 `config/<NN>/<应用组>/<APP_ID>.yml`，按实例和账号分开。

不要用 `YamlConfig` 存插件数据。它固定写到 `config/[NN/]<module>.yml`，那是本体配置区。写进去之后，从源码跑一条龙的用户会一直在 `git status` 里看到这条未跟踪文件；本体重置配置时也不认它。

## 设置页

`app_setting.py` 提供 `AppSettingProvider` 示例。接入真实设置界面时，把 `get_setting_cls()` 中的占位导入替换为自己的 `BaseInterface` 或 `AppSettingFlyout` 类。
