import time
import requests
from tradingview_ta import TA_Handler, Interval

# --- TUS CONFIGURACIONES (SIN CAMBIOS) ---
TOKEN = "8386038643:AAEngPQbBuu41WBWm7pCYQxm3yEowoJzYaw"
ID_PERSONAL = "6717348273"      # El ID que tú pusiste
ID_VIP = "-1002237930838"       # Tu Canal VIP
ID_BITACORA = "-1003621701961"  # Tu Bitácora
BOT_NAME = "Lógica Trading 📊"

conteo_operaciones = 0
wins_totales = 0  
LIMITE_OPERACIONES = 4  
TIEMPO_DESCANSO = 3600  

def enviar_telegram(mensaje, destino):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": destino, "text": mensaje, "parse_mode": "Markdown"}
    try: requests.post(url, json=payload, timeout=10)
    except: pass

def analizar_y_operar(par_trading, par_display):
    global conteo_operaciones, wins_totales
    handler = TA_Handler(symbol=par_trading, exchange="FX_IDC", screener="forex", interval=Interval.INTERVAL_1_MINUTE)
    
    try:
        analysis = handler.get_analysis()
        rsi = analysis.indicators["RSI"]
        precio_entrada = analysis.indicators["close"]
        
        # 1. SEÑAL PARA OPERAR (Se activa con RSI 60/40 o el nivel que prefieras)
        if (rsi >= 60) or (rsi <= 40):
            direccion = "BAJA (DOWN) 🔻" if rsi >= 60 else "SUBE (UP) 🟢"
            
            # Formato de Señal Real
            msg_señal = (f"💎 **{BOT_NAME} - SEÑAL VIP** 💎\n"
                         f"──────────────────\n"
                         f"💱 Par: {par_display}\n"
                         f"⏰ Tiempo: 2 Minutos\n"
                         f"📈 Operación: **{direccion}**\n"
                         f"──────────────────\n"
                         f"🔥 **¡ENTRA YA AHORA!** 🔥")
            
            # ENVIAR SEÑAL AL VIP Y A TU ID PERSONAL
            enviar_telegram(msg_señal, ID_VIP)
            enviar_telegram(msg_señal, ID_PERSONAL)
            
            conteo_operaciones += 1
            
            # 2. ESPERA DE LA OPERACIÓN (Aquí el bot espera los 2 min)
            time.sleep(125)
            
            # 3. ENVÍO DEL RESULTADO
            analisis_final = handler.get_analysis()
            precio_final = analisis_final.indicators["close"]
            es_win = (rsi >= 60 and precio_final < precio_entrada) or (rsi <= 40 and precio_final > precio_entrada)
            
            res_msg = f"✅ **RESULTADO: WIN**" if es_win else f"❌ **RESULTADO: LOSS**"
            if es_win: wins_totales += 1
            
            enviar_telegram(res_msg, ID_VIP)
            enviar_telegram(f"📑 *BITÁCORA*: {res_msg}\nMarcador: {wins_totales}W", ID_BITACORA)
            time.sleep(20) 
            
    except: pass

# --- INICIO ---
print(f"🚀 {BOT_NAME} Activo con IDs protegidos")

activos = [
    {"trading": "EURUSD", "display": "EUR/USD(OTC)"},
    {"trading": "GBPUSD", "display": "GBP/USD(OTC)"},
    {"trading": "USDJPY", "display": "USD/JPY(OTC)"},
    {"trading": "AUDUSD", "display": "AUD/USD(OTC)"}
]

while True:
    if conteo_operaciones >= LIMITE_OPERACIONES:
        enviar_telegram(f"⏳ **DESCANSO ACTIVADO** (1 Hora)", ID_VIP)
        time.sleep(TIEMPO_DESCANSO)
        conteo_operaciones = 0
        wins_totales = 0

    for activo in activos:
        if conteo_operaciones < LIMITE_OPERACIONES:
            analizar_y_operar(activo['trading'], activo['display'])
    time.sleep(20)
