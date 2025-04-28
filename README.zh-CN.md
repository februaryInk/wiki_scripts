运行脚本模块生成并输出 Wiki 需要使用的数据。

```
python -m script.<脚本文件名>
```

## 致谢

本项目基于 [PermDenied 的代码](https://github.com/cruiseliu/sandrock-scripts) 构建；我正在进行扩展，以便能够更新 Lua 模块。

## 资源包（Asset Bundles）

我使用 AssetStudioModGUI 导出游戏资源，但该工具的输出与这些脚本预期的内容有所不同，因此需要一些准备步骤。原作者可能有更优雅和简单的方法，但这是我的方法。

在没有特别说明的情况下，请使用以下设置：

1. `Options -> Display all assets`（否则看不到 `MonoScript`、`Transform` 和 `GameObjects`）
1. `Options -> Export optons`
    1. `Group exported assets by -> type name`（按类型名称分组导出的资源）
    1. `File name format -> assetName@pathID`（设置文件名格式）
    1. `Try to resore/Use original TextAsset extension name -> True`（尝试恢复/使用原始 TextAsset 扩展名）

然后，对每个资源包文件按以下步骤导出。

1. 使用 `Filter Type` 筛选想要的类型。
1. 对于 `MonoScript`、`Transform` 或 `GameObjects`，使用 `Export -> Dump -> Filtered assets`（或 `Selected assets`，如果适用）；输出应为 `.txt` 而非 `.dat`（在 Python 中解析 `.txt` 比读取 Unity `.dat` 更容易）。
1. 对于其他所有内容，使用 `Export -> Filtered assets`。
1. 导出完成后，筛选/选择所有已导出的资源类型/资源，然后使用 `Export -> Asset list to XML` 获取列表。

并非所有脚本都需要所有资源。请查看每个脚本中的注释，确定需要哪些文件。

### 游戏配置（Designer Config）

从 `designer_config` 导出 **MonoBehaviour**、**MonoScript**。

### 文本（Text）

#### 对于英语

从 `localization/english` 导出：

```
MonoBehaviour AssetItemEnglish
MonoScript    AssetItem
```

#### 对于中文

从 `localization/chinese` 导出：

```
MonoBehaviour AssetItemChinese
MonoScript    AssetItem
```

### 剧情脚本（Story）

从 `storyscript` 导出 **TextAsset**。

### 资源点（Resource Nodes）

从 `resourcepoint` 导出 **MonoBehaviour**、**MonoScript**、**GameObject** 和 **Transform**。

### 家园（Home）

从 `home` 导出：

```
MonoBehaviour HomeToolSetting
MonoBehaviour HomeToolSettingExtra
MonoScript    HomeToolSetting
```

### 怪物生成（Monsterspawnasset）

从 `monsterspawnasset` 导出：

```
MonoBehaviour SpawnMonsterAsset
MonoScript    SpawnMonsterAsset
```

### 场景（Scenes）

游戏中场景包超过 90 个，一个一个导出不太现实，所以这部分操作较为复杂——此处包含了**大量**资源，文件超过一百万个。

使用 `File -> Load folder` 一次性加载所有 `scenes/additive`。将导出选项更改为 `Group exported assets by -> source file name`（按源文件名分组导出的资源）。

导出 **MonoBehaviour**、**MonoScript**、**GameObject** 和 **Transform** 资源及文件列表。

运行 `python -m scripts.prepare_assets`，按类型排序资源并拆分文件列表。

### 场景信息（Sceneinfo）

从 `sceneinfo` 导出 **MonoBehaviour** 和 **MonoScript**。

### 图片和图标（Images & Icons）

从 `uisystem_sprite` 获取 **Texture2D** 和 **Sprite**。
