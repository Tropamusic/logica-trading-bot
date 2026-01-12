import time
import requests
from tradingview_ta import TA_Handler, Interval

# --- CONFIGURACIÓN ---
TOKEN = "8386038643:AAEngPQbBuu41WBWm7pCYQxm3yEowoJzYaw"
CHAT_ID = "6717348273" # Tu ID actualizado
CANAL_BITACORA = "-1003621701961" 
BOT_NAME = "Lógica Trading 📊"

conteo_operaciones = 0
wins_totales = 0  
LIMITE_OPERACIONES = 4  
TIEMPO_DESCANSO = 3600  

def enviar_telegram(mensaje, destino):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": destino, "text": mensaje, "parse_mode": "Markdown"}
    try: 
        requests.post(url, json=payload, timeout=10)
    except: 
        pass

def analizar_y_operar(par_trading, par_display):
    global conteo_operaciones, wins_totales
    handler = TA_Handler(symbol=par_trading, exchange="FX_IDC", screener="forex", interval=Interval.INTERVAL_1_MINUTE)
    
    try:
        analysis = handler.get_analysis()
        rsi = analysis.indicators["RSI"]
        precio_entrada = analysis.indicators["close"]
        
        # --- FASE 1: PRE-AVISO ---
        if (58 <= rsi < 63) or (42 >= rsi > 37):
            dir_pre = "VENDER (DOWN) 🔴" if rsi > 50 else "COMPRAR (UP) 🟢"
            enviar_telegram(f"⚠️ *PREPÁRATE PARA LA SEÑAL EN 2 MINUTOS*\nPair: {par_display}\nOperación: *{dir_pre}*", CHAT_ID)
            time.sleep(120) 
            
            # --- FASE 2: SEÑAL REAL ---
            nuevo_rsi = handler.get_analysis().indicators["RSI"]
            if (nuevo_rsi >= 60) or (nuevo_rsi <= 40):
                direccion = "🔻 TRADE HACIA ABAJO (DOWN)" if nuevo_rsi >= 60 else "⬆️ TRADE HACIA ARRIBA (UP)"
                
                msg = (f"💎 *{BOT_NAME} - SEÑAL VIP*\n"
                       f"──────────────────\n"
                       f"Pair: {par_display}\n"
                       f"Time: 2 min\n\n"
                       f"{direccion}\n"
                       f"──────────────────\n"
                       f"🔥 ¡ENTRA YA AHORA! 🔥")
                
                enviar_telegram(msg, CHAT_ID)
                conteo_operaciones += 1
                time.sleep(125)
                
                # --- FASE 3: RESULTADO ---
                precio_final = handler.get_analysis().indicators["close"]
                es_win = (nuevo_rsi >= 60 and precio_final < precio_entrada) or (nuevo_rsi <= 40 and precio_final > precio_entrada)
                
                res_msg = f"✅ *WIN - {par_display}* ✅" if es_win else f"❌ *LOSS - {par_display}* ❌"
                if es_win: wins_totales += 1
                
                enviar_telegram(res_msg, CHAT_ID)
                enviar_telegram(f"📑 *BITÁCORA*\n{res_msg}\nMarcador: {wins_totales}W", CANAL_BITACORA)
                time.sleep(10)
    except: pass

# --- INICIO ---
print(f"🚀 {BOT_NAME} OPERANDO")
enviar_telegram(f"🌟 *SISTEMA {BOT_NAME.upper()} EN LÍNEA*", CHAT_ID)

activos = [
    {"trading": "AUDUSD", "display": "AUD/USD(OTC)"},
    {"trading": "EURUSD", "display": "EUR/USD(OTC)"},
    {"trading": "GBPUSD", "display": "GBP/USD(OTC)"},
    {"trading": "USDJPY", "display": "USD/JPY(OTC)"}
]

while True:
    if conteo_operaciones >= LIMITE_OPERACIONES:
        enviar_telegram(f"📊 *RESUMEN*: {wins_totales} GANADAS\n⏳ Descanso de 1 hora activado.", CHAT_ID)
        time.sleep(TIEMPO_DESCANSO)
        conteo_operaciones = 0
        wins_totales = 0
        enviar_telegram(f"🚀 *{BOT_NAME}* Activo de nuevo.", CHAT_ID)

    for activo in activos:
        if conteo_operaciones < LIMITE_OPERACIONES:
            analizar_y_operar(activo['trading'], activo['display'])
    time.sleep(20)
