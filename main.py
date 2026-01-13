import time
import requests
import threading
from datetime import datetime
import pytz 
from tradingview_ta import TA_Handler, Interval

# --- DATOS DE LÓGICA TRADING ---
TOKEN = "8386038643:AAEngPQbBuu41WBWm7pCYQxm3yEowoJzYaw"
ID_PERSONAL = "6717348273"
LINK_VIP = "https://t.me/+4bqyiiDGXTA4ZTRh"
BOT_NAME = "Lógica Trading 📊"

MI_ZONA_HORARIA = pytz.timezone('America/Caracas') 

conteo_alertas = 0
ultima_senal_time = time.time()

def enviar_telegram(mensaje, destino):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": destino, "text": mensaje, "parse_mode": "Markdown"}
    try: requests.post(url, json=payload, timeout=10)
    except: pass

# --- LISTA DE ACTIVOS REALES (MERCADO ABIERTO) ---
activos = [
    {"trading": "XAUUSD", "display": "ORO (XAU/USD) ✨"},
    {"trading": "EURUSD", "display": "EUR/USD"},
    {"trading": "GBPUSD", "display": "GBP/USD"},
    {"trading": "USDJPY", "display": "USD/JPY"},
    {"trading": "AUDUSD", "display": "AUD/USD"},
    {"trading": "USDCAD", "display": "USD/CAD"},
    {"trading": "USDCHF", "display": "USD/CHF"},
    {"trading": "NZDUSD", "display": "NZD/USD"},
    {"trading": "EURJPY", "display": "EUR/JPY"},
    {"trading": "GBPJPY", "display": "GBP/JPY"},
    {"trading": "EURGBP", "display": "EUR/GBP"},
    {"trading": "AUDJPY", "display": "AUD/JPY"},
    {"trading": "EURAUD", "display": "EUR/AUD"}
]

print(f"🚀 {BOT_NAME} en modo DINERO REAL iniciado.")

# --- BUCLE PRINCIPAL ---
while True:
    ahora = datetime.now(MI_ZONA_HORARIA)
    
    # 1. CONTROL DE FIN DE SEMANA (CIERRE VIERNES 5PM - APERTURA DOMINGO 5PM)
    # 4 = Viernes, 5 = Sábado, 6 = Domingo
    dia_semana = ahora.weekday()
    hora = ahora.hour

    if (dia_semana == 4 and hora >= 17) or (dia_semana == 5) or (dia_semana == 6 and hora < 17):
        if ahora.minute == 0 and ahora.second < 10: # Solo avisa una vez al inicio del cierre
            enviar_telegram("🔒 **Lógica Trading - Mercado Cerrado**\nEl mercado real ha cerrado por fin de semana. El bot entrará en pausa para evitar el riesgo del OTC. ¡Nos vemos el domingo por la noche!", ID_PERSONAL)
        time.sleep(3600) # Espera una hora para volver a chequear
        continue

    # 2. AVISO DE ACTIVIDAD (CADA 10 MIN SIN SEÑALES)
    tiempo_actual = time.time()
    if (tiempo_actual - ultima_senal_time) >= 600:
        enviar_telegram("🔍 **Lógica Trading Informa:** Analizando mercado REAL. Esperando el punto 60/40 exacto para asegurar la entrada...", ID_PERSONAL)
        ultima_senal_time = tiempo_actual

    # 3. ANÁLISIS DE ACTIVOS
    for activo in activos:
        try:
            handler = TA_Handler(symbol=activo['trading'], exchange="FX_IDC", screener="forex", interval=Interval.INTERVAL_1_MINUTE)
            analysis = handler.get_analysis()
            rsi = analysis.indicators["RSI"]
            precio_entrada = analysis.indicators["close"]
            
            # FILTRO DE MÁXIMA PRECISIÓN 60/40
            es_venta = 60 <= rsi <= 65
            es_compra = 35 <= rsi <= 40
            
            if es_venta or es_compra:
                conteo_alertas += 1
                ultima_senal_time = time.time()
                direccion = "BAJA (DOWN) 🔻" if es_venta else "SUBE (UP) 🟢"
                
                msg = (f"🎯 **SEÑAL REAL DE PRECISIÓN #{conteo_alertas}**\n"
                       f"──────────────────\n"
                       f"💱 Par: **{activo['display']}**\n"
                       f"📈 Operación: **{direccion}**\n"
                       f"📊 RSI: **{round(rsi, 2)}**\n"
                       f"⏰ Tiempo: 2 Minutos\n"
                       f"──────────────────\n"
                       f"📢 **Lógica Trading: ¡Nivel confirmado!**")
                enviar_telegram(msg, ID_PERSONAL)
                
                time.sleep(125) # Espera resultado
                
                check = handler.get_analysis()
                precio_final = check.indicators["close"]
                ganada = (es_venta and precio_final < precio_entrada) or (es_compra and precio_final > precio_entrada)
                
                if ganada:
                    res_txt = f"✅ **¡WIN! MERCADO REAL** ✅\n💰 Par: {activo['display']}\n🔥 *Lógica Trading: Análisis cumplido.*"
                else:
                    res_txt = f"❌ **RESULTADO: LOSS** ❌\n📊 Par: {activo['display']}\nEl mercado es soberano. Seguimos con disciplina."
                
                enviar_telegram(res_txt, ID_PERSONAL)
                time.sleep(300) # Pausa de seguridad
                
        except: continue
    time.sleep(1)
