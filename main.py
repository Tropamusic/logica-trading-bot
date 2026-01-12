import time
import requests
from datetime import datetime, timedelta
import pytz 
from tradingview_ta import TA_Handler, Interval

# --- CONFIGURACIÓN ---
TOKEN = "8386038643:AAEngPQbBuu41WBWm7pCYQxm3yEowoJzYaw"
ID_PERSONAL = "6717348273"
BOT_NAME = "Lógica Trading 📊"

MI_ZONA_HORARIA = pytz.timezone('America/Caracas') 

conteo_alertas = 0
LIMITE_ALERTAS = 4
TIEMPO_DESCANSO_HORA = 3600 

def enviar_telegram(mensaje, destino):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": destino, "text": mensaje, "parse_mode": "Markdown"}
    try: requests.post(url, json=payload, timeout=10)
    except: pass

# --- CONFIRMACIÓN DE ARRANQUE ---
enviar_telegram(f"🚀 **{BOT_NAME} CONECTADO**\nAnalizando con RSI 55/45 para más señales.\n¡Listo para la sesión, Lógica!", ID_PERSONAL)

while True:
    if conteo_alertas < LIMITE_ALERTAS:
        activos = [
            {"trading": "EURUSD", "display": "EUR/USD"},
            {"trading": "GBPUSD", "display": "GBP/USD"},
            {"trading": "USDJPY", "display": "USD/JPY"},
            {"trading": "AUDUSD", "display": "AUD/USD"},
            {"trading": "EURJPY", "display": "EUR/JPY"}
        ]
        
        for activo in activos:
            try:
                handler = TA_Handler(symbol=activo['trading'], exchange="FX_IDC", screener="forex", interval=Interval.INTERVAL_1_MINUTE)
                analysis = handler.get_analysis()
                rsi = analysis.indicators["RSI"]
                
                # SENSIBILIDAD AUMENTADA (55/45)
                es_venta = rsi >= 55
                es_compra = rsi <= 45
                
                if es_venta or es_compra:
                    conteo_alertas += 1
                    accion = "VENTA (BAJA) 🔴" if es_venta else "COMPRA (SUBE) 🟢"
                    
                    msg = (f"🎯 **ALERTA #{conteo_alertas} / {LIMITE_ALERTAS}**\n"
                           f"──────────────────\n"
                           f"💹 Par: **{activo['display']}**\n"
                           f"⚡ Acción: **{accion}**\n"
                           f"📈 RSI: {rsi:.2f}\n"
                           f"──────────────────\n"
                           f"📢 *¿La enviamos al VIP?*")
                    
                    enviar_telegram(msg, ID_PERSONAL)
                    
                    # Espera de 2 minutos para no repetir la misma señal
                    time.sleep(120) 
                    
                    if conteo_alertas >= LIMITE_ALERTAS:
                        break
            except:
                continue
            time.sleep(4) 
            
    else:
        proxima = (datetime.now(MI_ZONA_HORARIA) + timedelta(hours=1)).strftime('%I:%M %p')
        enviar_telegram(f"😴 **BLOQUE COMPLETADO**\nTomando 1 hora de descanso.\nRegreso a las: **{proxima}**", ID_PERSONAL)
        time.sleep(TIEMPO_DESCANSO_HORA)
        conteo_alertas = 0
        enviar_telegram(f"⚡ **¡DE VUELTA!**\nBuscando nuevas oportunidades...", ID_PERSONAL)
