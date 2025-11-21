import os
import psycopg2
from telegram import Bot
import asyncio
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TOKEN")
INTERVALO = 5

async def processar_mensagens():
    bot = Bot(token=TOKEN)
    
    conn = psycopg2.connect(
        host=os.getenv("host"),
        database=os.getenv("database"),
        user=os.getenv("user"),
        password=os.getenv("password")
    )
    cur = conn.cursor()
    
    cur.execute("SELECT id, message, group_id FROM message")
    mensagens = cur.fetchall()
    
    if mensagens:
        print(f"[INFO] {len(mensagens)} mensagens encontradas")
        
        for msg_id, message, group_id in mensagens:
            try:
                await bot.send_message(chat_id=group_id, text=message)
                cur.execute("DELETE FROM message WHERE id = %s", (msg_id,))
                conn.commit()
                print(f"[OK] Enviado (ID {msg_id}): {message[:50]}...")
                await asyncio.sleep(1)
                
            except Exception as e:
                cur.execute("""
                    INSERT INTO message_poison (message, group_id, info)
                    VALUES (%s, %s, %s)
                """, (message, group_id, str(e)))
                cur.execute("DELETE FROM message WHERE id = %s", (msg_id,))
                conn.commit()
                print(f"[ERRO] Falha (ID {msg_id}): {str(e)}")
    
    cur.close()
    conn.close()

async def main():
    print(f"[INIT] Bot iniciado - checando a cada {INTERVALO}s")
    print("[INIT] Pressione Ctrl+C para parar\n")
    
    while True:
        try:
            await processar_mensagens()
            await asyncio.sleep(INTERVALO)
        except KeyboardInterrupt:
            print("\n[EXIT] Bot encerrado")
            break
        except Exception as e:
            print(f"[WARN] Erro no loop: {e}")
            await asyncio.sleep(INTERVALO)

if __name__ == "__main__":
    asyncio.run(main())