import time
import requests
import threading
from datetime import datetime
import pytz 
from tradingview_ta import TA_Handler, Interval

# --- DATOS DE LÓGICA TRADING ---
TOKEN = "8386038643:AAEngPQbBuu41WBWm7pCYQxm3yEowoJzYaw"
ID_PERSONAL = "6717348273"
BOT_NAME = "Lógica Trading 📊"
MI_ZONA_HORARIA = pytz.timezone('America/Caracas') 

# --- VARIABLES DE CONTROL ---
conteo_alertas = 0
bloqueo_operacion_activa = False # Nueva llave de seguridad

def enviar_telegram(mensaje, destino):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": destino, "text": mensaje, "parse_mode": "Markdown"}
    try: requests.post(url, json=payload, timeout=10)
    except: pass

def desbloquear_bot():
    global bloqueo_operacion_activa
    bloqueo_operacion_activa = False
    print("🔄 Bot desbloqueado. Buscando nueva señal...")

# --- ACTIVOS MONITOREADOS ---
activos = [
    {"trading": "XAUUSD", "display": "ORO (USD/OZ) ✨"},
    {"trading": "GBPJPY", "display": "GBP/JPY 💷"},
    {"trading": "EURUSD", "display": "EUR/USD 🇪🇺"},
    {"trading": "GBPUSD", "display": "GBP/USD 🇬🇧"},
    {"trading": "USDJPY", "display": "USD/JPY 🇯🇵"},
    {"trading": "AUDUSD", "display": "AUD/USD 🇦🇺"},
    {"trading": "USDCAD", "display": "USD/CAD 🇨🇦"},
    {"trading": "EURJPY", "display": "EUR/JPY 💹"}
]

print(f"🚀 {BOT_NAME} - MODO ORDENADO ACTIVADO (1 señal a la vez).")

while True:
    # Si hay una operación en curso, el bot no analiza nada
    if bloqueo_operacion_activa:
        time.sleep(5)
        continue

    for activo in activos:
        # Si durante el bucle se activa una señal, dejamos de buscar otros activos
        if bloqueo_operacion_activa: break 

        try:
            handler = TA_Handler(symbol=activo['trading'], exchange="FX_IDC", screener="forex", interval=Interval.INTERVAL_1_MINUTE)
            analysis = handler.get_analysis()
            rsi = analysis.indicators["RSI"]
            precio = analysis.indicators["close"]

            # --- LÓGICA DE SEÑAL SNIPER ---
            if rsi >= 58 or rsi <= 42:
                bloqueo_operacion_activa = True # BLOQUEO TOTAL
                conteo_alertas += 1
                direccion = "BAJA (DOWN) 🔻" if rsi >= 58 else "SUBE (UP) 🟢"
                
                # 1. Enviar la señal única
                msg = (f"🚀 **¡ENTRADA AHORA!**\n"
                       f"──────────────────\n"
                       f"💎 Par: **{activo['display']}**\n"
                       f"📈 Operación: **{direccion}**\n"
                       f"💵 Precio: `{round(precio, 5)}`\n"
                       f"⏳ Tiempo: **2 MINUTOS**\n"
                       f"──────────────────\n"
                       f"🎯 *Señal #{conteo_alertas}. Concentración total.*")
                enviar_telegram(msg, ID_PERSONAL)
                
                # 2. Programar el mensaje de WIN y el desbloqueo (135 segundos = 2min 15s)
                def finalizar_operacion(a=activo, n=conteo_alertas):
                    enviar_telegram(f"🏆 **¡ITM! Operación finalizada en {a['display']}**\n\n¿Cómo les fue? ¡Manden sus capturas! 💰", ID_PERSONAL)
                    desbloquear_bot()

                threading.Timer(135, finalizar_operacion).start()
                break # Salimos del for para esperar el desbloqueo

        except: continue
    
    time.sleep(1)
