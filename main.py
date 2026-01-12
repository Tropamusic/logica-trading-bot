import time
import requests
from datetime import datetime
import pytz 
from tradingview_ta import TA_Handler, Interval

# --- CONFIGURACIÓN ---
TOKEN = "8386038643:AAEngPQbBuu41WBWm7pCYQxm3yEowoJzYaw"
ID_PERSONAL = "6717348273" # EL BOT SOLO TE HABLARÁ A TI
BOT_NAME = "Lógica Trading 📊"

MI_ZONA_HORARIA = pytz.timezone('America/Caracas') 

def enviar_telegram(mensaje, destino):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": destino, "text": mensaje, "parse_mode": "Markdown"}
    try: requests.post(url, json=payload, timeout=10)
    except: pass

def analizar_privado(par_trading, par_display):
    handler = TA_Handler(symbol=par_trading, exchange="FX_IDC", screener="forex", interval=Interval.INTERVAL_1_MINUTE)
    try:
        analysis = handler.get_analysis()
        rsi = analysis.indicators["RSI"]
        
        # Mantenemos 60/40 para que tengas buenas oportunidades
        es_venta = rsi >= 60
        es_compra = rsi <= 40

        if es_compra or es_venta:
            direccion = "BAJA (DOWN) 🔻" if es_venta else "SUBE (UP) 🟢"
            
            # Formato listo para que solo le des a 'Reenviar'
            msg_para_ti = (f"⚠️ **NUEVA OPORTUNIDAD DETECTADA** ⚠️\n"
                           f"──────────────────\n"
                           f"💱 Par: **{par_display}**\n"
                           f"📈 Operación: **{direccion}**\n"
                           f"⏰ Tiempo: 2 Minutos\n"
                           f"──────────────────\n"
                           f"👉 *Lógica, ¿quieres enviarla al VIP?*")
            
            enviar_telegram(msg_para_ti, ID_PERSONAL)
            
            # Pausa de 3 minutos para que no te sature con el mismo par
            time.sleep(180) 
    except: pass

# --- ACTIVOS A ANALIZAR ---
activos = [
    {"trading": "EURUSD", "display": "EUR/USD"},
    {"trading": "GBPUSD", "display": "GBP/USD"},
    {"trading": "USDJPY", "display": "USD/JPY"},
    {"trading": "AUDUSD", "display": "AUD/USD"}
]

print("🤖 Modo Asistente Personal Activo...")

while True:
    # En este modo, el bot analiza siempre que esté encendido
    # Tú decides cuándo hacer caso y cuándo no.
    for activo in activos:
        analizar_privado(activo['trading'], activo['display'])
        time.sleep(5)
