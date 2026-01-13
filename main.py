import time
import requests
from datetime import datetime
import pytz 
from tradingview_ta import TA_Handler, Interval

# --- DATOS DE CONFIGURACIÓN ---
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

print(f"🚀 {BOT_NAME} - ASISTENTE DE ORO Y FOREX (Modo Volatilidad) iniciado.")

while True:
    ahora = datetime.now(MI_ZONA_HORARIA)
    
    # 1. CONTROL DE FIN DE SEMANA
    dia_semana = ahora.weekday()
    if (dia_semana == 4 and ahora.hour >= 17) or (dia_semana == 5) or (dia_semana == 6 and ahora.hour < 17):
        time.sleep(3600)
        continue

    # 2. ANÁLISIS DE MERCADO
    for activo in activos:
        try:
            handler = TA_Handler(symbol=activo['trading'], exchange="FX_IDC", screener="forex", interval=Interval.INTERVAL_1_MINUTE)
            analysis = handler.get_analysis()
            rsi = analysis.indicators["RSI"]
            simbolo = activo['trading']

            # --- LÓGICA DE VENTAS (BAJA) ---
            if 56 <= rsi < 58 and estado_activos[simbolo] != 'preaviso_down':
                enviar_telegram(f"⚠️ **[PRE-AVISO] {activo['display']}**\nRSI en {round(rsi, 2)}. Preparando VENTA.", ID_PERSONAL)
                estado_activos[simbolo] = 'preaviso_down'

            elif rsi >= 58 and estado_activos[simbolo] == 'preaviso_down':
                conteo_alertas += 1
                # Alerta Especial de Fuerza
                tipo_entrada = "🔥 FUERZA MÁXIMA" if rsi > 65 else "🚀 ENTRADA AHORA"
                
                msg = (f"{tipo_entrada} (#{conteo_alertas})\n"
                       f"──────────────────\n"
                       f"💎 Par: **{activo['display']}**\n"
                       f"🔻 Dirección: **BAJA (DOWN)**\n"
                       f"⏳ Tiempo: **2 MINUTOS**\n"
                       f"🎯 RSI: {round(rsi, 2)}\n"
                       f"──────────────────\n"
                       f"✅ *Copia y envía al canal.*")
                enviar_telegram(msg, ID_PERSONAL)
                estado_activos[simbolo] = 'operado'
                time.sleep(125) 

            # --- LÓGICA DE COMPRAS (UP) ---
            elif 42 < rsi <= 44 and estado_activos[simbolo] != 'preaviso_up':
                enviar_telegram(f"⚠️ **[PRE-AVISO] {activo['display']}**\nRSI en {round(rsi, 2)}. Preparando COMPRA.", ID_PERSONAL)
                estado_activos[simbolo] = 'preaviso_up'

            elif rsi <= 42 and estado_activos[simbolo] == 'preaviso_up':
                conteo_alertas += 1
                # Alerta Especial de Fuerza
                tipo_entrada = "🔥 FUERZA MÁXIMA" if rsi < 35 else "🚀 ENTRADA AHORA"
                
                msg = (f"{tipo_entrada} (#{conteo_alertas})\n"
                       f"──────────────────\n"
                       f"💎 Par: **{activo['display']}**\n"
                       f"🟢 Dirección: **SUBE (UP)**\n"
                       f"⏳ Tiempo: **2 MINUTOS**\n"
                       f"🎯 RSI: {round(rsi, 2)}\n"
                       f"──────────────────\n"
                       f"✅ *Copia y envía al canal.*")
                enviar_telegram(msg, ID_PERSONAL)
                estado_activos[simbolo] = 'operado'
                time.sleep(125)

            elif 46 < rsi < 54:
                estado_activos[simbolo] = 'esperando'

        except: continue
    time.sleep(1)
