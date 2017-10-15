MODULES_DIR = "modules"
DEFAULT_MODULES = {"texts", "sites"}

CATEGORIES_DIR = "categories"
TAGS_DIR = "tags"

COMPONENTS_DIR = "components"
TEMPLATES_DIR = "templates"
VARIABLES_DIR = "variables"

CONFIG_FILE_NAME = "config.yml"
SITE_CONFIG_FILE_NAME = "site_config_file.yml"

DYNAMIC_PAGES_DIR = "dynamic_pages"

ROOT_LEVEL_PATHS = {
    MODULES_DIR,
    COMPONENTS_DIR,
    TAGS_DIR,
    CATEGORIES_DIR,
    TEMPLATES_DIR,
    VARIABLES_DIR,
    DYNAMIC_PAGES_DIR,
    CONFIG_FILE_NAME,
    SITE_CONFIG_FILE_NAME
    }

ROOT_LEVEL_PATHS_LOWER = set([x.lower() for x in ROOT_LEVEL_PATHS])

ROOT_LEVEL_DIRS_LOWER = ROOT_LEVEL_PATHS_LOWER.copy()

# housekeeping
ROOT_LEVEL_DIRS_LOWER.remove(CONFIG_FILE_NAME.lower())
ROOT_LEVEL_DIRS_LOWER.remove(SITE_CONFIG_FILE_NAME.lower())
# < housekeeping

ROOT_LEVEL_FILES_LOWER = {CONFIG_FILE_NAME.lower(), SITE_CONFIG_FILE_NAME.lower()}


MODULE_FILE_EXTS_LOWER = {"md", "markdown"}
TEMPLATE_FILE_EXT_LOWER = "syml"
