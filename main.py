import time
import requests
import threading
from datetime import datetime
import pytz 
from tradingview_ta import TA_Handler, Interval

# --- DATOS DE CONFIGURACIÓN ---
TOKEN = "8386038643:AAEngPQbBuu41WBWm7pCYQxm3yEowoJzYaw"
ID_PERSONAL = "6717348273"
BOT_NAME = "Lógica Trading 📊"
MI_ZONA_HORARIA = pytz.timezone('America/Caracas') 

# --- VARIABLES DE CONTROL ---
conteo_alertas = 0
estado_activos = {}

def enviar_telegram(mensaje, destino):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": destino, "text": mensaje, "parse_mode": "Markdown"}
    try:
        requests.post(url, json=payload, timeout=10)
    except:
        pass

# --- LISTA DE ACTIVOS (MERCADO REAL + ORO) ---
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

# Inicializar estados de los activos
for a in activos:
    estado_activos[a['trading']] = 'esperando'

print(f"🚀 {BOT_NAME} iniciado con estrategia 58/42 (Modo Asistente)")

# --- BUCLE PRINCIPAL ---
while True:
    ahora = datetime.now(MI_ZONA_HORARIA)
    
    # 1. CONTROL DE FIN DE SEMANA (CIERRE REAL)
    dia_semana = ahora.weekday()
    hora_actual = ahora.hour

    if (dia_semana == 4 and hora_actual >= 17) or (dia_semana == 5) or (dia_semana == 6 and hora_actual < 17):
        time.sleep(3600)
        continue

    # 2. ANÁLISIS DE MERCADO
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

            # --- LÓGICA DE VENTAS (Nivel 58) ---
            if 56 <= rsi < 58 and estado_activos[simbolo] != 'preaviso_down':
                msg_pre = (f"⚠️ **[PRE-AVISO] Lógica Trading**\n"
                           f"──────────────────\n"
                           f"💱 Par: **{activo['display']}**\n"
                           f"📉 Operación: **Posible VENTA**\n"
                           f"📊 RSI: {round(rsi, 2)}\n"
                           f"📢 *Ten listo el broker...*")
                enviar_telegram(msg_pre, ID_PERSONAL)
                estado_activos[simbolo] = 'preaviso_down'

            elif rsi >= 58 and estado_activos[simbolo] == 'preaviso_down':
                conteo_alertas += 1
                msg_final = (f"🚀 **¡ENTRADA AHORA!** (Señal #{conteo_alertas})\n"
                             f"──────────────────\n"
                             f"💎 Par: **{activo['display']}**\n"
                             f"🔻 Dirección: **BAJA (DOWN)**\n"
                             f"⏳ Tiempo: **2 MINUTOS**\n"
                             f"🎯 RSI: {round(rsi, 2)}\n"
                             f"──────────────────\n"
                             f"✅ *Copia y envía al canal.*")
                enviar_telegram(msg_final, ID_PERSONAL)
                estado_activos[simbolo] = 'operado'
                time.sleep(125) # Pausa para finalizar la operación

            # --- LÓGICA DE COMPRAS (Nivel 42) ---
            elif 42 < rsi <= 44 and estado_activos[simbolo] != 'preaviso_up':
                msg_pre = (f"⚠️ **[PRE-AVISO] Lógica Trading**\n"
                           f"──────────────────\n"
                           f"💱 Par: **{activo['display']}**\n"
                           f"🟢 Operación: **Posible COMPRA**\n"
                           f"📊 RSI: {round(rsi, 2)}\n"
                           f"📢 *Ten listo el broker...*")
                enviar_telegram(msg_pre, ID_PERSONAL)
                estado_activos[simbolo] = 'preaviso_up'

            elif rsi <= 42 and estado_activos[simbolo] == 'preaviso_up':
                conteo_alertas += 1
                msg_final = (f"🚀 **¡ENTRADA AHORA!** (Señal #{conteo_alertas})\n"
                             f"──────────────────\n"
                             f"💎 Par: **{activo['display']}**\n"
                             f"🟢 Dirección: **SUBE (UP)**\n"
                             f"⏳ Tiempo: **2 MINUTOS**\n"
                             f"🎯 RSI: {round(rsi, 2)}\n"
                             f"──────────────────\n"
                             f"✅ *Copia y envía al canal.*")
                enviar_telegram(msg_final, ID_PERSONAL)
                estado_activos[simbolo] = 'operado'
                time.sleep(125)

            # --- RESETEAR ESTADO ---
            elif 46 < rsi < 54:
                estado_activos[simbolo] = 'esperando'

        except:
            continue
            
    time.sleep(1) # Escaneo constante
