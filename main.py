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

            # --- LÓGICA PARA VENTAS (DOWN) ---
            # Pre-aviso entre 58 y 60
            if 58 <= rsi < 60 and estado_activos[simbolo] != 'preaviso_down':
                msg_pre = (f"⚠️ **[PRE-AVISO] Lógica Trading**\n"
                           f"──────────────────\n"
                           f"💱 Par: **{activo['display']}**\n"
                           f"📉 Operación: **Posible VENTA (BAJA)**\n"
                           f"📊 RSI actual: {round(rsi, 2)}\n"
                           f"📢 *Ten listo el broker...*")
                enviar_telegram(msg_pre, ID_PERSONAL)
                estado_activos[simbolo] = 'preaviso_down'

            # Señal final en 60 o más
            elif rsi >= 60 and estado_activos[simbolo] == 'preaviso_down':
                conteo_alertas += 1
                msg_final = (f"🚀 **¡ENTRADA AHORA!** (Señal #{conteo_alertas})\n"
                             f"──────────────────\n"
                             f"💎 Par: **{activo['display']}**\n"
                             f"🔻 Dirección: **BAJA (DOWN)**\n"
                             f"⏳ Tiempo: **2 MINUTOS**\n"
                             f"🎯 RSI: {round(rsi, 2)}\n"
                             f"──────────────────\n"
                             f"✅ *Copia y pega en el Canal VIP.*")
                enviar_telegram(msg_final, ID_PERSONAL)
                estado_activos[simbolo] = 'operado'
                time.sleep(125) # Espera a que pase la operación para ese activo

            # --- LÓGICA PARA COMPRAS (UP) ---
            # Pre-aviso entre 40 y 42
            elif 40 < rsi <= 42 and estado_activos[simbolo] != 'preaviso_up':
                msg_pre = (f"⚠️ **[PRE-AVISO] Lógica Trading**\n"
                           f"──────────────────\n"
                           f"💱 Par: **{activo['display']}**\n"
                           f"🟢 Operación: **Posible COMPRA (SUBE)**\n"
                           f"📊 RSI actual: {round(rsi, 2)}\n"
                           f"📢 *Ten listo el broker...*")
                enviar_telegram(msg_pre, ID_PERSONAL)
                estado_activos[simbolo] = 'preaviso_up'

            # Señal final en 40 o menos
            elif rsi <= 40 and estado_activos[simbolo] == 'preaviso_up':
                conteo_alertas += 1
                msg_final = (f"🚀 **¡ENTRADA AHORA!** (Señal #{conteo_alertas})\n"
                             f"──────────────────\n"
                             f"💎 Par: **{activo['display']}**\n"
                             f"🟢 Dirección: **SUBE (UP)**\n"
                             f"⏳ Tiempo: **2 MINUTOS**\n"
                             f"🎯 RSI: {round(rsi, 2)}\n"
                             f"──────────────────\n"
                             f"✅ *Copia y pega en el Canal VIP.*")
                enviar_telegram(msg_final, ID_PERSONAL)
                estado_activos[simbolo] = 'operado'
                time.sleep(125)

            # Resetear estado si el RSI vuelve a zona neutral (entre 45 y 55)
            elif 45 < rsi < 55:
                estado_activos[simbolo] = 'esperando'

        except Exception as e:
            continue
            
    time.sleep(1)
