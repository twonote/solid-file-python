from httpx import Response

from rdflib import Namespace, Graph, URIRef, RDF

from solid.utils.api_util import get_item_name, get_parent_url

LDP = Namespace("http://www.w3.org/ns/ldp#")
container_types = [URIRef('http://www.w3.org/ns/ldp#Container'), URIRef('http://www.w3.org/ns/ldp#BasicContainer')]


# FIXME
# def parse_folder_response(folder_response: Response, url) -> FolderData:
def parse_folder_response(folder_response: Response, url):
    return _parse_folder_response(folder_response.text, url)


def _parse_folder_response(text, url):
    from solid.solid_api import FolderData, Item

    g = Graph().parse(data=text, publicID=url, format='turtle')

    def is_type(sub, type) -> bool:
        return (sub, RDF.type, type) in g

    def is_container(sub) -> bool:
        for ct in container_types:
            if is_type(sub, ct):
                return True
        return False

    this = URIRef(url)

    if not is_container(this):
        raise Exception('Not a container.')

    folders, files = [], []

    for obj in g.objects(this, LDP.contains):
        item_url = str(obj)
        item = Item()
        item.parent = get_parent_url(item_url)
        item.links = None  # TODO
        item.name = get_item_name(item_url)
        item.url = item_url
        item.itemType = 'Container' if is_container(obj) else 'Resource'

        cat = folders if is_container(obj) else files
        cat.append(item)

    ret = FolderData()
    ret.url = url
    ret.name = get_item_name(url)
    ret.parent = get_parent_url(url)
    ret.links = None  # TODO
    ret.folders = folders
    ret.files = files

    return ret
