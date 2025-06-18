from pathlib import Path

# Version is used for caching and for tracking when Lua data modules were last 
# updated.
version = '1.4.2.1'

_root = Path(__file__).parent.resolve()
assets_root = _root / f'extracted_assets/{version}'
cache_root  = _root / 'cache'
output_dir  = _root / 'out'

languages      = ['english'] # ['chinese', 'english']
language_codes = ['en'] # ['zh', 'en']
wiki_language  = 'english'
