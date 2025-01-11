Run script modules to generate data output for use on the wiki.

```
python -m script.<script_file_name>
```

## Credit

This is built on [PermDenied's code](https://github.com/cruiseliu/sandrock-scripts); I'm going through and expanding it so I can update the Lua modules.

## Asset Bundles

I'm using AssetStudioModGUI to export game assets, but the tool's output compared to what these scripts seem to expect has necessitated some preparatory steps. The imagine the original author had a more elegant workflow, but this is mine.

Unless otherwise mentioned, use these settings:

1. `Options -> Display all assets` (or you won't see `MonoScript`, `Transform`, or `GameObjects`)
1. `Options -> Export optons`
    1. `Group exported assets by -> type name`
    1. `File name format -> assetName@pathID`
    1. `Try to resore/Use original TextAsset extension name -> True`
1. Use `Filter Type` to filter just the types you want.
1. For `MonoScript`, `Transform`, or `GameObjects`, use `Export -> Dump -> Filtered assets` (or `Selected assets`, if appropriate); output should be `.txt`, not `.dat` (I had an easier time figuring out how to parse the `.txt` in Python than reading Unity `.dat`).
1. For everything else, `Export -> Filtered assets`.
1. When done with exporting from a bundle, filter/select all asset types/assets you exported and `Export -> Asset list to XML` to get your manifest.

### Designer Config

Export **MonoBehaviour**, **MonoScript** from `designer_config`.

### Story

Export **TextAsset** from `storyscript`.

### Resource Nodes

Export **MonoBehaviour**, **MonoScript**, **GameObject**, and **Transform** from `resourcepoint`.

### Scenes

There are over 90 scene bundles, and it's unreasonable to export them one-by-one. This is consequently more complicated.

Use `File -> Load folder` to load all of `scenes/additive` at once. Change the export options to `Group exported assets by -> source file name`.

Export **MonoBehaviour**, **MonoScript**, **GameObject**, and **Transform** assets and file list as usual.

Run `python -m scripts.prepare_assets` to sort the assets by type and split up the file list.

### Text

From `localization/english`, export:

```
*MonoBehaviour AssetItemEnglish
*MonoScript    AssetItem
```

### Sceneinfo

Export **MonoBehaviour**, **MonoScript** from `sceneinfo`.

### Images & Icons

And **Texture2D** and **Sprite** from:

```
uisystem_sprite
```

After each asset export, also export the assets list with Export -> Asset list to XML -> Filtered assets.

