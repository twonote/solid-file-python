from enum import Enum
from typing import Optional, Union, Dict, Callable, Iterable, AsyncIterable, List

import httpx
from httpx import Response, HTTPStatusError

from solid.auth import Auth
from solid.utils.api_util import get_root_url, LINK, get_parent_url, get_item_name
from solid.utils.folder_utils import parse_folder_response


class MERGE(Enum):
    REPLACE = 'replace'
    KEEP_SOURCE = 'keep_source'
    KEEP_TARGET = 'keep_target'


class LINKS(Enum):
    EXCLUDE = 'exclude'
    INCLUDE = 'include'
    INCLUDE_POSSIBLE = 'include_possible'


class AGENT(Enum):
    NO_MODIFY = 'no_modify'
    TO_TARGET = 'to_target'
    TO_SOURCE = 'to_source'


class WriteOptions:
    def __init__(self, create_path: bool = True, with_acl: bool = True, agent: AGENT = AGENT.NO_MODIFY,
                 with_meta: bool = True, merge: MERGE = MERGE.REPLACE):
        self.create_path: bool = create_path
        self.with_acl: bool = with_acl
        self.agent: AGENT = agent
        self.with_meta: bool = with_meta
        self.merge: MERGE = merge


class ReadFolderOptions:
    def __init__(self):
        self.links: LINKS = LINKS.EXCLUDE.value


class SolidAPIOptions:
    def __init__(self):
        self.enable_logging: bool = False


class Links:
    def __init__(self):
        self.acl = None
        self.meta = None


class Item:
    def __init__(self):
        self.url = None
        self.name = None
        self.parent = None
        self.itemType = None  # "Container" | "Resource"
        self.links: Optional[Links] = None


class FolderData:
    def __init__(self):
        self.url = None
        self.name = None
        self.parent = None
        self.links: Links = None
        self.type = 'folder'
        self.folders: List[Item] = None
        self.files: List[Item] = None


RequestContent = Union[str, bytes, Iterable[bytes], AsyncIterable[bytes]]


class SolidAPI:
    def __init__(self, auth=None):
        if not auth:
            auth = Auth()
        self.auth = auth

    def fetch(self, method, url, options: Dict = None) -> Response:
        if not options:
            options = {}
        # options['verify'] = False

        r = self.auth.client.request(method, url, **options)
        # r= httpx.request(method, url, **options)
        r.raise_for_status()
        return r

    def get(self, url, options: Dict = None) -> Response:
        return self.fetch('GET', url, options)

    def delete(self, url, options: Dict = None) -> Response:
        return self.fetch('DELETE', url, options)

    def post(self, url, options: Dict = None) -> Response:
        return self.fetch('POST', url, options)

    def put(self, url, options: Dict = None) -> Response:
        return self.fetch('PUT', url, options)

    def patch(self, url, options: Dict = None) -> Response:
        return self.fetch('PATCH', url, options)

    def head(self, url, options: Dict = None) -> Response:
        return self.fetch('HEAD', url, options)

    def option(self, url, options: Dict = None) -> Response:
        return self.fetch('OPTION', url, options)

    def item_exists(self, url) -> bool:
        try:
            self.head(url)
            return True
        except HTTPStatusError as e:
            if e.response.status_code == 404:
                return False
            else:
                raise e

    def post_item(self, url, content: RequestContent, content_type, link: LINK,
                  options: WriteOptions = WriteOptions(create_path=True)) -> Response:
        parent_url = get_parent_url(url)

        if options.create_path:
            self.create_folder(parent_url)

        request_options = {
            'headers': {
                'Link': link.value,
                'Slug': get_item_name(url),
                'Content-Type': content_type,
            },
            'content': content
        }

        return self.post(parent_url, request_options)

    def create_folder(self, url, options: WriteOptions = WriteOptions(merge=MERGE.KEEP_TARGET)) -> Response:
        if url[-1] != '/':
            raise Exception(f'Cannot use createFolder to create a file : ${url}')

        try:
            res = self.head(url)
            if options.merge != MERGE.REPLACE:
                return res
            self.delete_folder(url, recursive=True)
        except HTTPStatusError as e:
            if e.response.status_code == 404:
                pass
            else:
                raise e

        return self.post_item(url, '', 'text/turtle', LINK.CONTAINER, options)

    def post_file(self, url, content: RequestContent, content_type, options: WriteOptions = None) -> Response:
        if url[-1] == '/':
            raise Exception(f'Cannot use postFile to create a folder : ${url}')
        return self.post_item(url, content, content_type, LINK.RESOURCE, options)

    def create_file(self, url, content: RequestContent, content_type, options: WriteOptions = None) -> Response:
        return self.post_file(url, content, content_type, options)

    """
    files
    Support upload file, get/delete in higher level api
    """

    def put_file(self, url, content: RequestContent, content_type, options: WriteOptions = WriteOptions()) -> Response:
        if url[-1] == '/':
            raise Exception(f'Cannot use putFile to create a folder : {url}')

        if options.merge == MERGE.KEEP_TARGET and self.item_exists(url):
            raise Exception(f'File already existed: {url}')

        request_options = {
            'headers': {
                'Link': LINK.RESOURCE.value,
                'Content-Type': content_type,
            },
            'content': content
        }

        return self.put(url, request_options)

    def patch_file(self, url, patch_content, patch_content_type) -> Response:
        raise Exception('Not implemented')

    def read_folder(self, url, options: ReadFolderOptions = ReadFolderOptions()) -> FolderData:
        if url[-1] != '/':
            url += '/'

        folder_res = self.get(url, {'headers': {'Accept': 'text/turtle'}})
        parsed_folder = parse_folder_response(folder_res, url)

        if options.links in (LINKS.INCLUDE_POSSIBLE, LINKS.INCLUDE):
            raise Exception('Not implemented')

        return parsed_folder

    def get_item_links(self, url, options: Dict = None) -> Response:
        raise Exception('Not implemented')

    def copy_file(self, _from, to, options: WriteOptions = None) -> Response:
        raise Exception('Not implemented')

    def copy_meta_file_for_item(self, old_target_file, new_target_file, options: WriteOptions = None) -> Response:
        raise Exception('Not implemented')

    def copy_acl_file_for_item(self, old_target_file, new_target_file, options: WriteOptions = None) -> Response:
        raise Exception('Not implemented')

    def copy_links_for_item(self, old_target_file, new_target_file, options: WriteOptions = None) -> List[Response]:
        raise Exception('Not implemented')

    def copy_folder(self, _from, to, options: WriteOptions = None) -> List[Response]:
        raise Exception('Not implemented')

    def copy(self, _from, to, options: WriteOptions = None) -> List[Response]:
        raise Exception('Not implemented')

    def delete_folder(self, url, recursive=False) -> List[Response]:
        if recursive:
            raise Exception('Not implemented')

        if url == get_root_url(url):
            raise Exception('405 Pod cannot be deleted')
        return [self.delete(url)]

    def move(self, _from, to, copy_options: WriteOptions = None) -> List[Response]:
        raise Exception('Not implemented')

    def rename(self, url, new_name, move_options: WriteOptions = None) -> List[Response]:
        raise Exception('Not implemented')
