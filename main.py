import time
import requests
import threading
from tradingview_ta import TA_Handler, Interval
import telebot

# --- CONFIGURACIÓN TOTAL ---
TOKEN = "8386038643:AAEngPQbBuu41WBWm7pCYQxm3yEowoJzYaw"
CANAL_VIP = "-1002237930838"  # Donde se envían las señales para operar
CANAL_BITACORA = "-1003621701961" # Donde solo llegan resultados
LINK_CANAL_PRINCIPAL = "https://t.me/+4bqyiiDGXTA4ZTRh" 
BOT_NAME = "Lógica Trading 📊"

bot = telebot.TeleBot(TOKEN)

# Función de respuesta al /start (Ahora sí funcionará)
@bot.message_handler(commands=['start'])
def welcome(message):
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton("🚀 UNIRSE AL VIP", url=LINK_CANAL_PRINCIPAL))
    bot.reply_to(message, f"¡Hola! Soy el {BOT_NAME}. Estoy analizando el mercado para ti.", reply_markup=markup)

def enviar_mensaje(id_chat, texto):
    try:
        markup = telebot.types.InlineKeyboardMarkup()
        markup.add(telebot.types.InlineKeyboardButton("📥 ENTRAR AL BROKER", url=LINK_CANAL_PRINCIPAL))
        bot.send_message(id_chat, texto, parse_mode="Markdown", reply_markup=markup)
    except Exception as e:
        print(f"Error al enviar: {e}")

# --- LÓGICA DE TRADING REAL ---
def analizar():
    wins, loss = 0, 0
    print("📡 Analizando TradingView en tiempo real...")
    
    # Aviso de conexión
    enviar_mensaje(CANAL_VIP, f"✅ **{BOT_NAME} CONECTADO**\n\nBuscando señales operativas ahora mismo.")

    while True:
        activos = [
            {"t": "EURUSD", "d": "EUR/USD (OTC)"},
            {"t": "GBPUSD", "d": "GBP/USD (OTC)"},
            {"t": "AUDUSD", "d": "AUD/USD (OTC)"}
        ]

        for activo in activos:
            try:
                handler = TA_Handler(symbol=activo["t"], exchange="FX_IDC", screener="forex", interval=Interval.INTERVAL_1_MINUTE)
                datos = handler.get_analysis()
                rsi = datos.indicators["RSI"]
                precio_e = datos.indicators["close"]

                # --- DISPARADOR DE SEÑAL VENTA ---
                if rsi >= 64:
                    # PRIMERO: ENVIAR SEÑAL PARA OPERAR
                    texto_señal = (f"💎 **SEÑAL VIP CONFIRMADA** 💎\n\n"
                                   f"💱 Par: {activo['d']}\n"
                                   f"🔻 Operación: **BAJA (DOWN)**\n"
                                   f"⏱ Tiempo: 2 Minutos\n"
                                   f"📉 RSI: {rsi:.2f}\n\n"
                                   f"🔥 **¡ENTRAR AHORA!** 🔥")
                    enviar_mensaje(CANAL_VIP, texto_señal)
                    
                    time.sleep(125) # Tiempo de espera del trade
                    
                    # SEGUNDO: ENVIAR RESULTADO
                    final = handler.get_analysis().indicators["close"]
                    if final < precio_e:
                        wins += 1
                        res = f"✅ **RESULTADO: WIN** ✅\nPar: {activo['d']}\nMarcador: {wins}W - {loss}L"
                    else:
                        loss += 1
                        res = f"❌ **RESULTADO: LOSS** ❌\nPar: {activo['d']}\nMarcador: {wins}W - {loss}L"
                    
                    enviar_mensaje(CANAL_VIP, res)
                    enviar_mensaje(CANAL_BITACORA, f"📑 **BITÁCORA**\n{res}")

                # --- DISPARADOR DE SEÑAL COMPRA ---
                elif rsi <= 36:
                    # PRIMERO: ENVIAR SEÑAL PARA OPERAR
                    texto_señal = (f"💎 **SEÑAL VIP CONFIRMADA** 💎\n\n"
                                   f"💱 Par: {activo['d']}\n"
                                   f"🟢 Operación: **SUBE (UP)**\n"
                                   f"⏱ Tiempo: 2 Minutos\n"
                                   f"📈 RSI: {rsi:.2f}\n\n"
                                   f"🔥 **¡ENTRAR AHORA!** 🔥")
                    enviar_mensaje(CANAL_VIP, texto_señal)
                    
                    time.sleep(125)
                    
                    final = handler.get_analysis().indicators["close"]
                    if final > precio_e:
                        wins += 1
                        res = f"✅ **RESULTADO: WIN** ✅\nPar: {activo['d']}\nMarcador: {wins}W - {loss}L"
                    else:
                        loss += 1
                        res = f"❌ **RESULTADO: LOSS** ❌\nPar: {activo['d']}\nMarcador: {wins}W - {loss}L"
                    
                    enviar_mensaje(CANAL_VIP, res)
                    enviar_mensaje(CANAL_BITACORA, f"📑 **BITÁCORA**\n{res}")

            except:
                continue
        
        time.sleep(10)

if __name__ == "__main__":
    threading.Thread(target=analizar, daemon=True).start()
    bot.infinity_polling()
    
