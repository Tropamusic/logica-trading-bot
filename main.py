import time
import requests
from datetime import datetime
import pytz 
from tradingview_ta import TA_Handler, Interval

# --- DATOS DE LÓGICA TRADING ---
TOKEN = "8386038643:AAEngPQbBuu41WBWm7pCYQxm3yEowoJzYaw"
ID_PERSONAL = "6717348273"
BOT_NAME = "Lógica Trading 📊"
MI_ZONA_HORARIA = pytz.timezone('America/Caracas') 

# Control de flujo para evitar saturación
ultima_alerta_global = 0 
TIEMPO_ESPERA_GLOBAL = 180 # 3 minutos de silencio total entre señales

def enviar_telegram(mensaje, destino):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": destino, "text": mensaje, "parse_mode": "Markdown"}
    try: requests.post(url, json=payload, timeout=10)
    except: pass

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

print(f"🚀 {BOT_NAME} - MODO MÁXIMA SEGURIDAD (Sniper Elite) iniciado.")

while True:
    ahora_dt = datetime.now(MI_ZONA_HORARIA)
    ahora_ts = time.time()
    
    # Control Fin de Semana
    if (ahora_dt.weekday() == 4 and ahora_dt.hour >= 17) or (ahora_dt.weekday() == 5) or (ahora_dt.weekday() == 6 and ahora_dt.hour < 17):
        time.sleep(3600)
        continue

    # Solo analiza si ha pasado el tiempo de enfriamiento global
    if ahora_ts - ultima_alerta_global > TIEMPO_ESPERA_GLOBAL:
        for activo in activos:
            try:
                handler = TA_Handler(symbol=activo['trading'], exchange="FX_IDC", screener="forex", interval=Interval.INTERVAL_1_MINUTE)
                analysis = handler.get_analysis()
                rsi = analysis.indicators["RSI"]
                precio = analysis.indicators["close"]

                # FILTRO DE SEGURIDAD: Solo niveles de alta precisión 60/40
                es_venta = rsi >= 60
                es_compra = rsi <= 40

                if es_venta or es_compra:
                    direccion = "BAJA (DOWN) 🔻" if es_venta else "SUBE (UP) 🟢"
                    emoji = "🎯" if (40 < rsi < 60) else "🔥 ¡ALTA PRECISIÓN!"
                    
                    msg = (f"{emoji} **SEÑAL SNIPER ELITE**\n"
                           f"──────────────────\n"
                           f"💎 Par: **{activo['display']}**\n"
                           f"📈 Operación: **{direccion}**\n"
                           f"💵 Precio: `{round(precio, 5)}`\n"
                           f"📊 RSI: {round(rsi, 2)}\n"
                           f"⏳ Tiempo: **2 MINUTOS**\n"
                           f"──────────────────\n"
                           f"⚠️ *Enfriamiento activo: 3 min sin más alertas.*")
                    
                    enviar_telegram(msg, ID_PERSONAL)
                    ultima_alerta_global = time.time() # Activa el bloqueo global
                    break # Sale del bucle de activos para esperar el enfriamiento

            except: continue
    
    time.sleep(5) # Escaneo pausado para no saturar la conexión
