import time
import requests
from datetime import datetime, timedelta
from tradingview_ta import TA_Handler, Interval

# --- CONFIGURACIÓN ---
TOKEN = "8386038643:AAEngPQbBuu41WBWm7pCYQxm3yEowoJzYaw"
ID_PERSONAL = "6717348273"
ID_VIP = "-1003653748217"
ID_BITACORA = "-1003621701961"
LINK_VIP = "https://t.me/+4bqyiiDGXTA4ZTRh"
LINK_RESULTADOS = "https://t.me/LogicaTradingResultados"

BOT_NAME = "Lógica Trading 📊"

conteo_operaciones = 0
wins_totales = 0  
LIMITE_OPERACIONES = 4  
TIEMPO_DESCANSO_SEGUNDOS = 1800  # 30 minutos exactos

def enviar_telegram(mensaje, destino, botones=None):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": destino, 
        "text": mensaje, 
        "parse_mode": "Markdown",
        "disable_web_page_preview": True
    }
    if botones:
        payload["reply_markup"] = {"inline_keyboard": botones}
    try: requests.post(url, json=payload, timeout=10)
    except: pass

def analizar_sensible(par_trading, par_display):
    global conteo_operaciones, wins_totales
    handler = TA_Handler(symbol=par_trading, exchange="FX_IDC", screener="forex", interval=Interval.INTERVAL_1_MINUTE)
    
    try:
        analysis = handler.get_analysis()
        rsi = analysis.indicators["RSI"]
        precio_entrada = analysis.indicators["close"]
        
        # --- AJUSTE DE SENSIBILIDAD (60/40) ---
        # Esto enviará señales más seguido que el nivel 65/35
        es_venta = rsi >= 60
        es_compra = rsi <= 40

        if es_compra or es_venta:
            direccion = "BAJA (DOWN) 🔻" if es_venta else "SUBE (UP) 🟢"
            
            msg_señal = (f"💎 **{BOT_NAME} - SEÑAL VIP** 💎\n"
                         f"──────────────────\n"
                         f"💱 Par: {par_display}\n"
                         f"⏰ Tiempo: 2 Minutos\n"
                         f"📈 Operación: **{direccion}**\n"
                         f"──────────────────\n"
                         f"🔥 **¡ENTRA YA AHORA!** 🔥")
            
            enviar_telegram(msg_señal, ID_VIP)
            enviar_telegram(msg_señal, ID_PERSONAL)
            
            conteo_operaciones += 1
            time.sleep(125) # Tiempo de la operación
            
            # Resultado
            nuevo_analisis = handler.get_analysis()
            precio_final = nuevo_analisis.indicators["close"]
            win = (es_venta and precio_final < precio_entrada) or (es_compra and precio_final > precio_entrada)
            
            res_msg = f"✅ **OPERACIÓN GANADORA** ✅" if win else f"❌ **RESULTADO: LOSS** ❌"
            if win: wins_totales += 1
            
            enviar_telegram(res_msg, ID_VIP)
            enviar_telegram(f"📑 *BITÁCORA*: {res_msg}\nMarcador: {wins_totales}W", ID_BITACORA)
            time.sleep(30)
    except: pass

# --- INICIO ---
print(f"🚀 {BOT_NAME} Activo - Modo SENSIBLE (60/40)")

activos = [
    {"trading": "EURUSD", "display": "EUR/USD(OTC)"},
    {"trading": "GBPUSD", "display": "GBP/USD(OTC)"},
    {"trading": "USDJPY", "display": "USD/JPY(OTC)"},
    {"trading": "AUDUSD", "display": "AUD/USD(OTC)"},
    {"trading": "EURJPY", "display": "EUR/JPY(OTC)"}
]

while True:
    # Verificación de Horarios (Mañana, Tarde, Noche)
    ahora = datetime.now().hour
    # Mañana: 8-11 | Tarde: 14-17 | Noche: 20-23
    en_horario = (8 <= ahora < 11) or (14 <= ahora < 17) or (20 <= ahora < 23)

    if en_horario:
        if conteo_operaciones >= LIMITE_OPERACIONES:
            hora_regreso = (datetime.now() + timedelta(minutes=30)).strftime('%H:%M')
            reporte = (f"📊 **SESIÓN FINALIZADA**\n\n✅ Ganadas: {wins_totales}\n"
                       f"⏳ Pausa de 30 min. Regreso: **{hora_regreso}**\n\n📩 VIP: {LINK_VIP}")
            enviar_telegram(reporte, ID_VIP)
            time.sleep(TIEMPO_DESCANSO_SEGUNDOS)
            conteo_operaciones = 0
            wins_totales = 0
            enviar_telegram(f"🚀 **{BOT_NAME} DE VUELTA**\nBuscando señales sensibles...", ID_VIP)

        for activo in activos:
            if conteo_operaciones < LIMITE_OPERACIONES:
                analizar_sensible(activo['trading'], activo['display'])
                time.sleep(5)
    else:
        # Si no es hora de operar, espera y avisa en consola
        time.sleep(600) 
    
    time.sleep(15)
