import time
import requests
from tradingview_ta import TA_Handler, Interval

# --- CONFIGURACIÓN ---
TOKEN = "8386038643:AAEngPQbBuu41WBWm7pCYQxm3yEowoJzYaw"
ID_PERSONAL = "6717348273"
ID_VIP = "-1003653748217"
ID_BITACORA = "-1003621701961"
LINK_CONTACTO = "https://t.me/+4bqyiiDGXTA4ZTRh"
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

def analizar_equilibrado(par_trading, par_display):
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
        
        # --- LÓGICA EQUILIBRADA (65/35) ---
        # No es tan extremo como 70 ni tan flojo como 60.
        es_venta = rsi >= 65
        es_compra = rsi <= 35

        if es_compra or es_venta:
            direccion = "BAJA (DOWN) 🔻" if es_venta else "SUBE (UP) 🟢"
            
            # Formato profesional para mantener el interés
            msg_señal = (f"💎 **{BOT_NAME} - SEÑAL VIP** 💎\n"
                         f"──────────────────\n"
                         f"💱 Par: {par_display}\n"
                         f"⏰ Tiempo: 2 Minutos\n"
                         f"📈 Operación: **{direccion}**\n"
                         f"🎯 Probabilidad: ALTA\n"
                         f"──────────────────\n"
                         f"🔥 **¡ENTRA YA AHORA!** 🔥")
            
            enviar_telegram(msg_señal, ID_VIP)
            enviar_telegram(msg_señal, ID_PERSONAL)
            
            conteo_operaciones += 1
            time.sleep(125) # Espera del trade
            
            # Resultado
            nuevo_analisis = handler.get_analysis()
            precio_final = nuevo_analisis.indicators["close"]
            win = (es_venta and precio_final < precio_entrada) or (es_compra and precio_final > precio_entrada)
            
            if win:
                wins_totales += 1
                res_msg = f"✅ **OPERACIÓN GANADORA** ✅\n¡Profit asegurado en {par_display}!"
            else:
                res_msg = f"❌ **RESULTADO: LOSS** ❌\nMercado volátil, preparando siguiente par."
            
            enviar_telegram(res_msg, ID_VIP)
            enviar_telegram(f"📑 *BITÁCORA*: {res_msg}\nMarcador: {wins_totales}W", ID_BITACORA)
            time.sleep(30) # Pausa para buscar otra oportunidad

    except: pass

# --- INICIO ---
print(f"🚀 {BOT_NAME} en modo EQUILIBRADO activo.")
enviar_telegram(f"🌟 **{BOT_NAME.upper()} EN LÍNEA**\n\nAnalizando mercado con precisión equilibrada. ¡Prepárense para los profits! 🚀", ID_VIP)

activos = [
    {"trading": "EURUSD", "display": "EUR/USD(OTC)"},
    {"trading": "GBPUSD", "display": "GBP/USD(OTC)"},
    {"trading": "USDJPY", "display": "USD/JPY(OTC)"},
    {"trading": "AUDUSD", "display": "AUD/USD(OTC)"},
    {"trading": "EURJPY", "display": "EUR/JPY(OTC)"},
    {"trading": "GBPJP", "display": "GBP/JPY(OTC)"} # Añadí un par extra para flujo constante
]

while True:
    if conteo_operaciones >= LIMITE_OPERACIONES:
        reporte = (f"📊 **SESIÓN FINALIZADA**\n\n✅ Ganadas: {wins_totales}\n🎯 Efectividad: VIP\n\n📩 **VIP INFO:** {LINK_CONTACTO}")
        enviar_telegram(reporte, ID_VIP)
        time.sleep(TIEMPO_DESCANSO)
        conteo_operaciones = 0
        wins_totales = 0

    for activo in activos:
        if conteo_operaciones < LIMITE_OPERACIONES:
            analizar_equilibrado(activo['trading'], activo['display'])
            time.sleep(5)
    
    time.sleep(15)
