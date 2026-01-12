import time
import requests
import threading
from tradingview_ta import TA_Handler, Interval
import telebot

# --- CONFIGURACIÓN TOTAL ---
TOKEN = "8386038643:AAEngPQbBuu41WBWm7pCYQxm3yEowoJzYaw"
CANAL_VIP = "-1002237930838"  
CANAL_BITACORA = "-1003621701961" 
LINK_CANAL_PRINCIPAL = "https://t.me/+4bqyiiDGXTA4ZTRh" 
BOT_NAME = "Lógica Trading 📊"

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def welcome(message):
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton("🚀 OPERAR AHORA", url=LINK_CANAL_PRINCIPAL))
    bot.reply_to(message, f"¡Hola! {BOT_NAME} activo. Señales ganadoras cada 2 min en el VIP.", reply_markup=markup)

def enviar_mensaje(id_chat, texto, con_boton=True):
    try:
        markup = None
        if con_boton:
            markup = telebot.types.InlineKeyboardMarkup()
            markup.add(telebot.types.InlineKeyboardButton("📥 ENTRAR AL BROKER", url=LINK_CANAL_PRINCIPAL))
        bot.send_message(id_chat, texto, parse_mode="Markdown", reply_markup=markup)
    except Exception as e:
        print(f"Error: {e}")

# --- LÓGICA DE TRADING DE ALTA FRECUENCIA ---
def analizar():
    wins, loss = 0, 0
    racha_actual = 0  # Contador de racha
    print("📡 Buscando señales ganadoras...")
    
    enviar_mensaje(CANAL_VIP, f"✅ **{BOT_NAME} ACTIVADO 24/7**\n\nBuscando entradas sin riesgo. ¡Atentos!")

    while True:
        activos = [
            {"t": "EURUSD", "d": "EUR/USD (OTC)"},
            {"t": "AUDUSD", "d": "AUD/USD (OTC)"},
            {"t": "GBPUSD", "d": "GBP/USD (OTC)"},
            {"t": "USDJPY", "d": "USD/JPY (OTC)"}
        ]

        for activo in activos:
            try:
                handler = TA_Handler(symbol=activo["t"], exchange="FX_IDC", screener="forex", interval=Interval.INTERVAL_1_MINUTE)
                datos = handler.get_analysis()
                rsi = datos.indicators["RSI"]
                precio_e = datos.indicators["close"]

                if rsi >= 64 or rsi <= 36:
                    direccion = "BAJA (DOWN) 🔻" if rsi >= 64 else "SUBE (UP) 🟢"
                    emoji = "📉" if rsi >= 64 else "📈"

                    enviar_mensaje(CANAL_VIP, f"💎 **SEÑAL CONFIRMADA** 💎\n\n💱 Par: {activo['d']}\n{emoji} Operación: **{direccion}**\n⏱ Tiempo: 2 Minutos\n📊 RSI: {rsi:.2f}\n\n🔥 **¡ENTRAR AHORA!** 🔥")
                    
                    time.sleep(125) 
                    
                    final = handler.get_analysis().indicators["close"]
                    if (rsi >= 64 and final < precio_e) or (rsi <= 36 and final > precio_e):
                        wins += 1
                        racha_actual += 1
                        res = f"✅ **WIN GANADA ✅**\nPar: {activo['d']}\nMarcador: {wins}W - {loss}L"
                        
                        # --- AVISO DE RACHA ---
                        if racha_actual >= 3:
                            enviar_mensaje(CANAL_VIP, f"💰 **¡RACHA DE {racha_actual} GANADAS SEGUIDAS!** 💰\nEl sistema está en su mejor momento. 🔥")
                    else:
                        loss += 1
                        racha_actual = 0 # Se rompe la racha
                        res = f"❌ **LOSS PERDIDA ❌**\nPar: {activo['d']}\nMarcador: {wins}W - {loss}L"
                    
                    enviar_mensaje(CANAL_VIP, res)
                    enviar_mensaje(CANAL_BITACORA, f"📑 **BITÁCORA**\n{res}")
                    time.sleep(5) 

            except:
                continue
        time.sleep(5)

if __name__ == "__main__":
    threading.Thread(target=analizar, daemon=True).start()
    bot.infinity_polling()
    
