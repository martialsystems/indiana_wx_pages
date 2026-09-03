#!/usr/bin/env python3
# Copyright (c) 2026 Martial Systems LLC
"""Phone-width 390x844 and desktop 1280x800 overflow check for the console.

  python3 scripts/viewport_sanity.py
"""

from __future__ import annotations

import json
import os
import shutil
import socket
import subprocess
import sys
import tempfile
import threading
import time
import urllib.request
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import List, Optional, Tuple

ROOT = Path(__file__).resolve().parents[1]
PHONE = (390, 844)
DESKTOP = (1280, 800)


class _QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, fmt: str, *args) -> None:
        return


def find_chrome() -> Optional[str]:
    env = os.environ.get("VIEWPORT_SANITY_CHROME", "").strip()
    if env and Path(env).is_file():
        return env
    mac = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    if Path(mac).is_file():
        return mac
    for name in ("google-chrome", "chromium", "chromium-browser"):
        hit = shutil.which(name)
        if hit:
            return hit
    return None


def static_errors() -> List[str]:
    html = (ROOT / "index.html").read_text(encoding="utf-8")
    css = (ROOT / "assets/style.css").read_text(encoding="utf-8")
    errs: List[str] = []
    if 'name="viewport"' not in html:
        errs.append("missing viewport meta")
    if "max-width: 100%" not in css:
        errs.append("img/page CSS missing max-width: 100%")
    if "overflow-x: auto" not in css:
        errs.append("tables missing overflow-x: auto wrap")
    if "width: 3300" in html or 'width="3300"' in html:
        errs.append("CPC GIF baked at native 3300px width")
    if 'class="banner"' in html:
        errs.append("slogan banner still in HTML")
    if "assets/console.js" not in html:
        errs.append("console.js not linked")
    if "data-go=" not in html:
        errs.append("console nav missing data-go")
    js_path = ROOT / "assets/console.js"
    if not js_path.is_file():
        errs.append("missing assets/console.js")
        return errs
    js = js_path.read_text(encoding="utf-8")
    errs.extend(catalog_link_errors(html, css, js))
    tree = ROOT / "trees" / "indiana_freeze_date" / "index.html"
    if not tree.is_file():
        errs.append("missing trees/indiana_freeze_date/index.html")
    else:
        th = tree.read_text(encoding="utf-8")
        if "28941fb" not in th or "mae_bars.png" not in th or "tree-page" not in th:
            errs.append("freeze-date write-up missing SHA, figure, or tree-page class")
        if "trees/indiana_freeze_date/" not in html:
            errs.append("index missing trees/indiana_freeze_date/ href")
    if "nav.rail a" not in css:
        errs.append("CSS missing nav.rail a")
    if "tree-page" not in js:
        errs.append("console.js missing tree-page zoom path")
    return errs


def catalog_link_errors(html: str, css: str, js: str) -> List[str]:
    """GitHub hrefs in catalog/ledger must look like links and must navigate."""
    errs: List[str] = []
    cat_start = html.find('id="catalog"')
    maps_start = html.find('id="maps"')
    catalog = html[cat_start:maps_start] if cat_start >= 0 and maps_start > cat_start else ""
    if cat_start < 0:
        errs.append("catalog panel missing")
    elif 'href="https://github.com' not in catalog:
        errs.append("catalog missing GitHub hrefs")
    if "img.shields.io" in catalog:
        errs.append("catalog GitHub columns turned into shields badges")
    led_start = html.find('id="ledger"')
    nwm_start = html.find('id="nwm"')
    ledger = html[led_start:nwm_start] if led_start >= 0 and nwm_start > led_start else ""
    if led_start >= 0 and 'href="https://github.com' not in ledger:
        errs.append("ledger missing GitHub hrefs")
    if "#catalog a" not in css or "#ledger a" not in css or ".map-card h3 a" not in css:
        errs.append("CSS missing #catalog a / #ledger a / .map-card h3 a")
    block = ""
    idx = css.find("#catalog a")
    if idx >= 0:
        brace = css.find("{", idx)
        end = css.find("}", brace) if brace >= 0 else -1
        if brace >= 0 and end > brace:
            block = css[brace + 1 : end]
    if "underline" not in block:
        errs.append("#catalog a missing text-decoration underline")
    if "#5a2a16" not in block:
        errs.append("#catalog a missing link color #5a2a16")
    if "color: inherit" in block:
        errs.append("#catalog a still color: inherit")
    if 'closest("a[href]")' not in js and "closest('a[href]')" not in js:
        errs.append("console.js missing a[href] closest guard")
    if '"catalog"' not in js:
        errs.append("console.js PANELS missing catalog")
    return errs


def _serve(root: Path) -> Tuple[ThreadingHTTPServer, int]:
    handler = lambda *a, **k: _QuietHandler(*a, directory=str(root), **k)  # noqa: E731
    httpd = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    t = threading.Thread(target=httpd.serve_forever, daemon=True)
    t.start()
    return httpd, int(httpd.server_address[1])


def chrome_catalog_nav(chrome: str, url: str) -> List[str]:
    """#catalog hash shows Catalog; GitHub <a> clicks are not preventDefaulted."""
    errs: List[str] = []
    with tempfile.TemporaryDirectory(prefix="wx-cdp-cat-") as tmp:
        user = Path(tmp) / "profile"
        user.mkdir()
        port = _free_port()
        cmd = [
            chrome,
            "--headless=new",
            "--disable-gpu",
            "--remote-debugging-port={0}".format(port),
            "--user-data-dir={0}".format(user),
            "--window-size=1280,800",
            url,
        ]
        proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        try:
            ws = _wait_page_ws(port, timeout=12.0)
            if not ws:
                return ["no CDP page for catalog nav"]
            data = _cdp_catalog_nav(ws)
            if data is None:
                return ["CDP catalog nav evaluate failed"]
            if not data.get("catOn") or data.get("outOn"):
                errs.append(
                    "#catalog hash did not show catalog panel (catOn={0} outOn={1} href={2} ready={3} body={4})".format(
                        data.get("catOn"),
                        data.get("outOn"),
                        data.get("hrefNow"),
                        data.get("ready"),
                        data.get("bodyLen"),
                    )
                )
            if not data.get("hasA") or "github.com" not in str(data.get("href") or ""):
                errs.append("catalog GitHub <a href> missing in live DOM")
            color = str(data.get("color") or "")
            if "90, 42, 22" not in color and "90,42,22" not in color:
                errs.append("catalog <a> computed color is not #5a2a16 ({0})".format(color))
            deco = str(data.get("deco") or "").lower()
            if "underline" not in deco:
                errs.append("catalog <a> computed text-decoration is not underline ({0})".format(deco))
            if not data.get("slugCovered"):
                errs.append("code.slug is not inside a[href]")
            if data.get("prevented") is True:
                errs.append("click on catalog GitHub link (or slug) was preventDefaulted")
            if data.get("panelAfterLink") and data.get("panelAfterLink") != "catalog":
                errs.append(
                    "catalog GitHub click switched panel to {0}".format(data.get("panelAfterLink"))
                )
            if data.get("panelAfterRow") not in (None, "maps"):
                errs.append(
                    "non-link catalog row click did not open maps ({0})".format(
                        data.get("panelAfterRow")
                    )
                )
            elif data.get("hasOpenMap") and data.get("panelAfterRow") != "maps":
                errs.append("non-link catalog row click did not open maps")
        finally:
            proc.terminate()
            try:
                proc.wait(timeout=3)
            except subprocess.TimeoutExpired:
                proc.kill()
    return errs


def chrome_same_origin_width(chrome: str, url: str, width: int, height: int) -> List[str]:
    errs: List[str] = []
    with tempfile.TemporaryDirectory(prefix="wx-cdp-") as tmp:
        user = Path(tmp) / "profile"
        user.mkdir()
        port = _free_port()
        cmd = [
            chrome,
            "--headless=new",
            "--disable-gpu",
            "--remote-debugging-port={0}".format(port),
            "--user-data-dir={0}".format(user),
            "--window-size={0},{1}".format(width, height),
            url,
        ]
        proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        try:
            ws = _wait_page_ws(port, timeout=12.0)
            if not ws:
                return ["no CDP page at {0}x{1}".format(width, height)]
            # Minimal: HTTP /json/runtime is not a thing. Use websocket.
            sw, iw = _cdp_widths(ws)
            if sw is None or iw is None:
                return ["CDP evaluate failed at {0}x{1}".format(width, height)]
            if sw < 0:
                return ["outlook, ledger, or CPC images missing at {0}x{1}".format(width, height)]
            # Allow 1px subpixel plus the classic overlay scrollbar on some engines.
            slack = 16
            if sw > iw + slack:
                errs.append(
                    "horizontal overflow at {0}x{1}: scrollWidth {2} innerWidth {3}".format(
                        width, height, sw, iw
                    )
                )
        finally:
            proc.terminate()
            try:
                proc.wait(timeout=3)
            except subprocess.TimeoutExpired:
                proc.kill()
    return errs


def chrome_tree_overflow(chrome: str, url: str, width: int, height: int) -> List[str]:
    errs: List[str] = []
    with tempfile.TemporaryDirectory(prefix="wx-cdp-tree-") as tmp:
        user = Path(tmp) / "profile"
        user.mkdir()
        port = _free_port()
        cmd = [
            chrome,
            "--headless=new",
            "--disable-gpu",
            "--remote-debugging-port={0}".format(port),
            "--user-data-dir={0}".format(user),
            "--window-size={0},{1}".format(width, height),
            url,
        ]
        proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        try:
            ws = _wait_page_ws(port, timeout=12.0)
            if not ws:
                return ["no CDP page for freeze-date write-up at {0}x{1}".format(width, height)]
            data = _cdp_tree_page(ws)
            if data is None:
                return ["CDP freeze-date evaluate failed at {0}x{1}".format(width, height)]
            if not data.get("writeup") or int(data.get("img") or 0) < 2:
                return [
                    "freeze-date write-up or figures missing at {0}x{1}".format(width, height)
                ]
            sw, iw = int(data.get("sw") or 0), int(data.get("iw") or 0)
            if sw > iw + 16:
                errs.append(
                    "freeze-date overflow at {0}x{1}: scrollWidth {2} innerWidth {3}".format(
                        width, height, sw, iw
                    )
                )
        finally:
            proc.terminate()
            try:
                proc.wait(timeout=3)
            except subprocess.TimeoutExpired:
                proc.kill()
    return errs


def _cdp_tree_page(ws_url: str):
    try:
        cdp = _Cdp(ws_url)
        cdp.call("Page.enable")
        cdp.call("Runtime.enable")
        cdp.call("Page.reload", {"ignoreCache": True})
        time.sleep(0.4)
        result = cdp.call(
            "Runtime.evaluate",
            {
                "expression": (
                    "(async () => {"
                    " const imgs=[...document.images];"
                    " await Promise.all(imgs.map(img => img.complete ? 1 : new Promise(r => { img.onload=r; img.onerror=r; })));"
                    " return {sw: document.documentElement.scrollWidth, iw: window.innerWidth,"
                    " writeup: !!document.getElementById('writeup'),"
                    " img: imgs.length};"
                    "})()"
                ),
                "awaitPromise": True,
                "returnByValue": True,
            },
        )
        cdp.close()
        value = result.get("result", {}).get("value")
        if isinstance(value, dict):
            return value
        if isinstance(value, str):
            return json.loads(value)
        return None
    except Exception:
        return None


def _free_port() -> int:
    sock = socket.socket()
    sock.bind(("127.0.0.1", 0))
    port = int(sock.getsockname()[1])
    sock.close()
    return port


def _wait_page_ws(port: int, timeout: float) -> Optional[str]:
    deadline = time.time() + timeout
    list_url = "http://127.0.0.1:{0}/json/list".format(port)
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(list_url, timeout=1) as resp:
                pages = json.loads(resp.read().decode("utf-8"))
            if isinstance(pages, list):
                for page in pages:
                    ws = page.get("webSocketDebuggerUrl") or ""
                    if ws and page.get("type") in (None, "page"):
                        return ws
        except (OSError, ValueError):
            time.sleep(0.15)
            continue
        time.sleep(0.15)
    return None


def _cdp_widths(ws_url: str) -> Tuple[Optional[int], Optional[int]]:
    try:
        cdp = _Cdp(ws_url)
        cdp.call("Page.enable")
        cdp.call("Runtime.enable")
        cdp.call("Page.reload", {"ignoreCache": True})
        time.sleep(0.4)
        result = cdp.call(
            "Runtime.evaluate",
            {
                "expression": (
                    "(async () => {"
                    " const imgs=[...document.images];"
                    " await Promise.all(imgs.map(img => img.complete ? 1 : new Promise(r => { img.onload=r; img.onerror=r; })));"
                    " return {sw: document.documentElement.scrollWidth, iw: window.innerWidth,"
                    " outlook: !!document.getElementById('outlook'),"
                    " ledger: !!document.getElementById('ledger'),"
                    " img: imgs.length};"
                    "})()"
                ),
                "awaitPromise": True,
                "returnByValue": True,
            },
        )
        cdp.close()
        value = result.get("result", {}).get("value")
        if isinstance(value, str):
            data = json.loads(value)
        elif isinstance(value, dict):
            data = value
        else:
            return None, None
        if not data.get("outlook") or not data.get("ledger") or int(data.get("img") or 0) < 2:
            return -1, int(data.get("iw") or 0)
        return int(data["sw"]), int(data["iw"])
    except Exception:
        return None, None


def _cdp_catalog_nav(ws_url: str):
    try:
        cdp = _Cdp(ws_url)
        cdp.call("Page.enable")
        cdp.call("Runtime.enable")
        cdp.call("Page.reload", {"ignoreCache": True})
        time.sleep(0.6)
        result = cdp.call(
            "Runtime.evaluate",
            {
                "expression": (
                    "(async () => {"
                    " const waitFor = async (fn) => {"
                    "  const t = Date.now() + 4000;"
                    "  while (Date.now() < t) { if (fn()) return true; await new Promise(r => setTimeout(r, 50)); }"
                    "  return !!fn();"
                    " };"
                    " await waitFor(() => !!document.getElementById('catalog'));"
                    " location.hash = 'outlook';"
                    " await new Promise(r => setTimeout(r, 60));"
                    " location.hash = 'catalog';"
                    " await waitFor(() => {"
                    "  const el = document.querySelector('[data-panel=\"catalog\"]');"
                    "  return !!(el && el.classList.contains('is-on'));"
                    " });"
                    " const cat = document.querySelector('[data-panel=\"catalog\"]');"
                    " const out = document.querySelector('[data-panel=\"outlook\"]');"
                    " const catOn = !!(cat && cat.classList.contains('is-on'));"
                    " const outOn = !!(out && out.classList.contains('is-on'));"
                    " const hrefAfterHash = String(location.href);"
                    " const a = document.querySelector('#catalog a[href*=\"github.com\"]');"
                    " const slug = a && a.querySelector('code.slug');"
                    " const cs = a ? getComputedStyle(a) : {};"
                    " let prevented = null;"
                    " let panelAfterLink = null;"
                    " if (a) {"
                    "  const hit = slug || a;"
                    "  const spy = function (e) {"
                    "   prevented = e.defaultPrevented;"
                    "   const on = document.querySelector('[data-panel].is-on');"
                    "   panelAfterLink = on ? on.getAttribute('data-panel') : null;"
                    "   e.preventDefault();"
                    "  };"
                    "  document.addEventListener('click', spy);"
                    "  hit.dispatchEvent(new MouseEvent('click', {bubbles:true, cancelable:true, view:window}));"
                    "  document.removeEventListener('click', spy);"
                    " }"
                    " let panelAfterRow = null;"
                    " const tr = document.querySelector('#catalog tr[data-open-map]');"
                    " const hasOpenMap = !!tr;"
                    " if (tr) {"
                    "  const cell = [...tr.children].find(td => !td.querySelector('a'));"
                    "  if (cell) {"
                    "   const spy2 = function (e) { e.preventDefault(); };"
                    "   document.addEventListener('click', spy2);"
                    "   cell.dispatchEvent(new MouseEvent('click', {bubbles:true, cancelable:true, view:window}));"
                    "   document.removeEventListener('click', spy2);"
                    "   const on = document.querySelector('[data-panel].is-on');"
                    "   panelAfterRow = on ? on.getAttribute('data-panel') : null;"
                    "  }"
                    " }"
                    " return {catOn: catOn, outOn: outOn,"
                    "  hasA: !!a, href: a ? (a.getAttribute('href') || '') : '',"
                    "  color: cs.color || '', deco: (cs.textDecorationLine || cs.textDecoration || ''),"
                    "  slugCovered: !!(slug && slug.closest('a[href]')),"
                    "  prevented, panelAfterLink, panelAfterRow, hasOpenMap,"
                    "  hrefNow: hrefAfterHash, ready: document.readyState,"
                    "  bodyLen: document.body ? document.body.innerHTML.length : -1};"
                    "})()"
                ),
                "awaitPromise": True,
                "returnByValue": True,
            },
        )
        cdp.close()
        value = result.get("result", {}).get("value")
        if isinstance(value, dict):
            return value
        if isinstance(value, str):
            return json.loads(value)
        return None
    except Exception:
        return None


class _Cdp:
    def __init__(self, ws_url: str) -> None:
        import base64
        import hashlib
        import struct

        if not ws_url.startswith("ws://"):
            raise RuntimeError("only ws:// CDP")
        rest = ws_url[5:]
        hostport, _, path = rest.partition("/")
        path = "/" + path
        host, _, port_s = hostport.partition(":")
        port = int(port_s or "80")
        sock = socket.create_connection((host, port), timeout=20)
        key = base64.b64encode(os.urandom(16)).decode("ascii")
        req = (
            "GET {0} HTTP/1.1\r\n"
            "Host: {1}:{2}\r\n"
            "Upgrade: websocket\r\n"
            "Connection: Upgrade\r\n"
            "Sec-WebSocket-Key: {3}\r\n"
            "Sec-WebSocket-Version: 13\r\n"
            "\r\n"
        ).format(path, host, port, key)
        sock.sendall(req.encode("ascii"))
        hdr = b""
        while b"\r\n\r\n" not in hdr:
            chunk = sock.recv(4096)
            if not chunk:
                raise RuntimeError("CDP handshake closed")
            hdr += chunk
        if b"101" not in hdr.split(b"\r\n", 1)[0]:
            raise RuntimeError("CDP handshake failed")
        leftover = hdr.split(b"\r\n\r\n", 1)[1]
        sock.settimeout(20)
        self._sock = sock
        self._buf = leftover
        self._next = 1
        self._struct = struct

    def _send(self, payload: bytes) -> None:
        mask = os.urandom(4)
        n = len(payload)
        hdr = bytearray([0x81])
        if n < 126:
            hdr.append(0x80 | n)
        elif n < 65536:
            hdr.append(0x80 | 126)
            hdr.extend(self._struct.pack("!H", n))
        else:
            hdr.append(0x80 | 127)
            hdr.extend(self._struct.pack("!Q", n))
        hdr.extend(mask)
        masked = bytes(b ^ mask[i % 4] for i, b in enumerate(payload))
        self._sock.sendall(bytes(hdr) + masked)

    def _recv_frame(self) -> bytes:
        while True:
            if len(self._buf) < 2:
                chunk = self._sock.recv(4096)
                if not chunk:
                    raise RuntimeError("CDP closed")
                self._buf += chunk
                continue
            b0, b1 = self._buf[0], self._buf[1]
            ln = b1 & 0x7F
            idx = 2
            if ln == 126:
                if len(self._buf) < 4:
                    self._buf += self._sock.recv(4096)
                    continue
                ln = self._struct.unpack("!H", self._buf[2:4])[0]
                idx = 4
            elif ln == 127:
                if len(self._buf) < 10:
                    self._buf += self._sock.recv(4096)
                    continue
                ln = self._struct.unpack("!Q", self._buf[2:10])[0]
                idx = 10
            need = idx + ln
            while len(self._buf) < need:
                chunk = self._sock.recv(4096)
                if not chunk:
                    raise RuntimeError("CDP closed mid-frame")
                self._buf += chunk
            data = self._buf[idx:need]
            self._buf = self._buf[need:]
            opcode = b0 & 0x0F
            if opcode in (0x1, 0x2):
                return data

    def call(self, method: str, params=None) -> dict:
        mid = self._next
        self._next += 1
        msg = {"id": mid, "method": method}
        if params:
            msg["params"] = params
        self._send(json.dumps(msg, separators=(",", ":")).encode("utf-8"))
        deadline = time.time() + 20
        while time.time() < deadline:
            raw = self._recv_frame()
            data = json.loads(raw.decode("utf-8"))
            if data.get("id") == mid:
                if "error" in data:
                    raise RuntimeError("{0}: {1}".format(method, data["error"]))
                return data.get("result") or {}
        raise RuntimeError("CDP timeout {0}".format(method))

    def close(self) -> None:
        try:
            self._sock.close()
        except OSError:
            pass


def main() -> int:
    errs = static_errors()
    chrome = find_chrome()
    httpd = None
    if chrome:
        httpd, port = _serve(ROOT)
        url = "http://127.0.0.1:{0}/index.html".format(port)
        try:
            for w, h in (PHONE, DESKTOP):
                errs.extend(chrome_same_origin_width(chrome, url, w, h))
            errs.extend(chrome_catalog_nav(chrome, url + "#catalog"))
            tree_url = "http://127.0.0.1:{0}/trees/indiana_freeze_date/".format(port)
            for w, h in (PHONE, DESKTOP):
                errs.extend(chrome_tree_overflow(chrome, tree_url, w, h))
        finally:
            httpd.shutdown()
    else:
        errs.append("Chrome not found; static CSS checks only")
    if errs:
        print("FAIL")
        for e in errs:
            print(" ", e)
        # Chrome-missing is residual, not a hard fail if static is clean.
        hard = [e for e in errs if not e.startswith("Chrome not found")]
        if hard:
            return 2
        print("static ok; Chrome missing")
        return 0
    print("PASS 390x844 and 1280x800")
    return 0


if __name__ == "__main__":
    sys.exit(main())
