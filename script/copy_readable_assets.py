from sandrock import *
from sandrock.preproc import get_config_paths

import urllib.parse

def do() -> None:
    copy_designer_config()
    copy_text()
    copy_mission()

def copy_designer_config() -> None:
    config_paths = get_config_paths()
    for key in config_paths['designer_config'].keys():
        out_path = config.output_dir / 'designer_config' / (key + '.yaml')
        data = load_designer_config(key)
        if data:
            write_yaml(out_path, data)

def copy_text() -> None:
    out_path = config.output_dir / 'text.yaml'
    texts = defaultdict(dict)
    for lang, code in zip(config.languages, config.language_codes):
        lang_texts = load_text(lang)
        for id_, text in lang_texts.items():
            texts[id_][code] = text
    write_yaml(out_path, texts)

def copy_mission() -> None:
    bundle = Bundle('story_script')
    for asset in bundle.assets:
        if asset.type == 'TextAsset':
            out_path = config.output_dir / 'mission' / (asset.name + '.xml')
            xml = asset.read_xml()
            _recursive_unquote(xml)
            write_xml(out_path, xml)

def _recursive_unquote(element: ElementTree.Element) -> None:
    for k, v in element.attrib.items():
        if v and isinstance(v, str) and '%' in v:
            element.attrib[k] = urllib.parse.unquote(v)
    for child in element:
        _recursive_unquote(child)

if __name__ == '__main__':
    do()
