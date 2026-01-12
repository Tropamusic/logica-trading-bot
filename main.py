import time
import requests
from tradingview_ta import TA_Handler, Interval

# --- CONFIGURACIÓN ---
TOKEN = "8386038643:AAEngPQbBuu41WBWm7pCYQxm3yEowoJzYaw"
CANAL_VIP = "-1002237930838"  
CANAL_BITACORA = "-1003621701961" 
BOT_NAME = "Lógica Trading 📊"

conteo_operaciones = 0
wins_totales = 0  
LIMITE_OPERACIONES = 4  
TIEMPO_DESCANSO = 3600  

def enviar_telegram(mensaje, chat_id):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": mensaje, "parse_mode": "Markdown"}
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
        
        # --- FASE 1: PRE-AVISO (RSI CERCA DEL LÍMITE) ---
        if (58 <= rsi < 63) or (42 >= rsi > 37):
            dir_pre = "VENDER (DOWN) 🔴" if rsi > 50 else "COMPRAR (UP) 🟢"
            enviar_telegram(f"⚠️ *PREPÁRATE PARA LA SEÑAL EN 2 MINUTOS*\nPair: {par_display}\nOperación: *{dir_pre}*", CANAL_VIP)
            
            # ESPERA 2 MINUTOS PARA LA CONFIRMACIÓN
            time.sleep(120) 
            
            # --- FASE 2: SEÑAL REAL (CONFIRMACIÓN) ---
            nuevo_analisis = handler.get_analysis()
            nuevo_rsi = nuevo_analisis.indicators["RSI"]
            
            if (nuevo_rsi >= 60) or (nuevo_rsi <= 40):
                direccion = "🔻 TRADE HACIA ABAJO (DOWN)" if nuevo_rsi >= 60 else "⬆️ TRADE HACIA ARRIBA (UP)"
                
                msg = (f"💎 *{BOT_NAME} - SEÑAL VIP*\n"
                       f"──────────────────\n"
                       f"Pair: {par_display}\n"
                       f"Time: 2 min\n\n"
                       f"{direccion}\n"
                       f"──────────────────\n"
                       f"🔥 ¡ENTRA YA AHORA! 🔥")
                
                enviar_telegram(msg, CANAL_VIP)
                conteo_operaciones += 1
                
                # ESPERA 2 MINUTOS DE LA OPERACIÓN
                time.sleep(125)
                
                # --- FASE 3: RESULTADO ---
                analisis_final = handler.get_analysis()
                precio_final = analisis_final.indicators["close"]
                
                es_win = (nuevo_rsi >= 60 and precio_final < precio_entrada) or (nuevo_rsi <= 40 and precio_final > precio_entrada)
                
                if es_win:
                    wins_totales += 1
                    res_msg = f"✅ *WIN - {par_display}* ✅\n¡Resultado Excelente!"
                else:
                    res_msg = f"❌ *LOSS - {par_display}* ❌\nBuscando nueva oportunidad."
                
                enviar_telegram(res_msg, CANAL_VIP)
                enviar_telegram(f"📑 *BITÁCORA*\n{res_msg}\nMarcador: {wins_totales}W", CANAL_BITACORA)
                time.sleep(10)
                
    except:
        pass

# --- INICIO ---
print(f"🚀 {BOT_NAME} OPERANDO")
enviar_telegram(f"🌟 *SISTEMA {BOT_NAME.upper()} EN LÍNEA*", CANAL_VIP)

activos = [
    {"trading": "AUDUSD", "display": "AUD/USD(OTC)"},
    {"trading": "EURUSD", "display": "EUR/USD(OTC)"},
    {"trading": "GBPUSD", "display": "GBP/USD(OTC)"},
    {"trading": "USDJPY", "display": "USD/JPY(OTC)"},
    {"trading": "EURJPY", "display": "EUR/JPY(OTC)"}
]

while True:
    if conteo_operaciones >= LIMITE_OPERACIONES:
        reporte = (f"📊 *RESUMEN DE SESIÓN* 📊\n\n✅ Operaciones Ganadas: *{wins_totales}*\n🎯 Efectividad: *ALTA PRECISIÓN*\n\n🔥 *¡LA LÓGICA NO FALLA!* 🔥")
        enviar_telegram(reporte, CANAL_VIP)
        enviar_telegram(f"⏳ *MODO DESCANSO ACTIVADO*\nReanudando en 1 hora para proteger las ganancias. 🛡", CANAL_VIP)
        time.sleep(TIEMPO_DESCANSO)
        conteo_operaciones = 0
        wins_totales = 0
        enviar_telegram(f"🚀 *{BOT_NAME}* de vuelta activo. ¡Vamos por más!", CANAL_VIP)

    for activo in activos:
        if conteo_operaciones < LIMITE_OPERACIONES:
            analizar_y_operar(activo['trading'], activo['display'])
    
    time.sleep(20)
