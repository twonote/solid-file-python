from enum import Enum
from typing import List
import re


class LINK(Enum):
    CONTAINER = '<http://www.w3.org/ns/ldp#BasicContainer>; rel="type"'
    RESOURCE = '<http://www.w3.org/ns/ldp#Resource>; rel="type"'


def append_slashes_at_end(url) -> str:
    if url[-1] != '/':
        url += '/'
    return url


def remove_slashes_at_end(url) -> str:
    if url[-1] == '/':
        url = url[:-1]
    return url


def get_root_url(url: str) -> str:
    slash_count = 0
    for i in range(len(url)):
        if url[i] == '/':
            slash_count += 1
        if slash_count == 3:
            break

    if slash_count == 3:
        return url[:i + 1]
    else:
        return append_slashes_at_end(url)


def get_parent_url(url) -> str:
    url = remove_slashes_at_end(url)

    if url.count('/') == 2:  # is base url, no parent url, return it self
        return append_slashes_at_end(url)

    i = url.rindex('/')
    return url[:i + 1]


def get_item_name(url) -> str:
    url = remove_slashes_at_end(url)

    if url.count('/') == 2:  # is base url, no item name
        return ''

    i = url.rindex('/')
    return url[i + 1:]


def are_folders(urls: List) -> bool:
    pass


def are_files(urls: List) -> bool:
    pass

def get_links_from_response(response) -> dict:
    link_header = response.headers.get('link')
    if (not link_header) or (link_header == ''):
        return {}
    else:
        return parse_link_header(link_header, response.url)

def parse_link_header(link_header: str, item_url) -> dict:
    link_dict = {}
    link_header_list = parse_link_header_to_array(link_header)
    if len(link_header_list) > 0:
        for link in link_header_list:
            url = link[link.index('<')+ 1:link.index('>')]
            original_rel = link[link.index('rel="')+ 5:link.rindex('"')]
            if (original_rel.lower() == 'describedby'):
                rel = 'meta'
            else:
                rel = original_rel

            if rel in ['meta', 'acl']:
                link_dict[rel] = url_join(url, item_url)
    
    return link_dict

def parse_link_header_to_array(link_header: str) -> list:
    if (not link_header): return
    linkexp = '<[^>]*>\s*(\s*;\s*[^()<>@,;:"/[\]?={} \t]+=(([^\(\)<>@,;:"\/\[\]\?={} \t]+)|("[^"]*")))*(,|$)'
    match = re.finditer(linkexp, link_header)
    links = [x.group() for x in match]
    return links

def url_join(given, base):
  base = str(base)
  base_hash = base.find('#')
  if (base_hash > 0):
    base = base[0:base_hash]

  if (len(given) == 0):
    return base

  if (given.find('#') == 0):
    return base + given
  
  colon = given.find(':')
  if (colon >= 0) :
    return given
  
  base_colon = base.find(':')
  if (len(base) == 0) :
    return given
  
  if (base_colon < 0) :
    return given
  
  if (+ base_colon + 1):
      end_index = +base_colon + 1
  else:
      end_index = 9e9

  base_scheme = base[:end_index]
  if (given.find('//') == 0) :
    return base_scheme + given
  
  if (base.find('//', base_colon) == base_colon + 1):
    base_single = base.find('/', base_colon + 3)
    if (base_single < 0):
      if (len(base) - base_colon - 3 > 0):
        return base + '/' + given
      else:
        return base_scheme + given
      
  else:
    base_single = base.find('/', base_colon + 1)
    if (base_single < 0):
      if (len(base) - base_colon - 1 > 0) :
        return base + '/' + given
      else:
        return base_scheme + given
      
  if (given.find('/') == 0) :
    return base[:base_single] + given

  path = base[base_single:]
  try:
    last_slash = path.rindex('/')
  except:
    return base_scheme + given
  
  if (last_slash >= 0 and last_slash < len(path) - 1) :
    if (+last_slash + 1):
        end_index = +last_slash + 1
    else:
        end_index = 9e9
    path = path[:end_index]

  path += given
  while (re.match("[^\/]*\/\.\.\/", path)) :
    path = re.sub("[^\/]*\/\.\.\/", '', path, 1)
  
  path = re.sub("\.\/", '', path)
  path = re.sub("\/\.$", '/', path)
  return base[:base_single] + path

