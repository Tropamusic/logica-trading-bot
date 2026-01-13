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

# --- LISTA DE ACTIVOS (ORO + FOREX) ---
activos = [
    {"trading": "XAUUSD", "display": "ORO (USD/OZ) ✨"},
    {"trading": "EURUSD", "display": "EUR/USD"},
    {"trading": "GBPUSD", "display": "GBP/USD"},
    {"trading": "USDJPY", "display": "USD/JPY"},
    {"trading": "AUDUSD", "display": "AUD/USD"},
    {"trading": "USDCAD", "display": "USD/CAD"},
    {"trading": "USDCHF", "display": "USD/CHF"},
    {"trading": "NZDUSD", "display": "NZD/USD"},
    {"trading": "EURJPY", "display": "EUR/JPY"},
    {"trading": "GBPJPY", "display": "GBP/JPY"},
    {"trading": "EURGBP", "display": "EUR/GBP"},
    {"trading": "AUDJPY", "display": "AUD/JPY"},
    {"trading": "EURAUD", "display": "EUR/AUD"}
]

for a in activos:
    estado_activos[a['trading']] = 'esperando'

print(f"🚀 {BOT_NAME} - MODO TIEMPO REAL (58/42) activo.")

while True:
    ahora = datetime.now(MI_ZONA_HORARIA)
    
    # Control Fin de Semana
    if (ahora.weekday() == 4 and ahora.hour >= 17) or (ahora.weekday() == 5) or (ahora.weekday() == 6 and ahora.hour < 17):
        time.sleep(3600)
        continue

    for activo in activos:
        try:
            # Conexión directa con TradingView (Intervalo 1 Minuto)
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

            # --- SEÑALES EN TIEMPO REAL ---
            
            # VENTA (DOWN) si RSI toca 58
            if rsi >= 58 and estado_activos[simbolo] == 'esperando':
                conteo_alertas += 1
                msg = (f"🚀 **¡ENTRADA AHORA!** (#{conteo_alertas})\n"
                       f"──────────────────\n"
                       f"💎 Par: **{activo['display']}**\n"
                       f"🔻 Operación: **BAJA (DOWN)**\n"
                       f"💵 Precio: `{round(precio, 5)}`\n"
                       f"🎯 RSI: {round(rsi, 2)}\n"
                       f"⏳ Tiempo: **2 MINUTOS**\n"
                       f"──────────────────\n"
                       f"✅ *Copia y envía rápido al canal.*")
                enviar_telegram(msg, ID_PERSONAL)
                estado_activos[simbolo] = 'operado'
                # Solo bloquea ESTE activo por 2 min (para no repetir la misma vela)
                threading.Timer(125, lambda s=simbolo: estado_activos.update({s: 'esperando'})).start()

            # COMPRA (UP) si RSI toca 42
            elif rsi <= 42 and estado_activos[simbolo] == 'esperando':
                conteo_alertas += 1
                msg = (f"🚀 **¡ENTRADA AHORA!** (#{conteo_alertas})\n"
                       f"──────────────────\n"
                       f"💎 Par: **{activo['display']}**\n"
                       f"🟢 Operación: **SUBE (UP)**\n"
                       f"💵 Precio: `{round(precio, 5)}`\n"
                       f"🎯 RSI: {round(rsi, 2)}\n"
                       f"⏳ Tiempo: **2 MINUTOS**\n"
                       f"──────────────────\n"
                       f"✅ *Copia y envía rápido al canal.*")
                enviar_telegram(msg, ID_PERSONAL)
                estado_activos[simbolo] = 'operado'
                threading.Timer(125, lambda s=simbolo: estado_activos.update({s: 'esperando'})).start()

        except: continue
    
    # Escaneo sin pausas largas para tiempo real
    time.sleep(0.5)
