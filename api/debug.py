"""TEMPORARY diagnostic endpoint -> GET /api/debug. Delete after debugging."""

import json
import os
import sys
import traceback
from http.server import BaseHTTPRequestHandler


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        info = {"python": sys.version}
        here = os.path.dirname(os.path.abspath(__file__))
        root = os.path.dirname(here)
        info["__file__"] = os.path.abspath(__file__)
        info["cwd"] = os.getcwd()
        info["api_dir"] = here
        info["root_dir"] = root
        for label, path in (("ls_api_dir", here), ("ls_root_dir", root), ("ls_cwd", os.getcwd())):
            try:
                info[label] = sorted(os.listdir(path))
            except Exception as exc:
                info[label] = f"ERR: {exc}"
        info["sys_path_head"] = sys.path[:6]

        sys.path.insert(0, root)
        for mod in ("config", "llm", "knowledge_base", "agents"):
            try:
                __import__(mod)
                info[f"import_{mod}"] = "OK"
            except Exception:
                info[f"import_{mod}"] = traceback.format_exc()

        body = json.dumps(info, indent=2).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.end_headers()
        self.wfile.write(body)
