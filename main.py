import time
import requests
from datetime import datetime, timedelta
from tradingview_ta import TA_Handler, Interval

# --- CONFIGURACIÓN (TUS DATOS SE MANTIENEN) ---
TOKEN = "8386038643:AAEngPQbBuu41WBWm7pCYQxm3yEowoJzYaw"
ID_PERSONAL = "6717348273"
ID_VIP = "-1003653748217"
ID_BITACORA = "-1003621701961"
LINK_CONTACTO = "https://t.me/+4bqyiiDGXTA4ZTRh"
BOT_NAME = "Lógica Trading 📊"

conteo_operaciones = 0
wins_totales = 0  
LIMITE_OPERACIONES = 4  
TIEMPO_DESCANSO_30MIN = 1800 # 30 minutos de descanso

def enviar_telegram(mensaje, destino):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": destino, "text": mensaje, "parse_mode": "Markdown"}
    try: requests.post(url, json=payload, timeout=10)
    except: pass

def analizar_sensible(par_trading, par_display):
    global conteo_operaciones, wins_totales
    handler = TA_Handler(
        symbol=par_trading, 
        exchange="FX_IDC", 
        screener="forex", 
        interval=Interval.INTERVAL_1_MINUTE
    )
    
    try:
        analysis = handler.get_analysis()
        rsi = analysis.indicators["RSI"]
        precio_entrada = analysis.indicators["close"]
        
        # --- LÓGICA SENSIBLE (60/40) ---
        # Envía señales más rápido para que el canal esté activo
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
            time.sleep(125) # Espera de la operación
            
            # Resultado
            nuevo_analisis = handler.get_analysis()
            precio_final = nuevo_analisis.indicators["close"]
            win = (es_venta and precio_final < precio_entrada) or (es_compra and precio_final > precio_entrada)
            
            if win:
                wins_totales += 1
                res_msg = f"✅ **OPERACIÓN GANADORA** ✅"
            else:
                res_msg = f"❌ **RESULTADO: LOSS** ❌"
            
            enviar_telegram(res_msg, ID_VIP)
            enviar_telegram(f"📑 *BITÁCORA*: {res_msg}\nMarcador: {wins_totales}W", ID_BITACORA)
            time.sleep(30) 

    except: pass

# --- INICIO ---
print(f"🚀 {BOT_NAME} Activo en Modo Sensible (60/40)")

activos = [
    {"trading": "EURUSD", "display": "EUR/USD(OTC)"},
    {"trading": "GBPUSD", "display": "GBP/USD(OTC)"},
    {"trading": "USDJPY", "display": "USD/JPY(OTC)"},
    {"trading": "AUDUSD", "display": "AUD/USD(OTC)"},
    {"trading": "EURJPY", "display": "EUR/JPY(OTC)"}
]

while True:
    # FILTRO DE HORARIO (Mañana, Tarde y Noche)
    hora_actual = datetime.now().hour
    # Mañana: 8-11 | Tarde: 14-17 | Noche: 20-23
    es_hora_de_operar = (8 <= hora_actual < 11) or (14 <= hora_actual < 17) or (20 <= hora_actual < 23)

    if es_hora_de_operar:
        if conteo_operaciones >= LIMITE_OPERACIONES:
            # Reporte con hora de regreso
            h_regreso = (datetime.now() + timedelta(minutes=30)).strftime('%H:%M')
            reporte = (f"📊 **SESIÓN FINALIZADA**\n\n✅ Ganadas: {wins_totales}\n"
                       f"⏳ Pausa de 30 min. Regreso: **{h_regreso}**\n\n📩 VIP: {LINK_CONTACTO}")
            enviar_telegram(reporte, ID_VIP)
            time.sleep(TIEMPO_DESCANSO_SEGUNDOS)
            conteo_operaciones = 0
            wins_totales = 0
            enviar_telegram(f"🚀 **{BOT_NAME} ACTIVO**\nBuscando entradas sensibles...", ID_VIP)

        for activo in activos:
            if conteo_operaciones < LIMITE_OPERACIONES:
                analizar_sensible(activo['trading'], activo['display'])
                time.sleep(5)
    else:
        # Fuera de horario espera 10 min antes de chequear de nuevo
        time.sleep(600)

    time.sleep(15)
