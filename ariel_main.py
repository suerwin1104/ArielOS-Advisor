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

        # 1. 🧬 [Soul Start] 28 歲成人禮指令
        if content.startswith("!系統初始化"):
            self.config["status"] = "active"
            self.config["age"] = 28
            with open(self.config_path, 'w', encoding='utf-8') as f: json.dump(self.config, f)
            await message.reply("🧬 [Ariel OS] 28 歲成人禮完成。我是您的專業顧問 Ariel，很高興為您服務。")
            return

        # 2. ⌚ 時區精準校正 (UTC+8)
        now_tw = datetime.datetime.utcnow() + timedelta(hours=8)
        today_str = now_tw.strftime("%Y/%m/%d")
        tomorrow_str = (now_tw + timedelta(days=1)).strftime("%Y/%m/%d")
        week_days = ["一", "二", "三", "四", "五", "六", "日"]
        time_display = now_tw.strftime(f"%Y年%m月%d日 星期{week_days[now_tw.weekday()]} %H:%M")

        context = f"現在時間：{time_display}。"
        
        # 3. 🛰️ 感官資料過濾 (防止日期混淆)
        if self.config.get("gas_url"):
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(self.config["gas_url"], timeout=15) as resp:
                        gas = await resp.json()
                        owner = gas.get("owner", "erwin")
                        raw_sched = gas.get("schedule", [])
                        
                        # 🌟 核心修正：將行程分類為「今天」與「明天」
                        today_events = [f"• {s['time'].split(' ')[1]} {s['title']}" for s in raw_sched if s['time'].startswith(today_str)]
                        tomorrow_events = [f"• {s['time'].split(' ')[1]} {s['title']}" for s in raw_sched if s['time'].startswith(tomorrow_str)]
                        
                        context += f"\n[主人身分: {owner}]\n"
                        context += f"[今天 ({today_str}) 行程]: " + (", ".join(today_events) if today_events else "暫無行程") + "\n"
                        context += f"[明天 ({tomorrow_str}) 行程]: " + (", ".join(tomorrow_events) if tomorrow_events else "暫無行程")
            except:
                context += "\n(感官連線中...)"

        # 4. 🧠 呼叫大腦 (身分鎖定)
        async with message.channel.typing():
            try:
                async with aiohttp.ClientSession() as session:
                    url = f"http://{self.ollama_host}:11434/api/generate"
                    # 強制約束：嚴禁胡說八道，嚴禁自稱 Qwen
                    prompt = (
                        f"妳是 Ariel，28歲，專業親切的 AI 秘書。現在時間是 {time_display}。\n"
                        f"請嚴格根據以下背景資訊回答，不要虛構行程或日期。嚴禁說妳是 Qwen。\n"
                        f"背景資訊：{context}\n"
                        f"主人指令：{content}"
                    )
                    
                    payload = {"model": "qwen2.5:7b", "prompt": prompt, "stream": False}
                    async with session.post(url, json=payload, timeout=90) as resp:
                        res = await resp.json()
                        await message.reply(res.get('response', '...'))
                        
                        # 自主敘事日誌 (規範第 4 章)
                        with open(self.bio_path, 'a', encoding='utf-8') as f:
                            f.write(f"[{time_display}] 與 {owner} 對話: {content[:10]}\n")
            except Exception as e:
                await message.reply(f"⚠️ 思考出錯：{str(e)}")

if __name__ == '__main__':
    client = ArielAdvisor(intents=discord.Intents.all())
    client.run(os.getenv('DISCORD_TOKEN'))
