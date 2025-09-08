Run script modules to generate data output for use on the wiki.

```
python -m script.<script_file_name>
```

## Credit

This is built on [PermDenied's code](https://github.com/cruiseliu/sandrock-scripts); I'm going through and expanding it so I can update the Lua modules.

## Asset Bundles

I'm using AssetStudioModGUI (https://github.com/aelurum/AssetStudio/releases) to export game assets, but the tool's output compared to what these scripts seem to expect has necessitated some preparatory steps. I imagine the original author had a more elegant and simpler method, but this is mine.

Unless otherwise mentioned, use these settings:

1. `Options -> Display all assets` (or you won't see `MonoScript`, `Transform`, or `GameObjects`)
1. `Options -> Export optons`
    1. `Group exported assets by -> type name`
    1. `File name format -> assetName@pathID`
    1. `Try to resore/Use original TextAsset extension name -> True`

Then, follow these steps to export for each asset bundle file.

1. Use `Filter Type` to filter just the types you want.
1. For `MonoScript`, `Transform`, or `GameObjects`, use `Export -> Dump -> Filtered assets` (or `Selected assets`, if appropriate); output should be `.txt`, not `.dat` (I had an easier time figuring out how to parse the `.txt` in Python than reading Unity `.dat`).
1. For everything else, `Export -> Filtered assets`.
1. When done with exporting, filter/select all asset types/assets you exported and `Export -> Asset list to XML` to get your manifest.

Not all scripts need all assets. See the notes in each script to determine what you need.

### Designer Config

Export **MonoBehaviour**, **MonoScript** from `designer_config`.

### Text

From `localization/english`, export:

```
MonoBehaviour AssetItemEnglish
MonoScript    AssetItem
```

### Story

Export **TextAsset** from `storyscript`.

### Resource Nodes

Export **MonoBehaviour**, **MonoScript**, **GameObject**, and **Transform** from `resourcepoint`.

### Home

From `home`, export:

```
MonoBehaviour HomeToolSetting
MonoBehaviour HomeToolSettingExtra
MonoScript    HomeToolSetting
```

### Monsterspawnasset

From `monsterspawnasset`, export:

```
MonoBehaviour SpawnMonsterAsset
MonoScript    SpawnMonsterAsset
```

### Scenes

There are over 90 scene bundles, and it's unreasonable to export them one-by-one. This is consequently more complicated. There are also a **lot** of assets here, as in, over a million files.

Use `File -> Load folder` to load all of `scenes/additive` at once. Change the export options to `Group exported assets by -> source file name`.

Export **MonoBehaviour**, **MonoScript**, **GameObject**, and **Transform** assets and file list as usual.

Run `python -m scripts.prepare_assets` to sort the assets by type and split up the file list.

### Sceneinfo

Export **MonoBehaviour**, **MonoScript** from `sceneinfo`.

### Images & Icons

Get **Texture2D** and **Sprite** from: `uisystem_sprite`.

