import time
import requests
from datetime import datetime, timedelta
import pytz 
from tradingview_ta import TA_Handler, Interval

# --- CONFIGURACIÓN ---
TOKEN = "8386038643:AAEngPQbBuu41WBWm7pCYQxm3yEowoJzYaw"
ID_PERSONAL = "6717348273"
ID_VIP = "-1003653748217"
ID_BITACORA = "-1003621701961"
LINK_CONTACTO = "https://t.me/+4bqyiiDGXTA4ZTRh"
BOT_NAME = "Lógica Trading 📊"

MI_ZONA_HORARIA = pytz.timezone('America/Caracas') 

conteo_operaciones = 0
wins_totales = 0  
LIMITE_OPERACIONES = 4  
TIEMPO_DESCANSO = 1800 

# Variable para no repetir el aviso de 5 min
aviso_enviado = False

def enviar_telegram(mensaje, destino):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": destino, "text": mensaje, "parse_mode": "Markdown", "disable_web_page_preview": True}
    try: requests.post(url, json=payload, timeout=10)
    except: pass

def analizar_sensible(par_trading, par_display):
    global conteo_operaciones, wins_totales
    handler = TA_Handler(symbol=par_trading, exchange="FX_IDC", screener="forex", interval=Interval.INTERVAL_1_MINUTE)
    try:
        analysis = handler.get_analysis()
        rsi = analysis.indicators["RSI"]
        precio_entrada = analysis.indicators["close"]
        
        if (rsi >= 60) or (rsi <= 40):
            dir_txt = "BAJA (DOWN) 🔻" if rsi >= 60 else "SUBE (UP) 🟢"
            msg = (f"💎 **{BOT_NAME} - SEÑAL VIP** 💎\n"
                   f"──────────────────\n"
                   f"💱 Par: {par_display}\n"
                   f"⏰ Tiempo: 2 Minutos\n"
                   f"📈 Operación: **{dir_txt}**\n"
                   f"──────────────────\n"
                   f"🔥 **¡ENTRA YA AHORA!** 🔥")
            enviar_telegram(msg, ID_VIP)
            enviar_telegram(msg, ID_PERSONAL)
            conteo_operaciones += 1
            time.sleep(125)
            
            p_final = handler.get_analysis().indicators["close"]
            win = (rsi >= 60 and p_final < precio_entrada) or (rsi <= 40 and p_final > precio_entrada)
            res = "✅ **OPERACIÓN GANADORA** ✅" if win else "❌ **RESULTADO: LOSS** ❌"
            if win: wins_totales += 1
            
            enviar_telegram(res, ID_VIP)
            enviar_telegram(f"📑 *BITÁCORA*: {res}\n📊 {par_display} | E: {precio_entrada:.5f} -> S: {p_final:.5f}", ID_BITACORA)
            time.sleep(30) 
    except: pass

# --- BUCLE PRINCIPAL ---
print(f"🚀 {BOT_NAME} en línea. Esperando sesión...")

activos = [
    {"trading": "EURUSD", "display": "EUR/USD(OTC)"},
    {"trading": "GBPUSD", "display": "GBP/USD(OTC)"},
    {"trading": "USDJPY", "display": "USD/JPY(OTC)"},
    {"trading": "AUDUSD", "display": "AUD/USD(OTC)"}
]

while True:
    ahora = datetime.now(MI_ZONA_HORARIA)
    hora = ahora.hour
    minuto = ahora.minute

    # 1. LÓGICA DE AVISO (5 minutos antes de cada sesión)
    if (hora in [7, 13, 19]) and (minuto == 55) and not aviso_enviado:
        msg_aviso = (f"⏳ **¡PREPÁRENSE! 5 MINUTOS...**\n\n"
                     f"La sesión de {BOT_NAME} está por iniciar. Abran sus brokers y verifiquen su conexión. 🚀")
        enviar_telegram(msg_aviso, ID_VIP)
        aviso_enviado = True
    
    # Resetear el aviso cuando inicie la sesión
    if minuto == 0:
        aviso_enviado = False

    # 2. LÓGICA DE OPERACIÓN
    es_hora = (8 <= hora < 11) or (14 <= hora < 17) or (20 <= hora < 23)

    if es_hora:
        if conteo_operaciones >= LIMITE_OPERACIONES:
            h_regreso = (ahora + timedelta(minutes=30)).strftime('%I:%M %p')
            reporte = (f"📊 **SESIÓN FINALIZADA**\n\n✅ Ganadas: {wins_totales}\n⏳ Regreso: **{h_regreso}**")
            enviar_telegram(reporte, ID_VIP)
            time.sleep(TIEMPO_DESCANSO)
            conteo_operaciones = 0
            wins_totales = 0
        
        for activo in activos:
            if conteo_operaciones < LIMITE_OPERACIONES:
                analizar_sensible(activo['trading'], activo['display'])
                time.sleep(5)
    else:
        time.sleep(20) # Revisa cada 20 segundos
