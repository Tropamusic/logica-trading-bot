import time
import requests
from tradingview_ta import TA_Handler, Interval

# --- CONFIGURACIÓN DE IDENTIDAD ---
TOKEN = "8386038643:AAEngPQbBuu41WBWm7pCYQxm3yEowoJzYaw"
ID_PERSONAL = "6717348273"
ID_VIP = "-1003653748217"
ID_BITACORA = "-1003621701961"

# TUS LINKS ACTUALIZADOS
LINK_VIP = "https://t.me/+4bqyiiDGXTA4ZTRh"
LINK_RESULTADOS = "https://t.me/LogicaTradingResultados"

BOT_NAME = "Lógica Trading 📊"

conteo_operaciones = 0
wins_totales = 0  
LIMITE_OPERACIONES = 4  
TIEMPO_DESCANSO = 3600  

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
    
    try: 
        requests.post(url, json=payload, timeout=10)
    except: 
        pass

# --- FUNCIÓN DE BIENVENIDA CON TUS LINKS ---
def enviar_menu_inicio(chat_id):
    texto = (f"👋 **¡Bienvenido a {BOT_NAME}!**\n\n"
             f"Soy tu asistente de alta precisión para Opciones Binarias.\n\n"
             f"🚀 **¡Empieza a ganar hoy mismo!**\n"
             f"Selecciona una opción abajo para unirte a nuestra comunidad:")
    
    botones = [
        [{"text": "💎 UNIRSE AL CANAL VIP (GRATIS)", "url": LINK_VIP}],
        [{"text": "📊 VER RESULTADOS (BITÁCORA)", "url": LINK_RESULTADOS}]
    ]
    enviar_telegram(texto, chat_id, botones)

def analizar_equilibrado(par_trading, par_display):
    global conteo_operaciones, wins_totales
    handler = TA_Handler(symbol=par_trading, exchange="FX_IDC", screener="forex", interval=Interval.INTERVAL_1_MINUTE)
    
    try:
        analysis = handler.get_analysis()
        rsi = analysis.indicators["RSI"]
        precio_entrada = analysis.indicators["close"]
        
        # Lógica equilibrada 65/35
        es_venta = rsi >= 65
        es_compra = rsi <= 35

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
            time.sleep(125) # Duración de la operación
            
            # Resultado
            nuevo_p = handler.get_analysis().indicators["close"]
            win = (es_venta and nuevo_p < precio_entrada) or (es_compra and nuevo_p > precio_entrada)
            
            if win:
                wins_totales += 1
                res_msg = f"✅ **OPERACIÓN GANADORA** ✅"
            else:
                res_msg = f"❌ **RESULTADO: LOSS** ❌"
            
            enviar_telegram(res_msg, ID_VIP)
            enviar_telegram(f"📑 *BITÁCORA*: {res_msg}\nMarcador: {wins_totales}W", ID_BITACORA)
            time.sleep(30)
    except: 
        pass

# --- INICIO DEL PROGRAMA ---
print(f"🚀 {BOT_NAME} Activo con Menú y Links actualizados.")

# Envío del menú de bienvenida para que lo veas en tu Telegram
enviar_menu_inicio(ID_PERSONAL)

activos = [
    {"trading": "EURUSD", "display": "EUR/USD(OTC)"},
    {"trading": "GBPUSD", "display": "GBP/USD(OTC)"},
    {"trading": "USDJPY", "display": "USD/JPY(OTC)"},
    {"trading": "AUDUSD", "display": "AUD/USD(OTC)"},
    {"trading": "EURJPY", "display": "EUR/JPY(OTC)"}
]

while True:
    if conteo_operaciones >= LIMITE_OPERACIONES:
        reporte = (f"📊 **SESIÓN FINALIZADA**\n\n✅ Ganadas: {wins_totales}\n🎯 Efectividad: VIP\n\n📩 Más info: {LINK_VIP}")
        enviar_telegram(reporte, ID_VIP)
        time.sleep(TIEMPO_DESCANSO)
        conteo_operaciones = 0
        wins_totales = 0

    for activo in activos:
        if conteo_operaciones < LIMITE_OPERACIONES:
            analizar_equilibrado(activo['trading'], activo['display'])
            time.sleep(5)
    time.sleep(15)
