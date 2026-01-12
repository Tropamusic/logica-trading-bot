import time
import requests
from datetime import datetime, timedelta
import pytz # Para manejar el horario de tu país
from tradingview_ta import TA_Handler, Interval

# --- CONFIGURACIÓN ---
TOKEN = "8386038643:AAEngPQbBuu41WBWm7pCYQxm3yEowoJzYaw"
ID_PERSONAL = "6717348273"
ID_VIP = "-1003653748217"
ID_BITACORA = "-1003621701961"
LINK_VIP = "https://t.me/+4bqyiiDGXTA4ZTRh"
LINK_RESULTADOS = "https://t.me/LogicaTradingResultados"

# Configura tu zona horaria (Ej: 'America/Caracas', 'America/Bogota', 'America/Mexico_City')
ZONA_HORARIA = pytz.timezone('America/Caracas') 

BOT_NAME = "Lógica Trading 📊"
conteo_operaciones = 0
wins_totales = 0  
LIMITE_OPERACIONES = 4  
TIEMPO_DESCANSO_30MIN = 1800 

def enviar_telegram(mensaje, destino, botones=None):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": destino, "text": mensaje, "parse_mode": "Markdown", "disable_web_page_preview": True}
    if botones: payload["reply_markup"] = {"inline_keyboard": botones}
    try: requests.post(url, json=payload, timeout=10)
    except: pass

def esta_en_horario():
    # Define aquí tus rangos de horas
    ahora = datetime.now(ZONA_HORARIA).hour
    # Mañana (8-11), Tarde (14-17), Noche (20-23)
    if (8 <= ahora < 11) or (14 <= ahora < 17) or (20 <= ahora < 23):
        return True
    return False

def analizar_y_operar(par_trading, par_display):
    global conteo_operaciones, wins_totales
    handler = TA_Handler(symbol=par_trading, exchange="FX_IDC", screener="forex", interval=Interval.INTERVAL_1_MINUTE)
    try:
        analysis = handler.get_analysis()
        rsi = analysis.indicators["RSI"]
        precio_entrada = analysis.indicators["close"]
        
        if (rsi >= 65) or (rsi <= 35):
            direccion = "BAJA (DOWN) 🔻" if rsi >= 65 else "SUBE (UP) 🟢"
            msg = (f"💎 **{BOT_NAME} - SEÑAL VIP** 💎\n"
                   f"──────────────────\n"
                   f"💱 Par: {par_display}\n"
                   f"⏰ Tiempo: 2 Minutos\n"
                   f"📈 Operación: **{direccion}**\n"
                   f"──────────────────\n"
                   f"🔥 **¡ENTRA YA AHORA!** 🔥")
            enviar_telegram(msg, ID_VIP)
            enviar_telegram(msg, ID_PERSONAL)
            
            conteo_operaciones += 1
            time.sleep(125)
            
            p_final = handler.get_analysis().indicators["close"]
            win = (rsi >= 65 and p_final < precio_entrada) or (rsi <= 35 and p_final > precio_entrada)
            res = "✅ **OPERACIÓN GANADORA** ✅" if win else "❌ **RESULTADO: LOSS** ❌"
            if win: wins_totales += 1
            
            enviar_telegram(res, ID_VIP)
            enviar_telegram(f"📑 *BITÁCORA*: {res}\nMarcador: {wins_totales}W", ID_BITACORA)
            time.sleep(30)
    except: pass

# --- BUCLE PRINCIPAL ---
print(f"🚀 {BOT_NAME} Activo con Horarios Programados.")

activos = [
    {"trading": "EURUSD", "display": "EUR/USD(OTC)"},
    {"trading": "GBPUSD", "display": "GBP/USD(OTC)"},
    {"trading": "USDJPY", "display": "USD/JPY(OTC)"},
    {"trading": "AUDUSD", "display": "AUD/USD(OTC)"}
]

while True:
    if esta_en_horario():
        if conteo_operaciones >= LIMITE_OPERACIONES:
            h_regreso = (datetime.now(ZONA_HORARIA) + timedelta(minutes=30)).strftime('%H:%M')
            reporte = (f"📊 **SESIÓN FINALIZADA**\n\n✅ Ganadas: {wins_totales}\n"
                       f"⏳ Pausa de 30 min. Regreso: **{h_regreso}**")
            enviar_telegram(reporte, ID_VIP)
            time.sleep(TIEMPO_DESCANSO_30MIN)
            conteo_operaciones = 0
            wins_totales = 0
        
        for activo in activos:
            if conteo_operaciones < LIMITE_OPERACIONES:
                analizar_y_operar(activo['trading'], activo['display'])
        time.sleep(20)
    else:
        # Si no es hora de operar, el bot espera 15 min para volver a chequear el horario
        print("💤 Fuera de horario. Bot en espera...")
        time.sleep(900) 
