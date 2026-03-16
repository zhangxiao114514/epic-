import os
import json
import requests

# 从 GitHub Secrets 读取配置
TG_BOT_TOKEN = os.environ.get("TG_BOT_TOKEN")
TG_CHAT_ID = os.environ.get("TG_CHAT_ID")

# 去重文件
SENT_FILE = "sent_games.json"
sent_games = set()

# 加载已发送的游戏ID
if os.path.exists(SENT_FILE):
    try:
        with open(SENT_FILE, "r", encoding="utf-8") as f:
            sent_games = set(json.load(f))
    except:
        sent_games = set()

def get_free_games():
    """获取 Steam 免费游戏"""
    url = "https://store.steampowered.com/api/featuredcategories"
    try:
        res = requests.get(url, timeout=20)
        data = res.json()
        return data.get("free_games", {}).get("items", [])
    except:
        return []

def send_telegram(game):
    """发送 TG 消息（带图片+按钮）"""
    appid = game["id"]
    name = game["name"]
    img = game["large_capsule_image"]
    link = f"https://store.steampowered.com/app/{appid}"

    caption = f"""🎮 **Steam 喜加一**
🆓 免费领取：{name}
⏰ 领取链接：[点击领取]({link})"""

    api_url = f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendPhoto"
    payload = {
        "chat_id": TG_CHAT_ID,
        "photo": img,
        "caption": caption,
        "parse_mode": "Markdown",
        "reply_markup": json.dumps({
            "inline_keyboard": [[{"text": "🔗 立即领取", "url": link}]]
        })
    }

    try:
        requests.post(api_url, json=payload, timeout=15)
        print(f"✅ 已发送：{name}")
    except Exception as e:
        print(f"❌ 发送失败：{e}")

def main():
    if not TG_BOT_TOKEN or not TG_CHAT_ID:
        print("❌ 未配置 TG 令牌或聊天ID")
        return

    games = get_free_games()
    if not games:
        print("✅ 今日无免费游戏")
        return

    new_count = 0
    for game in games:
        appid = game.get("id")
        if not appid or appid in sent_games:
            continue

        sent_games.add(appid)
        send_telegram(game)
        new_count += 1

    # 保存去重列表
    with open(SENT_FILE, "w", encoding="utf-8") as f:
        json.dump(list(sent_games), f, ensure_ascii=False)

    print(f"🎯 任务完成，本次推送 {new_count} 个游戏")

if __name__ == "__main__":
    main()
