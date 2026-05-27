#!/usr/bin/env python3
"""小米MiMo API - 对话内可直接使用
用法:
  python .workbuddy/mimo.py chat "你的问题"
  python .workbuddy/mimo.py models
  python .workbuddy/mimo.py chat --system "你是助手" "你的问题"
"""
import urllib.request, json, os, sys

API_KEY = os.environ.get("MIMO_API_KEY", "tp-c1nat0poze2d6lv6d8kv83jf9k00xxr92nzzgcnzo3a874ik")
BASE_URL = "https://token-plan-cn.xiaomimimo.com/v1"

def chat(model="mimo-v2.5-pro", prompt="", system=None, max_tokens=2048, temp=0.7):
    msgs = []
    if system: msgs.append({"role":"system","content":system})
    msgs.append({"role":"user","content":prompt})
    data = json.dumps({"model":model,"messages":msgs,"max_completion_tokens":max_tokens,"temperature":temp,"stream":False}).encode()
    req = urllib.request.Request(f"{BASE_URL}/chat/completions", data=data,
        headers={"api-key":API_KEY,"Content-Type":"application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read())

def models():
    req = urllib.request.Request(f"{BASE_URL}/models", headers={"api-key":API_KEY})
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read())

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__); sys.exit(1)
    cmd = sys.argv[1]
    if cmd == "models":
        for m in models().get("data",[]): print(m["id"])
    elif cmd == "chat":
        prompt = sys.argv[-1]
        system = None
        if "--system" in sys.argv:
            si = sys.argv.index("--system")
            system = sys.argv[si+1]
        r = chat(prompt=prompt, system=system)
        print(r["choices"][0]["message"]["content"])
