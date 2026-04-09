import requests
import json

# 源JSON地址
JSON_URL = "https://github.com/proxygenerator1/ProxyGenerator/raw/refs/heads/main/ALL/all.json"
OUTPUT_FILE = "mihomo_all_json_config.yaml"

def main():
    # 开启重定向跟随
    try:
        resp = requests.get(JSON_URL, timeout=15, allow_redirects=True)
        resp.raise_for_status()
        print("✅ JSON下载成功")
        raw_text = resp.text
        print(f"📄 JSON前500字符预览: {raw_text[:500]}")
        data = json.loads(raw_text)
    except Exception as e:
        print(f"❌ 下载/解析失败: {e}")
        return

    # 兼容：如果外层是对象，尝试取里面的代理数组
    if isinstance(data, dict):
        for key in data:
            if isinstance(data[key], list):
                data = data[key]
                print(f"🔍 检测到嵌套数组，使用key: {key}")
                break

    if not isinstance(data, list):
        print("❌ 不是列表格式，无法解析")
        return

    proxies_block = []
    group_list = []
    count = 0

    # 遍历+字段大小写容错
    for item in data:
        # 兼容大小写字段
        ip = item.get("ip") or item.get("IP")
        port = item.get("port") or item.get("PORT")
        ptype = item.get("type") or item.get("Type") or item.get("protocol")
        if not ip or not port or not ptype:
            continue

        ptype = str(ptype).lower()
        count += 1
        name = f"JSON-PROXY-{count:03d}"

        # Mihomo类型映射
        if ptype == "socks5":
            proxy_type = "socks5"
            extra = "udp: true"
        elif ptype in ("http", "https"):
            proxy_type = "http"
            extra = ""
        else:
            print(f"⏭️ 跳过不支持类型: {ptype}")
            continue

        proxies_block.append(f"""
  - name: {name}
    type: {proxy_type}
    server: {ip}
    port: {port}
    skip-cert-verify: true
    {extra}""")
        group_list.append(f"      - {name}")

    print(f"🎉 解析完成，有效节点总数: {count}")

    # 完整Mihomo模板
    yaml_template = f"""mixed-port: 7890
allow-lan: true
mode: rule
log-level: info
unified-delay: true
tcp-concurrent: true

proxies:{"".join(proxies_block)}

proxy-groups:
  - name: Proxy
    type: select
    proxies:
      - DIRECT
{"".join(group_list)}

rules:
  - MATCH,Proxy
"""

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(yaml_template)

if __name__ == "__main__":
    main()
