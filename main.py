import time
import requests
from datetime import datetime
import pytz 
from tradingview_ta import TA_Handler, Interval

# --- CONFIGURACIÓN ---
TOKEN = "8386038643:AAEngPQbBuu41WBWm7pCYQxm3yEowoJzYaw"
ID_PERSONAL = "6717348273" # Solo tú recibirás las alertas
BOT_NAME = "Lógica Trading 📊"

MI_ZONA_HORARIA = pytz.timezone('America/Caracas') 

def enviar_telegram(mensaje, destino):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": destino, "text": mensaje, "parse_mode": "Markdown"}
    try: requests.post(url, json=payload, timeout=10)
    except: pass

def analizar_asistente(par_trading, par_display):
    # Usamos exchange FX_IDC para mercado real y OANDA para mayor estabilidad
    handler = TA_Handler(symbol=par_trading, exchange="FX_IDC", screener="forex", interval=Interval.INTERVAL_1_MINUTE)
    
    try:
        analysis = handler.get_analysis()
        rsi = analysis.indicators["RSI"]
        recomendacion = analysis.summary["RECOMMENDATION"]
        precio = analysis.indicators["close"]
        
        # Filtro profesional: RSI + Recomendación fuerte de TradingView
        es_venta = rsi >= 60 and "SELL" in recomendacion
        es_compra = rsi <= 40 and "BUY" in recomendacion

        if es_compra or es_venta:
            dir_emoji = "🔴 VENTA" if es_venta else "🟢 COMPRA"
            accion = "BAJA 🔻" if es_venta else "SUBE 🟢"
            
            # Formato de alerta privada para TI
            msg_alerta = (f"🔔 **ALERTA DE ENTRADA** 🔔\n"
                          f"──────────────────\n"
                          f"💹 Par: **{par_display}**\n"
                          f"📉 RSI: {rsi:.2f}\n"
                          f"💰 Precio: {precio:.5f}\n"
                          f"⚡️ Acción: **{dir_emoji} ({accion})**\n"
                          f"──────────────────\n"
                          f"📢 *Copia y envía al VIP si te gusta la gráfica.*")
            
            enviar_telegram(msg_alerta, ID_PERSONAL)
            
            # Bloqueo de 5 min para ese par (no queremos spam en tu privado)
            time.sleep(300) 
    except: pass

# Activos sugeridos por su liquidez
activos = [
    {"trading": "EURUSD", "display": "EUR/USD"},
    {"trading": "GBPUSD", "display": "GBP/USD"},
    {"trading": "USDJPY", "display": "USD/JPY"},
    {"trading": "AUDUSD", "display": "AUD/USD"},
    {"trading": "EURJPY", "display": "EUR/JPY"}
]

print("🕵️‍♂️ Asistente personal en línea. Analizando mercados...")

while True:
    for activo in activos:
        analizar_asistente(activo['trading'], activo['display'])
        time.sleep(2) # Escaneo rápido entre pares
