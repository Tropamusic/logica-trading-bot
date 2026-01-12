import time
import requests
from datetime import datetime, timedelta
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
TIEMPO_DESCANSO = 1800 # 30 min

def enviar_telegram(mensaje, destino):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": destino, "text": mensaje, "parse_mode": "Markdown"}
    try: requests.post(url, json=payload, timeout=10)
    except: pass

def analizar_sensible(par_trading, par_display):
    global conteo_operaciones, wins_totales
    handler = TA_Handler(symbol=par_trading, exchange="FX_IDC", screener="forex", interval=Interval.INTERVAL_1_MINUTE)
    
    try:
        analysis = handler.get_analysis()
        rsi = analysis.indicators["RSI"]
        precio_entrada = analysis.indicators["close"]
        
        # SENSILIBIDAD 60/40
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
            
            # ESPERA DE LA OPERACIÓN (2 MINUTOS)
            time.sleep(120) 
            
            # PAUSA DE SEGURIDAD (5 seg) para que el precio se asiente
            time.sleep(5) 
            
            # CONSULTA PRECIO FINAL PARA COMPARAR
            nuevo_analisis = handler.get_analysis()
            precio_final = nuevo_analisis.indicators["close"]
            
            # Lógica de verificación precisa
            win = False
            if es_venta and precio_final < precio_entrada:
                win = True
            elif es_compra and precio_final > precio_entrada:
                win = True
            
            if win:
                wins_totales += 1
                res_msg = f"✅ **OPERACIÓN GANADORA** ✅\nEntrada: {precio_entrada:.5f} | Cierre: {precio_final:.5f}"
            else:
                res_msg = f"❌ **RESULTADO: LOSS** ❌\nEntrada: {precio_entrada:.5f} | Cierre: {precio_final:.5f}"
            
            enviar_telegram(res_msg, ID_VIP)
            enviar_telegram(f"📑 *BITÁCORA*: {res_msg}\nMarcador: {wins_totales}W", ID_BITACORA)
            time.sleep(30) 

    except Exception as e:
        print(f"Error: {e}")

# --- BUCLE PRINCIPAL ---
activos = [
    {"trading": "EURUSD", "display": "EUR/USD(OTC)"},
    {"trading": "GBPUSD", "display": "GBP/USD(OTC)"},
    {"trading": "USDJPY", "display": "USD/JPY(OTC)"},
    {"trading": "AUDUSD", "display": "AUD/USD(OTC)"},
    {"trading": "EURJPY", "display": "EUR/JPY(OTC)"}
]

while True:
    ahora = datetime.now().hour
    # Horarios: Mañana (8-11), Tarde (14-17), Noche (20-23)
    es_hora = (8 <= ahora < 11) or (14 <= ahora < 17) or (20 <= ahora < 23)

    if es_hora:
        if conteo_operaciones >= LIMITE_OPERACIONES:
            h_regreso = (datetime.now() + timedelta(minutes=30)).strftime('%H:%M')
            reporte = (f"📊 **SESIÓN FINALIZADA**\n\n✅ Ganadas: {wins_totales}\n"
                       f"⏳ Pausa de 30 min. Regreso: **{h_regreso}**")
            enviar_telegram(reporte, ID_VIP)
            time.sleep(TIEMPO_DESCANSO)
            conteo_operaciones = 0
            wins_totales = 0
        
        for activo in activos:
            if conteo_operaciones < LIMITE_OPERACIONES:
                analizar_sensible(activo['trading'], activo['display'])
                time.sleep(5)
    else:
        time.sleep(600) # Espera 10 min si está fuera de horario
    
    time.sleep(15)
