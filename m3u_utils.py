import os
import re
import requests
import hashlib
import time

CACHE_DIR = "m3u_cache"
CACHE_TIMEOUT = 24 * 60 * 60  # 24 horas

def get_cache_filename(url):
    if not os.path.exists(CACHE_DIR):
        os.makedirs(CACHE_DIR)
    return os.path.join(CACHE_DIR, f"{hashlib.md5(url.encode()).hexdigest()}.m3u")

def descargar_m3u(url):
    headers = {'User-Agent': 'Mozilla/5.0'}
    cache_file = get_cache_filename(url)
    if os.path.exists(cache_file):
        cache_time = os.path.getmtime(cache_file)
        if time.time() - cache_time < CACHE_TIMEOUT:
            with open(cache_file, "r", encoding="utf-8") as f:
                return f.read()
    resp = requests.get(url, timeout=30, headers=headers)
    resp.raise_for_status()
    content = resp.text
    with open(cache_file, "w", encoding="utf-8") as f:
        f.write(content)
    return content

def parsear_m3u_completo(contenido_m3u):
    canales = []
    extinf_pattern = re.compile(r'#EXTINF:(-?\d+)\s*(.*?),(.*)')
    attr_pattern = re.compile(r'([\w-]+)="([^"]*)"')
    lines = contenido_m3u.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith('#EXTINF:'):
            match = extinf_pattern.match(line)
            if match:
                duration, attrs_str, name = match.groups()
                canal = {'duration': duration, 'name': name.strip(), 'group': 'Otros', 'attributes': {}}
                attrs = dict(attr_pattern.findall(attrs_str))
                canal['group'] = attrs.get('group-title', canal['group'])
                canal['attributes'] = {k: v for k, v in attrs.items() if k != 'group-title'}
                canal['tvg-id'] = attrs.get('tvg-id', '')
                canal['tvg-name'] = attrs.get('tvg-name', '')
                canal['tvg-logo'] = attrs.get('tvg-logo', '')
                i += 1
                while i < len(lines) and (not lines[i].strip() or lines[i].strip().startswith('#')):
                    i += 1
                if i < len(lines) and lines[i].strip():
                    url = lines[i].strip()
                    if url.startswith('http://') or url.startswith('https://'):
                        canal['url'] = url
                        canales.append(canal)
        i += 1
    return canales

def generar_m3u_filtrado(canales):
    m3u_content = "#EXTM3U\n"
    for canal in canales:
        name = canal.get('name', 'Unknown')
        group = canal.get('group', '')
        url = canal.get('url', '')
        tvg_id = canal.get('tvg-id', '')
        tvg_name = canal.get('tvg-name', '')
        tvg_logo = canal.get('tvg-logo', '')
        if not url:
            continue
        extinf_line = f'#EXTINF:-1'
        if tvg_id: extinf_line += f' tvg-id="{tvg_id}"'
        if tvg_name: extinf_line += f' tvg-name="{tvg_name}"'
        if tvg_logo: extinf_line += f' tvg-logo="{tvg_logo}"'
        if group: extinf_line += f' group-title="{group}"'
        extinf_line += f',{name}\n{url}\n'
        m3u_content += extinf_line
    return m3u_content

def generar_txt(canales):
    txt_content = ""
    for canal in canales:
        name = canal.get('name', 'Unknown')
        group = canal.get('group', '')
        url = canal.get('url', '')
        if not url:
            continue
        txt_content += f"Grupo: {group}, Nombre: {name}, URL: {url}\n"
    return txt_content
