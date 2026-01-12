import time
import requests
import threading
from tradingview_ta import TA_Handler, Interval
import telebot
from telebot import apihelper

# --- CONFIGURACIÓN ---
TOKEN = "8386038643:AAEngPQbBuu41WBWm7pCYQxm3yEowoJzYaw"
CANAL_VIP = "-1002237930838"  
CANAL_BITACORA = "-1003621701961" 
LINK_CANAL_PRINCIPAL = "https://t.me/+4bqyiiDGXTA4ZTRh" 
BOT_NAME = "Lógica Trading 📊"

# Evita colisiones de hilos
apihelper.SESSION_ITER_SIZE = 50 
bot = telebot.TeleBot(TOKEN, threaded=False) # Desactivamos hilos en el polling para evitar el 409

def enviar_mensaje(id_chat, texto):
    try:
        markup = telebot.types.InlineKeyboardMarkup()
        markup.add(telebot.types.InlineKeyboardButton("📥 ENTRAR AL BROKER", url=LINK_CANAL_PRINCIPAL))
        bot.send_message(id_chat, texto, parse_mode="Markdown", reply_markup=markup)
    except: pass

def analizar():
    wins, loss, racha = 0, 0, 0
    # Espera un momento a que el polling inicie
    time.sleep(5)
    enviar_mensaje(CANAL_VIP, f"✅ **{BOT_NAME} RECONECTADO**\n\nBuscando señales ganadoras cada 2 minutos... 📡")

    while True:
        # Lista de pares para asegurar que SIEMPRE haya una señal cerca
        activos = [
            {"t": "EURUSD", "d": "EUR/USD (OTC)"},
            {"t": "GBPUSD", "d": "GBP/USD (OTC)"},
            {"t": "AUDUSD", "d": "AUD/USD (OTC)"},
            {"t": "USDJPY", "d": "USD/JPY (OTC)"},
            {"t": "EURJPY", "d": "EUR/JPY (OTC)"},
            {"t": "GBPJPY", "d": "GBP/JPY (OTC)"}
        ]

        for activo in activos:
            try:
                handler = TA_Handler(symbol=activo["t"], exchange="FX_IDC", screener="forex", interval=Interval.INTERVAL_1_MINUTE)
                analysis = handler.get_analysis()
                rsi = analysis.indicators["RSI"]
                precio_e = analysis.indicators["close"]

                # Lógica de alta probabilidad (36/64)
                if rsi >= 64 or rsi <= 36:
                    direccion = "BAJA (DOWN) 🔻" if rsi >= 64 else "SUBE (UP) 🟢"
                    
                    enviar_mensaje(CANAL_VIP, f"💎 **SEÑAL CONFIRMADA** 💎\n\n💱 Par: {activo['d']}\n🎯 Acción: **{direccion}**\n⏱ Tiempo: 2 Minutos\n📊 RSI: {rsi:.2f}\n\n🔥 **¡ENTRAR YA!** 🔥")
                    
                    time.sleep(125) # Duración de la operación
                    
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
                    time.sleep(2)
                    break 

            except Exception as e:
                print(f"Error analizando {activo['t']}: {e}")
                continue
        time.sleep(10)

# --- EJECUCIÓN CON LIMPIEZA DE WEBHOOKS ---
if __name__ == "__main__":
    # 1. Quitar cualquier conexión previa
    bot.remove_webhook()
    time.sleep(2)
    
    # 2. Iniciar análisis en hilo aparte
    t = threading.Thread(target=analizar)
    t.daemon = True
    t.start()
    
    # 3. Polling infinito con reconexión automática
    print("Bot activo...")
    while True:
        try:
            bot.polling(none_stop=True, interval=0, timeout=20)
        except Exception as e:
            print(f"Conflicto detectado: {e}. Reiniciando en 5s...")
            time.sleep(5)
