import io
import uuid

import pytest
from httpx import HTTPStatusError

from solid.solid_api import SolidAPI
from solid.utils.api_util import append_slashes_at_end


def gen_random_str() -> str:
    return uuid.uuid4().hex


def test_folder():
    base_url = 'https://dahanhsi.solidcommunity.net/'
    folder_name = 'testfolder-' + gen_random_str()
    url = base_url + folder_name + '/'

    api = SolidAPI(None)
    api.create_folder(url)
    assert api.item_exists(url)
    api.delete_folder(url)

    with pytest.raises(Exception):
        api.delete_folder(base_url)


def test_read_folder():
    base_url = 'https://dahanhsi.solidcommunity.net/'
    folder_name = 'testfolder'
    url = base_url + folder_name + '/'

    body = '#hello Solid!'
    f = io.BytesIO(body.encode('UTF-8'))
    file_name = 'test.md'
    file_url = url + file_name

    sub_folder_name = 'subfolder'
    sub_folder_url = url + sub_folder_name + '/'

    api = SolidAPI(None)

    try:
        api.delete(file_url)
    except HTTPStatusError as e:
        if e.response.status_code != 404:
            raise e

    try:
        api.delete(sub_folder_url)
    except HTTPStatusError as e:
        if e.response.status_code != 404:
            raise e

    try:
        api.delete(url)
    except HTTPStatusError as e:
        if e.response.status_code != 404:
            raise e

    api.create_folder(url)

    # empty folder
    folder_data = api.read_folder(url)
    assert folder_data.name == folder_name
    assert len(folder_data.folders) == 0
    assert len(folder_data.files) == 0
    assert folder_data.url == url
    assert folder_data.parent == append_slashes_at_end(base_url)
    assert folder_data.type == 'folder'
    # assert folder_data.links == None # TODO

    # folder with subdir and file
    api.create_folder(sub_folder_url)
    api.put_file(file_url, f, 'text/markdown')

    folder_data = api.read_folder(url)
    assert len(folder_data.folders) == 1
    assert len(folder_data.files) == 1
    file_item, sub_folder_item = folder_data.files[0], folder_data.folders[0]

    assert sub_folder_item.itemType == 'Container'
    assert sub_folder_item.url == sub_folder_url
    assert sub_folder_item.name == sub_folder_name
    # assert sub_folder_item.links = None # TODO
    assert sub_folder_item.parent == url

    assert file_item.itemType == 'Resource'
    assert file_item.url == file_url
    assert file_item.name == file_name
    # assert file_item.links == None # TODO
    assert file_item.parent == url


def test_file():
    url = 'https://dahanhsi.solidcommunity.net/public/test.md.' + gen_random_str()
    api = SolidAPI(None)

    assert not api.item_exists(url)
    with pytest.raises(HTTPStatusError) as e:
        api.get(url)
    assert e.value.response.status_code == 404

    # create
    body = '#hello Solid!'
    f = io.BytesIO(body.encode('UTF-8'))
    api.put_file(url, f, 'text/markdown')

    # retrieve
    assert api.item_exists(url)
    resp = api.get(url)
    assert resp.text == body

    # delete
    api.delete(url)
