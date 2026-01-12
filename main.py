import time
import requests
from tradingview_ta import TA_Handler, Interval

# --- CONFIGURACIÓN DE IDENTIDAD ---
TOKEN = "8386038643:AAEngPQbBuu41WBWm7pCYQxm3yEowoJzYaw"
ID_PERSONAL = "6717348273"
ID_VIP = "-1003653748217"      # <--- NUEVO ID VIP ACTUALIZADO
ID_BITACORA = "-1003621701961"
LINK_CONTACTO = "https://t.me/+4bqyiiDGXTA4ZTRh"
BOT_NAME = "Lógica Trading 📊"

conteo_operaciones = 0
wins_totales = 0  
LIMITE_OPERACIONES = 4  
TIEMPO_DESCANSO = 3600  

def enviar_telegram(mensaje, destino):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": destino, 
        "text": mensaje, 
        "parse_mode": "Markdown",
        "disable_web_page_preview": False
    }
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
        
        # --- DETECCIÓN DE SEÑAL (RSI 60/40) ---
        if (rsi >= 60) or (rsi <= 40):
            direccion = "BAJA (DOWN) 🔻" if rsi >= 60 else "SUBE (UP) 🟢"
            
            # 1. ENVIAR SEÑAL OPERATIVA INMEDIATA
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
            
            # 2. ESPERA DE 2 MINUTOS (DURACIÓN DE LA OPERACIÓN)
            time.sleep(125) 
            
            # 3. VERIFICAR RESULTADO
            analisis_final = handler.get_analysis()
            precio_final = analisis_final.indicators["close"]
            
            # Lógica de acierto
            es_win = (rsi >= 60 and precio_final < precio_entrada) or (rsi <= 40 and precio_final > precio_entrada)
            
            if es_win:
                wins_totales += 1
                res_msg = f"✅ **RESULTADO: WIN** ✅\n¡Profit excelente en {par_display}!"
            else:
                res_msg = f"❌ **RESULTADO: LOSS** ❌\nMercado volátil en {par_display}."
            
            # 4. ENVIAR RESULTADO
            enviar_telegram(res_msg, ID_VIP)
            enviar_telegram(f"📑 *BITÁCORA*: {res_msg}\nMarcador: {wins_totales}W", ID_BITACORA)
            time.sleep(20) # Pausa entre señales
            
    except Exception as e:
        print(f"Error analizando {par_trading}: {e}")

# --- BUCLE PRINCIPAL ---
print(f"🚀 {BOT_NAME} Operando en Canal VIP: {ID_VIP}")
enviar_telegram(f"🌟 **SISTEMA {BOT_NAME.upper()} EN LÍNEA**\n\nBuscando las mejores oportunidades del mercado. 📡", ID_VIP)

activos = [
    {"trading": "EURUSD", "display": "EUR/USD(OTC)"},
    {"trading": "GBPUSD", "display": "GBP/USD(OTC)"},
    {"trading": "USDJPY", "display": "USD/JPY(OTC)"},
    {"trading": "AUDUSD", "display": "AUD/USD(OTC)"}
]

while True:
    # Si llegamos a 4 operaciones, hacemos el reporte y descansamos
    if conteo_operaciones >= LIMITE_OPERACIONES:
        reporte_final = (f"📊 **SESIÓN FINALIZADA**\n\n"
                         f"✅ Operaciones Ganadas: {wins_totales}\n"
                         f"🎯 Efectividad Lograda: VIP\n\n"
                         f"📩 **¿Quieres entrar al VIP? Contáctame aquí:**\n{LINK_CONTACTO}\n\n"
                         f"⏳ El bot descansará 1 hora para proteger el capital. 🛡")
        
        enviar_telegram(reporte_final, ID_VIP)
        time.sleep(TIEMPO_DESCANSO)
        conteo_operaciones = 0
        wins_totales = 0
        enviar_telegram(f"🚀 **{BOT_NAME}** Activo de nuevo. ¡Vamos por más profit!", ID_VIP)

    for activo in activos:
        if conteo_operaciones < LIMITE_OPERACIONES:
            analizar_y_operar(activo['trading'], activo['display'])
            time.sleep(5) # Pequeña pausa entre escaneo de activos
    
    time.sleep(20) # Pausa de escaneo general
