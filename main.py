import time
import requests
import threading
from tradingview_ta import TA_Handler, Interval
import telebot

# --- CONFIGURACIÓN ---
TOKEN = "8386038643:AAEngPQbBuu41WBWm7pCYQxm3yEowoJzYaw"
CANAL_VIP = "-1002237930838"  
CANAL_BITACORA = "-1003621701961" 
LINK_CANAL_PRINCIPAL = "https://t.me/+4bqyiiDGXTA4ZTRh" 
BOT_NAME = "Lógica Trading 📊"

# Evita el error 409 Conflict eliminando sesiones previas
bot = telebot.TeleBot(TOKEN)
bot.remove_webhook()
time.sleep(1)

@bot.message_handler(commands=['start'])
def welcome(message):
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton("🚀 OPERAR AHORA", url=LINK_CANAL_PRINCIPAL))
    bot.reply_to(message, f"¡Hola! {BOT_NAME} listo. Enviando señales cada 2 min.", reply_markup=markup)

def enviar_mensaje(id_chat, texto):
    try:
        markup = telebot.types.InlineKeyboardMarkup()
        markup.add(telebot.types.InlineKeyboardButton("📥 ENTRAR AL BROKER", url=LINK_CANAL_PRINCIPAL))
        bot.send_message(id_chat, texto, parse_mode="Markdown", reply_markup=markup)
    except: pass

def analizar():
    wins, loss, racha = 0, 0, 0
    enviar_mensaje(CANAL_VIP, f"✅ **{BOT_NAME} CONECTADO 24/7**\n\nBuscando señales ganadoras cada 2 minutos...")

    while True:
        # Lista amplia de pares para asegurar señales constantes
        activos = [
            {"t": "EURUSD", "d": "EUR/USD (OTC)"},
            {"t": "GBPUSD", "d": "GBP/USD (OTC)"},
            {"t": "AUDUSD", "d": "AUD/USD (OTC)"},
            {"t": "USDJPY", "d": "USD/JPY (OTC)"},
            {"t": "EURJPY", "d": "EUR/JPY (OTC)"}
        ]

        for activo in activos:
            try:
                handler = TA_Handler(symbol=activo["t"], exchange="FX_IDC", screener="forex", interval=Interval.INTERVAL_1_MINUTE)
                analysis = handler.get_analysis()
                rsi = analysis.indicators["RSI"]
                precio_e = analysis.indicators["close"]

                # Filtro de seguridad (Sin riesgo): 64 para Venta, 36 para Compra
                if rsi >= 64 or rsi <= 36:
                    direccion = "BAJA (DOWN) 🔻" if rsi >= 64 else "SUBE (UP) 🟢"
                    
                    # ENVIAR SEÑAL INMEDIATA
                    enviar_mensaje(CANAL_VIP, f"💎 **SEÑAL CONFIRMADA** 💎\n\n💱 Par: {activo['d']}\n🎯 Acción: **{direccion}**\n⏱ Tiempo: 2 Minutos\n📊 RSI: {rsi:.2f}\n\n🔥 **¡ENTRAR YA!** 🔥")
                    
                    # Espera exacta de la operación (120 seg + 5 seg de margen)
                    time.sleep(125)
                    
                    # Verificación de Resultado
                    final = handler.get_analysis().indicators["close"]
                    es_win = (rsi >= 64 and final < precio_e) or (rsi <= 36 and final > precio_e)

                    if es_win:
                        wins += 1
                        racha += 1
                        res_txt = f"✅ **WIN GANADA ✅**\nPar: {activo['d']}\nMarcador: {wins}W - {loss}L"
                        if racha >= 3:
                            enviar_mensaje(CANAL_VIP, f"💰 **¡RACHA DE {racha} GANADAS!** 💰")
                    else:
                        loss += 1
                        racha = 0
                        res_txt = f"❌ **LOSS PERDIDA ❌**\nPar: {activo['d']}\nMarcador: {wins}W - {loss}L"
                    
                    enviar_mensaje(CANAL_VIP, res_txt)
                    enviar_mensaje(CANAL_BITACORA, f"📑 **BITÁCORA**\n{res_txt}")
                    
                    # Pausa mínima para buscar la siguiente oportunidad de 2 min
                    time.sleep(2)
                    break # Salta al siguiente ciclo de escaneo para frescura de datos

            except: continue
        time.sleep(5)

if __name__ == "__main__":
    threading.Thread(target=analizar, daemon=True).start()
    # Parámetros para evitar el error 409 y desconexiones
    bot.infinity_polling(timeout=10, long_polling_timeout=5)
    
