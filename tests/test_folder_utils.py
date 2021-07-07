from solid.utils.folder_utils import parse_folder_response
import httpx


def test_parse_folder_response():
    url = 'https://dahanhsi.solidcommunity.net/test/'
    resp = httpx.get(url)
    fold_data = parse_folder_response(resp, url)
    pass
