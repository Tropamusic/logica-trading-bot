import time
import requests
import threading
from datetime import datetime
import pytz 
from tradingview_ta import TA_Handler, Interval

# --- DATOS DE LÓGICA TRADING ---
TOKEN = "8386038643:AAEngPQbBuu41WBWm7pCYQxm3yEowoJzYaw"
ID_PERSONAL = "6717348273"
LINK_VIP = "https://t.me/+4bqyiiDGXTA4ZTRh"
BOT_NAME = "Lógica Trading 📊"

MI_ZONA_HORARIA = pytz.timezone('America/Caracas') 

conteo_alertas = 0
# Diccionario para controlar el estado de cada activo y evitar spam de pre-avisos
estado_activos = {}

def enviar_telegram(mensaje, destino):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": destino, "text": mensaje, "parse_mode": "Markdown"}
    try: requests.post(url, json=payload, timeout=10)
    except: pass

# --- LISTA COMPLETA DE ACTIVOS REALES + ORO ---
activos = [
    {"trading": "XAUUSD", "display": "ORO (XAU/USD) ✨"},
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

# Inicializar estados
for a in activos:
    estado_activos[a['trading']] = 'esperando'

print(f"🚀 {BOT_NAME} - ASISTENTE PERSONAL (Modo Pre-Aviso) iniciado.")

# --- BUCLE PRINCIPAL ---
while True:
    ahora = datetime.now(MI_ZONA_HORARIA)
    
    # 1. CONTROL DE FIN DE SEMANA
    dia_semana = ahora.weekday()
    hora_actual = ahora.hour

    if (dia_semana == 4 and hora_actual >= 17) or (dia_semana == 5) or (dia_semana == 6 and hora_actual < 17):
        time.sleep(3600)
        continue

    # 2. ANÁLISIS DE ACTIVOS CON LÓGICA DE PRE-AVISO
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

            # --- LÓGICA OPTIMIZADA 58/42 ---

            # VENTAS (DOWN)
            if 56 <= rsi < 58 and estado_activos[simbolo] != 'preaviso_down':
                enviar_telegram(f"⚠️ **[PRE-AVISO]** {activo['display']} cerca de nivel 58 (Venta).", ID_PERSONAL)
                estado_activos[simbolo] = 'preaviso_down'

            elif rsi >= 58 and estado_activos[simbolo] == 'preaviso_down':
                conteo_alertas += 1
                msg = (f"🚀 **¡ENTRADA AHORA!** (#{conteo_alertas})\n"
                       f"💎 Par: **{activo['display']}**\n"
                       f"🔻 Dirección: **BAJA (DOWN)**\n"
                       f"⏳ Tiempo: **2 MINUTOS**\n"
                       f"🎯 RSI: {round(rsi, 2)}")
                enviar_telegram(msg, ID_PERSONAL)
                estado_activos[simbolo] = 'operado'
                time.sleep(125)

            # COMPRAS (UP)
            elif 42 < rsi <= 44 and estado_activos[simbolo] != 'preaviso_up':
                enviar_telegram(f"⚠️ **[PRE-AVISO]** {activo['display']} cerca de nivel 42 (Compra).", ID_PERSONAL)
                estado_activos[simbolo] = 'preaviso_up'

            elif rsi <= 42 and estado_activos[simbolo] == 'preaviso_up':
                conteo_alertas += 1
                msg = (f"🚀 **¡ENTRADA AHORA!** (#{conteo_alertas})\n"
                       f"💎 Par: **{activo['display']}**\n"
                       f"🟢 Dirección: **SUBE (UP)**\n"
                       f"⏳ Tiempo: **2 MINUTOS**\n"
                       f"🎯 RSI: {round(rsi, 2)}")
                enviar_telegram(msg, ID_PERSONAL)
                estado_activos[simbolo] = 'operado'
                time.sleep(125)

            # Zona neutral para resetear
            elif 46 < rsi < 54:
                estado_activos[simbolo] = 'esperando'

        except: continue

            
    time.sleep(1)
