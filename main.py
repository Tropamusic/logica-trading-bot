import time
import requests
import threading
from datetime import datetime
import pytz 
from tradingview_ta import TA_Handler, Interval

# --- DATOS DE LÓGICA TRADING ---
TOKEN = "8386038643:AAEngPQbBuu41WBWm7pCYQxm3yEowoJzYaw"
ID_PERSONAL = "6717348273"
LINK_VIP = "https://t.me/+tYm_D39iB8YxZDRh"
BOT_NAME = "Lógica Trading 📊"

MI_ZONA_HORARIA = pytz.timezone('America/Caracas') 

conteo_alertas = 0
ultima_senal_time = time.time()

def enviar_telegram(mensaje, destino):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": destino, "text": mensaje, "parse_mode": "Markdown"}
    try: requests.post(url, json=payload, timeout=10)
    except: pass

# --- LISTA MAESTRA DE ACTIVOS (FOREX + ORO) ---
activos = [
    {"trading": "XAUUSD", "display": "ORO (XAU/USD) ✨"}, # ¡Añadido!
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

print(f"🚀 {BOT_NAME} Iniciado con {len(activos)} activos.")

# --- BUCLE DE ANÁLISIS TOTAL ---
while True:
    # Aviso de "Bot Activo" cada 10 minutos si no hay señales
    tiempo_actual = time.time()
    if (tiempo_actual - ultima_senal_time) >= 600: # 600 segundos = 10 min
        enviar_telegram("🔍 **Lógica Trading Informa:** Sigo analizando los mercados en tiempo real. Esperando el punto exacto 60/40...", ID_PERSONAL)
        ultima_senal_time = tiempo_actual

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
            precio_entrada = analysis.indicators["close"]
            
            # PRECISIÓN 60/40
            es_venta = 60 <= rsi <= 65
            es_compra = 35 <= rsi <= 40
            
            if es_venta or es_compra:
                conteo_alertas += 1
                ultima_senal_time = time.time() # Reinicia el cronómetro de inactividad
                direccion = "BAJA (DOWN) 🔻" if es_venta else "SUBE (UP) 🟢"
                
                msg = (f"🎯 **SEÑAL DE PRECISIÓN #{conteo_alertas}**\n"
                       f"──────────────────\n"
                       f"💱 Par: **{activo['display']}**\n"
                       f"📈 Operación: **{direccion}**\n"
                       f"📊 RSI actual: **{round(rsi, 2)}**\n"
                       f"⏰ Tiempo: 2 Minutos\n"
                       f"──────────────────\n"
                       f"📢 **Lógica Trading: ¡Nivel confirmado!**")
                enviar_telegram(msg, ID_PERSONAL)
                
                time.sleep(125) # Expiración de 2 min
                
                check = handler.get_analysis()
                precio_final = check.indicators["close"]
                ganada = (es_venta and precio_final < precio_entrada) or (es_compra and precio_final > precio_entrada)
                
                if ganada:
                    res_txt = f"✅ **¡WIN! EN {activo['display']}** ✅\n🔥 *Lógica Trading: Operación Exitosa.*"
                else:
                    res_txt = f"❌ **RESULTADO: LOSS** ❌\n📊 Par: {activo['display']}\nMercado volátil. Buscando la siguiente..."
                
                enviar_telegram(res_txt, ID_PERSONAL)
                
                # Pausa de 5 min para tranquilidad del canal
                time.sleep(300) 
                
        except: continue
    time.sleep(1)
