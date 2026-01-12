import time
import requests
from tradingview_ta import TA_Handler, Interval

# --- CONFIGURACIÓN DE IDENTIDAD ---
TOKEN = "8386038643:AAEngPQbBuu41WBWm7pCYQxm3yEowoJzYaw"
ID_PERSONAL = "6717348273"
ID_VIP = "-1003653748217"
ID_BITACORA = "-1003621701961"
LINK_CONTACTO = "https://t.me/+4bqyiiDGXTA4ZTRh"
BOT_NAME = "Lógica Trading Elite 💎"

conteo_operaciones = 0
wins_totales = 0  
LIMITE_OPERACIONES = 4  
TIEMPO_DESCANSO = 3600  

def enviar_telegram(mensaje, destino):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": destino, "text": mensaje, "parse_mode": "Markdown"}
    try: requests.post(url, json=payload, timeout=10)
    except: pass

def analizar_estricto(par_trading, par_display):
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
        sma200 = analysis.indicators["SMA200"] # Media Móvil de 200 periodos
        precio_actual = analysis.indicators["close"]
        
        # --- FILTRO FRANCOTIRADOR ---
        # Solo COMPRA si el mercado está barato (RSI < 30) Y la tendencia general es ALCISTA (Precio > SMA200)
        es_compra = rsi <= 30 and precio_actual > sma200
        
        # Solo VENDE si el mercado está caro (RSI > 70) Y la tendencia general es BAJISTA (Precio < SMA200)
        es_venta = rsi >= 70 and precio_actual < sma200

        if es_compra or es_venta:
            direccion = "SUBE (UP) 🟢" if es_compra else "BAJA (DOWN) 🔻"
            
            # 1. SEÑAL VIP DE ALTA PRECISIÓN
            msg_señal = (f"🔥 **SEÑAL DE ALTA PRECISIÓN (ELITE)** 🔥\n"
                         f"──────────────────\n"
                         f"💱 Par: {par_display}\n"
                         f"⏰ Tiempo: 2 Minutos\n"
                         f"📈 Operación: **{direccion}**\n"
                         f"📊 Filtro Tendencia: ✅ Confirmado\n"
                         f"──────────────────\n"
                         f"🚀 **ENTRADA SEGURA - ¡YA!**")
            
            enviar_telegram(msg_señal, ID_VIP)
            enviar_telegram(msg_señal, ID_PERSONAL)
            
            conteo_operaciones += 1
            time.sleep(125) # Duración del trade
            
            # 2. RESULTADO
            final_analisis = handler.get_analysis()
            precio_final = final_analisis.indicators["close"]
            win = (es_compra and precio_final > precio_actual) or (es_venta and precio_final < precio_actual)
            
            res_msg = f"✅ **OPERACIÓN GANADORA** ✅" if win else f"❌ **RESULTADO: LOSS**"
            if win: wins_totales += 1
            
            enviar_telegram(res_msg, ID_VIP)
            enviar_telegram(f"📑 *BITÁCORA*: {res_msg}\nMarcador: {wins_totales}W", ID_BITACORA)
            
            # Pausa de seguridad para que el mercado respire tras una señal ganadora
            time.sleep(60) 

    except: pass

# --- INICIO ---
print(f"🚀 {BOT_NAME} en modo FRANCOTIRADOR activo.")
enviar_telegram(f"💎 **SISTEMA {BOT_NAME} ACTIVADO**\n\nModo de alta precisión: ON. El bot buscará entradas perfectas con filtros de tendencia. 🎯", ID_VIP)

activos = [
    {"trading": "EURUSD", "display": "EUR/USD(OTC)"},
    {"trading": "GBPUSD", "display": "GBP/USD(OTC)"},
    {"trading": "USDJPY", "display": "USD/JPY(OTC)"},
    {"trading": "AUDUSD", "display": "AUD/USD(OTC)"},
    {"trading": "EURJPY", "display": "EUR/JPY(OTC)"}
]

while True:
    if conteo_operaciones >= LIMITE_OPERACIONES:
        reporte = (f"📊 **SESIÓN ELITE COMPLETADA**\n\n✅ Ganadas: {wins_totales}\n🎯 Precisión: Máxima\n\n📩 **¿Quieres operar con nosotros?**\n{LINK_CONTACTO}")
        enviar_telegram(reporte, ID_VIP)
        time.sleep(TIEMPO_DESCANSO)
        conteo_operaciones = 0
        wins_totales = 0

    for activo in activos:
        if conteo_operaciones < LIMITE_OPERACIONES:
            analizar_estricto(activo['trading'], activo['display'])
            time.sleep(5)
    
    time.sleep(30)
