from solid.utils.folder_utils import _parse_folder_response

TEXT = '''
@prefix : <#>.
@prefix dct: <http://purl.org/dc/terms/>.
@prefix ldp: <http://www.w3.org/ns/ldp#>.
@prefix stat: <http://www.w3.org/ns/posix/stat#>.
@prefix xsd: <http://www.w3.org/2001/XMLSchema#>.
@prefix test: <>.
@prefix sub: <subdir/>.
@prefix jpeg: <http://www.w3.org/ns/iana/media-types/image/jpeg#>.
@prefix tur: <http://www.w3.org/ns/iana/media-types/text/turtle#>.
@prefix m: <http://www.w3.org/ns/iana/media-types/text/markdown#>.

test:
    a ldp:BasicContainer, ldp:Container;
    dct:modified "2021-07-06T03:24:55Z"^^xsd:dateTime;
    ldp:contains <picture.jpg>, <picture.jpg2>, test:qq, sub:, <testfile.md>;
    stat:mtime 1625541895.566;
    stat:size 4096.
<picture.jpg>
    a jpeg:Resource, ldp:Resource;
    dct:modified "2021-06-24T02:47:10Z"^^xsd:dateTime;
    stat:mtime 1624502830.078;
    stat:size 412944.
<picture.jpg2>
    a jpeg:Resource, ldp:Resource;
    dct:modified "2021-07-05T03:49:57Z"^^xsd:dateTime;
    stat:mtime 1625456997.73;
    stat:size 0.
test:qq
    a tur:Resource, ldp:Resource;
    dct:modified "2021-06-22T11:08:50Z"^^xsd:dateTime;
    stat:mtime 1624360130.12;
    stat:size 0.
sub:
    a ldp:BasicContainer, ldp:Container, ldp:Resource;
    dct:modified "2021-07-06T03:24:55Z"^^xsd:dateTime;
    stat:mtime 1625541895.566;
    stat:size 4096.
<testfile.md>
    a m:Resource, ldp:Resource;
    dct:modified "2021-06-22T10:00:07Z"^^xsd:dateTime;
    stat:mtime 1624356007.481;
    stat:size 44.
'''

URL = 'https://tim.solidcommunity.net/test/'


def test_parse_folder_response():
    fold_data = _parse_folder_response(TEXT, URL)
    # TODO: assert result
    pass
