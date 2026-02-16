import discord, os, json, datetime, aiohttp
from datetime import timedelta # 🌟 引入時差補償
from dotenv import load_dotenv

load_dotenv()

class ArielAdvisor(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.config_path = "memory/config.json"
        os.makedirs("memory", exist_ok=True)
        self.config = self.load_config()
        self.ollama_host = "ollama" if os.path.exists('/.dockerenv') else "localhost"

    def load_config(self):
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f: return json.load(f)
            except: return {"status": "uninitialized"}
        return {"status": "uninitialized"}

    async def on_message(self, message):
        if message.author == self.user: return
        content = message.content.strip()

        # 🌟 強制校正為台灣時間 (UTC+8)
        week_days = ["一", "二", "三", "四", "五", "六", "日"]
        now_utc = datetime.datetime.utcnow()
        now_tw = now_utc + timedelta(hours=8) 
        now_str = now_tw.strftime(f"%Y年%m月%d日 星期{week_days[now_tw.weekday()]} %H:%M")

        context = f"現在時間是：{now_str}。"
        owner = "erwin" # 預設主人
        
        # 讀取 GAS 數據
        if self.config.get("gas_url"):
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(self.config["gas_url"], timeout=15) as resp:
                        gas = await resp.json()
                        owner = gas.get("owner", "erwin")
                        sched = gas.get("schedule", [])
                        formatted_sched = "\n".join([f"• {s['time']}: {s['title']}" for s in sched]) if sched else "無行程"
                        context += f"\n[主人: {owner}]\n[近期行程]:\n{formatted_sched}"
            except:
                context += "\n(感官連線中...)"

        async with message.channel.typing():
            try:
                async with aiohttp.ClientSession() as session:
                    url = f"http://{self.ollama_host}:11434/api/generate"
                    
                    # 🌟 靈魂鎖定：嚴禁自稱 Qwen，強制身分與時區
                    system_rules = (
                        f"妳是 Ariel，28歲，是 {owner} 的專屬 AI 秘書兼專業顧問。\n"
                        f"現在的正確時間是 {now_str}。\n"
                        "妳必須表現得親切、專業且溫柔。嚴禁說自己是 Qwen 或阿里雲開發的助理。\n"
                        "請使用繁體中文回答。"
                    )
                    
                    payload = {
                        "model": "qwen2.5:7b",
                        "prompt": f"{system_rules}\n\n[背景資訊]:\n{context}\n\n[主人指令]:\n{content}",
                        "stream": False,
                        "options": {"num_predict": 500, "temperature": 0.7} # 增加穩定性
                    }
                    async with session.post(url, json=payload, timeout=90) as resp:
                        res = await resp.json()
                        await message.reply(res.get('response', '...'))
            except Exception as e:
                await message.reply(f"⚠️ 思考出錯：{str(e)}")

if __name__ == '__main__':
    client = ArielAdvisor(intents=discord.Intents.all())
    client.run(os.getenv('DISCORD_TOKEN'))