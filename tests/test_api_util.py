import pytest

from solid.utils.api_util import remove_slashes_at_end, get_root_url, get_parent_url, get_item_name


def test_remove_slashes_at_end():
    assert remove_slashes_at_end('http://pod.com/xxx/xxx/') == 'http://pod.com/xxx/xxx'
    assert remove_slashes_at_end('http://pod.com/xxx/xxx') == 'http://pod.com/xxx/xxx'


def test_get_root_url():
    assert get_root_url('http://pod.com/folder/file') == 'http://pod.com/'
    assert get_root_url('http://pod.com/folder/') == 'http://pod.com/'
    assert get_root_url('http://pod.com/folder') == 'http://pod.com/'
    assert get_root_url('http://pod.com/') == 'http://pod.com/'
    assert get_root_url('http://pod.com') == 'http://pod.com/'


def test_get_parent_url():
    assert get_parent_url('http://pod.com/folder/file') == 'http://pod.com/folder/'
    assert get_parent_url('http://pod.com/folder/') == 'http://pod.com/'
    assert get_parent_url('http://pod.com/folder') == 'http://pod.com/'
    assert get_parent_url('http://pod.com/') == 'http://pod.com/'
    assert get_parent_url('http://pod.com') == 'http://pod.com/'


def test_get_item_name():
    assert get_item_name('http://pod.com/folder/file') == 'file'
    assert get_item_name('http://pod.com/folder/') == 'folder'
    assert get_item_name('http://pod.com/folder') == 'folder'
    assert get_item_name('http://pod.com/') == ''
    assert get_item_name('http://pod.com') == ''


@pytest.mark.skip
def test_are_folders():
    assert False


@pytest.mark.skip
def test_are_files():
    assert False
