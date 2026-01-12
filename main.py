import time
import requests
from datetime import datetime, timedelta
import pytz 
from tradingview_ta import TA_Handler, Interval

# --- CONFIGURACIÓN DE IDENTIDAD ---
TOKEN = "8386038643:AAEngPQbBuu41WBWm7pCYQxm3yEowoJzYaw"
ID_PERSONAL = "6717348273"
ID_VIP = "-1003653748217"
ID_BITACORA = "-1003621701961"
LINK_CONTACTO = "https://t.me/+4bqyiiDGXTA4ZTRh"
BOT_NAME = "Lógica Trading 📊"

# Zona horaria maestra (Venezuela / EST)
MI_ZONA_HORARIA = pytz.timezone('America/Caracas') 

conteo_operaciones = 0
wins_totales = 0  
LIMITE_OPERACIONES = 4  
TIEMPO_DESCANSO = 1800 # 30 minutos

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
        
        # SENSIBILIDAD 60/40 (Ideal para flujo constante de señales)
        es_venta = rsi >= 60
        es_compra = rsi <= 40

        if es_compra or es_venta:
            direccion = "BAJA (DOWN) 🔻" if es_venta else "SUBE (UP) 🟢"
            
            # Mensaje Profesional para todos los brokers
            msg_señal = (f"💎 **{BOT_NAME} - SEÑAL VIP** 💎\n"
                         f"──────────────────\n"
                         f"💱 Par: {par_display}\n"
                         f"⏰ Tiempo: 2 Minutos (M2)\n"
                         f"📈 Operación: **{direccion}**\n"
                         f"📱 Válido para: TODOS LOS BROKERS\n"
                         f"──────────────────\n"
                         f"🔥 **¡ENTRA YA!** 🔥")
            
            enviar_telegram(msg_señal, ID_VIP)
            enviar_telegram(msg_señal, ID_PERSONAL)
            conteo_operaciones += 1
            
            # Espera de 2 min + 5 seg de margen para cierre exacto
            time.sleep(125) 
            
            # Verificación de resultado
            p_final = handler.get_analysis().indicators["close"]
            win = (es_venta and p_final < precio_entrada) or (es_compra and p_final > precio_entrada)
            
            if win:
                wins_totales += 1
                res_msg = f"✅ **OPERACIÓN GANADORA** ✅\n¡Profit en {par_display}!"
            else:
                res_msg = f"❌ **RESULTADO: LOSS** ❌\nPreparando siguiente par..."
            
            enviar_telegram(res_msg, ID_VIP)
            # Bitácora con detalles técnicos
            enviar_telegram(f"📑 *BITÁCORA*: {res_msg}\n📊 {par_display}\nEntrada: {precio_entrada:.5f} | Salida: {p_final:.5f}", ID_BITACORA)
            time.sleep(30) 

    except: pass

# --- BUCLE DE CONTROL ---
print(f"🚀 {BOT_NAME} Operando en horario Vzla/EST.")

activos = [
    {"trading": "EURUSD", "display": "EUR/USD(OTC)"},
    {"trading": "GBPUSD", "display": "GBP/USD(OTC)"},
    {"trading": "USDJPY", "display": "USD/JPY(OTC)"},
    {"trading": "AUDUSD", "display": "AUD/USD(OTC)"},
    {"trading": "EURJPY", "display": "EUR/JPY(OTC)"}
]

while True:
    ahora_vzla = datetime.now(MI_ZONA_HORARIA).hour
    # Horarios: Mañana (8-11), Tarde (14-17), Noche (20-23)
    es_hora = (8 <= ahora_vzla < 11) or (14 <= ahora_vzla < 17) or (20 <= ahora_vzla < 23)

    if es_hora:
        if conteo_operaciones >= LIMITE_OPERACIONES:
            h_regreso = (datetime.now(MI_ZONA_HORARIA) + timedelta(minutes=30)).strftime('%I:%M %p')
            reporte = (f"📊 **SESIÓN FINALIZADA**\n\n"
                       f"✅ Ganadas: {wins_totales}\n"
                       f"❌ Perdidas: {LIMITE_OPERACIONES - wins_totales}\n\n"
                       f"⏳ Próxima sesión: **{h_regreso} (Hora Vzla/EST)**\n"
                       f"🌐 *Calcula el horario de tu país.*")
            enviar_telegram(reporte, ID_VIP)
            time.sleep(TIEMPO_DESCANSO)
            conteo_operaciones = 0
            wins_totales = 0
        
        for activo in activos:
            if conteo_operaciones < LIMITE_OPERACIONES:
                analizar_sensible(activo['trading'], activo['display'])
                time.sleep(5)
    else:
        # Pausa larga fuera de horario para ahorrar recursos
        time.sleep(600) 
    
    time.sleep(15)
