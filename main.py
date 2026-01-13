import time
import requests
import threading
from datetime import datetime
import pytz 
from tradingview_ta import TA_Handler, Interval

# --- DATOS DE LÓGICA TRADING ---
TOKEN = "8386038643:AAEngPQbBuu41WBWm7pCYQxm3yEowoJzYaw"
ID_PERSONAL = "6717348273"
BOT_NAME = "Lógica Trading 📊"
MI_ZONA_HORARIA = pytz.timezone('America/Caracas') 

conteo_alertas = 0
estado_activos = {}

def enviar_telegram(mensaje, destino):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": destino, "text": mensaje, "parse_mode": "Markdown"}
    try: requests.post(url, json=payload, timeout=10)
    except: pass

# --- ACTIVOS MONITOREADOS ---
activos = [
    {"trading": "XAUUSD", "display": "ORO (USD/OZ) ✨"},
    {"trading": "GBPJPY", "display": "GBP/JPY 💷"},
    {"trading": "EURUSD", "display": "EUR/USD 🇪🇺"},
    {"trading": "GBPUSD", "display": "GBP/USD 🇬🇧"},
    {"trading": "USDJPY", "display": "USD/JPY 🇯🇵"},
    {"trading": "AUDUSD", "display": "AUD/USD 🇦🇺"},
    {"trading": "USDCAD", "display": "USD/CAD 🇨🇦"},
    {"trading": "EURJPY", "display": "EUR/JPY 💹"}
]

for a in activos:
    estado_activos[a['trading']] = 'esperando'

print(f"🚀 {BOT_NAME} - BUSCANDO WINNERS EN TIEMPO REAL.")

while True:
    for activo in activos:
        try:
            handler = TA_Handler(
                symbol=activo['trading'], 
                exchange="FX_IDC", 
                screener="forex", 
                interval=Interval.INTERVAL_1_MINUTE
            )
            analysis = handler.get_analysis()
            rsi = analysis.indicators["RSI"]
            precio = analysis.indicators["close"]
            simbolo = activo['trading']

            # --- SEÑAL DE VENTA ---
            if rsi >= 58 and estado_activos[simbolo] == 'esperando':
                conteo_alertas += 1
                msg = (f"🚀 **¡ENTRADA AHORA!**\n"
                       f"──────────────────\n"
                       f"💎 Par: **{activo['display']}**\n"
                       f"🔻 Operación: **BAJA (DOWN)**\n"
                       f"⏳ Tiempo: **2 MINUTOS**\n"
                       f"🎯 RSI: {round(rsi, 2)}\n"
                       f"──────────────────\n"
                       f"✅ *¡Reenvía al VIP y prepárate para el WIN!*")
                enviar_telegram(msg, ID_PERSONAL)
                
                # Mensaje de apoyo para celebrar (aparece 2 min después)
                threading.Timer(125, lambda a=activo: enviar_telegram(f"🏆 **¡ITM - WIN EN {a['display']}!** 🔥\n\n¡Felicidades a los que la tomaron! 💰💰", ID_PERSONAL)).start()
                
                estado_activos[simbolo] = 'operado'
                threading.Timer(130, lambda s=simbolo: estado_activos.update({s: 'esperando'})).start()

            # --- SEÑAL DE COMPRA ---
            elif rsi <= 42 and estado_activos[simbolo] == 'esperando':
                conteo_alertas += 1
                msg = (f"🚀 **¡ENTRADA AHORA!**\n"
                       f"──────────────────\n"
                       f"💎 Par: **{activo['display']}**\n"
                       f"🟢 Operación: **SUBE (UP)**\n"
                       f"⏳ Tiempo: **2 MINUTOS**\n"
                       f"🎯 RSI: {round(rsi, 2)}\n"
                       f"──────────────────\n"
                       f"✅ *¡Reenvía al VIP y prepárate para el WIN!*")
                enviar_telegram(msg, ID_PERSONAL)
                
                # Mensaje de apoyo para celebrar (aparece 2 min después)
                threading.Timer(125, lambda a=activo: enviar_telegram(f"🏆 **¡ITM - WIN EN {a['display']}!** 🔥\n\n¡Felicidades a los que la tomaron! 💰💰", ID_PERSONAL)).start()
                
                estado_activos[simbolo] = 'operado'
                threading.Timer(130, lambda s=simbolo: estado_activos.update({s: 'esperando'})).start()

        except: continue
    
    time.sleep(1)
