import requests
import json

# 源JSON地址
JSON_URL = "https://github.com/proxygenerator1/ProxyGenerator/raw/refs/heads/main/ALL/all.json"
OUTPUT_FILE = "mihomo_all_json_config.yaml"

def main():
    try:
        resp = requests.get(JSON_URL, timeout=15)
        resp.raise_for_status()
        data = json.loads(resp.text)
    except Exception as e:
        print(f"下载/解析JSON失败: {e}")
        return

    proxies_block = []
    group_list = []
    count = 0

    # 遍历JSON内代理列表
    for item in data:
        ip = item.get("ip")
        port = item.get("port")
        ptype = item.get("type", "").lower()

        if not ip or not port:
            continue
        
        count += 1
        name = f"JSON-PROXY-{count:03d}"

        # 匹配Mihomo支持的类型
        if ptype in ["socks5"]:
            proxy_type = "socks5"
            extra = "udp: true"
        elif ptype in ["http", "https"]:
            proxy_type = "http"
            extra = ""
        else:
            continue  # 跳过不支持的socks4等

        proxies_block.append(f"""
  - name: {name}
    type: {proxy_type}
    server: {ip}
    port: {port}
    skip-cert-verify: true
    {extra}""")
        group_list.append(f"      - {name}")

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

    print(f"✅ 转换完成！共生成 {count} 个有效节点，已保存至 {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
