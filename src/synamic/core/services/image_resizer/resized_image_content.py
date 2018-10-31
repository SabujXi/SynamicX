import mimetypes
import re
from PIL import Image
from synamic.core.contracts.content import ContentContract
from synamic.core.services.urls.url import _ContentUrl
from io import BytesIO


def construct_new_file_name_comps(path, width, height):
    basename = path.basename
    dircomps = path.dirname_comps

    m = re.search(r'(\.jpg|\.png|\.gif|\.jpeg)$', basename, re.I)
    if m:
        base = basename[:m.start()]
        ext = basename[m.start():m.end()]
        new_name = base + str(width) + 'x' + str(height) + ext
    else:
        new_name = basename + str(width) + 'x' + str(height)
    res = (*dircomps, new_name)
    return res


class ResizedImageContent(ContentContract):
    def __init__(self, site, original_image_path, width, height):
        self.__site = site
        self.__original_image_path = original_image_path
        self.__width = int(width)
        self.__height = int(height)
        self.__url = None

        self.__file_name_comps = construct_new_file_name_comps(self.__original_image_path, self.__width, self.__height)
        self.__new_file_path = self.__site.path_tree.create_cpath(self.__file_name_comps, is_file=True)

    @property
    def original_image_path(self):
        return self.__original_image_path

    @property
    def width(self):
        return self.__width

    @property
    def height(self):
        return self.__height

    @property
    def new_file_path(self):
        return self.__new_file_path

    def __eq__(self, other):
        return self.__original_image_path == other.original_image_path and self.__width == other.width and self.__height == other.height

    def __hash__(self):
        return hash(self.__file_name_comps)

    @property
    def site(self):
        return self.__site

    @property
    def path(self):
        return self.new_file_path

    @property
    def path_object(self):
        return self.path

    @property
    def id(self):
        return None

    def get_stream(self):
        img = Image.open(self.__original_image_path.abs_path)
        new_img = img.resize((self.width, self.height), Image.BICUBIC)
        bio = BytesIO()
        format = img.format
        new_img.save(bio, format)
        new_img.close()
        img.close()
        del new_img
        del img
        bio.seek(0)
        return bio

    @property
    def mime_type(self):
        mime_type = 'octet/stream'
        path = self.__url.real_path
        type, enc = mimetypes.guess_type(path)
        if type:
            mime_type = type
        return mime_type

    @property
    def content_type(self):
        return ContentContract.types.AUXILIARY

    @property
    def url_object(self):
        if self.__url is None:
            self.__url = _ContentUrl(self.__site, self.__new_file_path)
        return self.__url
