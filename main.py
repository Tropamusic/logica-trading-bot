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

# --- LISTA DE ACTIVOS (INCLUYENDO ORO USD/OZ) ---
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

print(f"🚀 {BOT_NAME} - MODO SNIPER (45/55) iniciado.")

while True:
    ahora = datetime.now(MI_ZONA_HORARIA)
    
    # Control de Fin de Semana
    dia_semana = ahora.weekday()
    if (dia_semana == 4 and ahora.hour >= 17) or (dia_semana == 5) or (dia_semana == 6 and ahora.hour < 17):
        time.sleep(3600)
        continue

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
            simbolo = activo['trading']

            # --- LÓGICA SNIPER VENTAS (DOWN) EN 55 ---
            # El "Sniper" solo dispara si está entre 55 y 58 (Zona de agotamiento temprano)
            if 55 <= rsi <= 58 and estado_activos[simbolo] == 'esperando':
                conteo_alertas += 1
                msg = (f"🎯 **SEÑAL SNIPER: BAJA (DOWN)**\n"
                       f"──────────────────\n"
                       f"💎 Par: **{activo['display']}**\n"
                       f"📊 RSI actual: {round(rsi, 2)}\n"
                       f"⏳ Tiempo: **2 MINUTOS**\n"
                       f"──────────────────\n"
                       f"✅ *Nivel 55 confirmado. Revisa y envía.*")
                enviar_telegram(msg, ID_PERSONAL)
                estado_activos[simbolo] = 'operado'
                # Bloqueo largo de 5 minutos para no saturar con el mismo par
                threading.Timer(300, lambda s=simbolo: estado_activos.update({s: 'esperando'})).start()

            # --- LÓGICA SNIPER COMPRAS (UP) EN 45 ---
            # El "Sniper" solo dispara si está entre 42 y 45 (Zona de rebote temprano)
            elif 42 <= rsi <= 45 and estado_activos[simbolo] == 'esperando':
                conteo_alertas += 1
                msg = (f"🎯 **SEÑAL SNIPER: SUBE (UP)**\n"
                       f"──────────────────\n"
                       f"💎 Par: **{activo['display']}**\n"
                       f"📊 RSI actual: {round(rsi, 2)}\n"
                       f"⏳ Tiempo: **2 MINUTOS**\n"
                       f"──────────────────\n"
                       f"✅ *Nivel 45 confirmado. Revisa y envía.*")
                enviar_telegram(msg, ID_PERSONAL)
                estado_activos[simbolo] = 'operado'
                threading.Timer(300, lambda s=simbolo: estado_activos.update({s: 'esperando'})).start()

        except: continue
    
    time.sleep(2) # Escaneo más pausado para precisión
