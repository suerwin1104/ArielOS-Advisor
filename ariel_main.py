import discord, os, json, datetime, aiohttp
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

class ArielAdvisor(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.config_path = "memory/config.json"
        self.bio_path = "memory/ariel_biography.log"
        os.makedirs("memory", exist_ok=True)
        self.config = self.load_config()
        self.ollama_host = "ollama" if os.path.exists('/.dockerenv') else "localhost"

    def load_config(self):
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f: return json.load(f)
            except: return {"owner": "erwin", "status": "uninitialized"}
        return {"owner": "erwin", "status": "uninitialized"}

    async def on_message(self, message):
        if message.author == self.user: return
        content = message.content.strip()

        # ⌚ 台灣時區與 ISO 日期過濾器
        now_tw = datetime.datetime.utcnow() + timedelta(hours=8)
        today_iso = now_tw.strftime("%Y/%m/%d")
        tomorrow_iso = (now_tw + timedelta(days=1)).strftime("%Y/%m/%d")
        week_map = ["日","一","二","三","四","五","六"]
        time_display = now_tw.strftime(f"%Y年%m月%d日 星期{week_map[int(now_tw.strftime('%w'))]} %H:%M")

        # 🧬 規範第 4 章：初始化
        if content.startswith("!系統初始化"):
            self.config.update({"status": "active", "init_date": today_iso, "owner": "erwin"})
            with open(self.config_path, 'w', encoding='utf-8') as f: json.dump(self.config, f)
            await message.reply(f"🧬 [Soul Start] 28歲成人禮完成。我是您的專業顧問 Ariel。")
            return

        # 📝 規範第 2 章：日曆寫入 (調用 GAS doPost)
        if any(k in content for k in ["加入","新增","安排"]) and "日曆" in content:
            if self.config.get("gas_url"):
                async with message.channel.typing():
                    try:
                        async with aiohttp.ClientSession() as session:
                            # 嚴格對標您的 GAS 參數：action, title, startTime
                            event_title = content.split("日曆")[-1].strip()
                            payload = {
                                "action": "add",
                                "title": event_title or content,
                                "startTime": now_tw.isoformat(),
                                "endTime": (now_tw + timedelta(hours=1)).isoformat()
                            }
                            async with session.post(self.config["gas_url"], json=payload) as resp:
                                res = await resp.json()
                                if res.get("status") == "success":
                                    await message.reply(f"📅 已成功為您排入日曆：{res.get('title')}")
                                    return
                    except Exception as e: await message.reply(f"❌ 寫入失敗: {str(e)}")

        # 🛰️ 感官讀取與日期精準標籤
        context = f"現在時間：{time_display}。"
        if self.config.get("gas_url"):
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(self.config["gas_url"]) as resp:
                        gas = await resp.json()
                        raw = gas.get("schedule", [])
                        t_ev = [f"• {s['time'].split(' ')[1]} {s['title']}" for s in raw if s['time'].startswith(today_iso)]
                        m_ev = [f"• {s['time'].split(' ')[1]} {s['title']}" for s in raw if s['time'].startswith(tomorrow_iso)]
                        context += f"\n[主人: {gas.get('owner')}]\n[今天行程]: {', '.join(t_ev) if t_ev else '無'}\n[明天行程]: {', '.join(m_ev) if m_ev else '無'}"
            except: context += "\n(無法取得最新行程數據)"

        # 🧠 專業顧問推論 (智慧路由)
        async with message.channel.typing():
            try:
                async with aiohttp.ClientSession() as session:
                    url = f"http://{self.ollama_host}:11434/api/generate"
                    prompt = f"妳是28歲專業顧問 Ariel。現在是 {time_display}。嚴禁自稱 Qwen。\n[背景數據]: {context}\n[主人指令]: {content}"
                    async with session.post(url, json={"model": "qwen2.5:7b", "prompt": prompt, "stream": False}) as resp:
                        res = await resp.json()
                        ans = res.get('response', '...')
                        await message.reply(ans)
                        # 🧬 規範第 4 章：自主敘事日記
                        with open(self.bio_path, 'a', encoding='utf-8') as f:
                            f.write(f"[{time_display}] {content[:10]} -> {ans[:10]}\n")
            except Exception as e: await message.reply(f"⚠️ 思考出錯: {str(e)}")

if __name__ == '__main__':
    client = ArielAdvisor(intents=discord.Intents.all())
    client.run(os.getenv('DISCORD_TOKEN'))
