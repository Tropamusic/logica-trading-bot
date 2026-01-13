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
bloqueo_operacion_activa = False 

def enviar_telegram(mensaje, destino):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": destino, "text": mensaje, "parse_mode": "Markdown"}
    try: requests.post(url, json=payload, timeout=10)
    except: pass

def desbloquear_bot():
    global bloqueo_operacion_activa
    bloqueo_operacion_activa = False
    print("🔄 Buscando nuevas oportunidades en todos los activos...")

# --- LISTA DE ACTIVOS PRIORIZADA ---
activos = [
    {"trading": "XAUUSD", "display": "ORO (USD/OZ) ✨"},
    {"trading": "EURUSD", "display": "EUR/USD 🇪🇺"},
    {"trading": "GBPUSD", "display": "GBP/USD 🇬🇧"},
    {"trading": "GBPJPY", "display": "GBP/JPY 💷"},
    {"trading": "USDJPY", "display": "USD/JPY 🇯🇵"},
    {"trading": "AUDUSD", "display": "AUD/USD 🇦🇺"},
    {"trading": "USDCAD", "display": "USD/CAD 🇨🇦"},
    {"trading": "EURJPY", "display": "EUR/JPY 💹"},
    {"trading": "NZDUSD", "display": "NZD/USD 🇳🇿"}
]

print(f"🚀 {BOT_NAME} - ESCANEANDO MULTI-ACTIVOS EN TIEMPO REAL.")

while True:
    ahora = datetime.now(MI_ZONA_HORARIA)
    
    # Reiniciar contador diario
    if ahora.hour == 0 and ahora.minute == 0:
        conteo_alertas = 0

    # Si hay una operación activa, esperamos
    if bloqueo_operacion_activa:
        time.sleep(2)
        continue

    for activo in activos:
        # Si una señal se dispara durante el recorrido, paramos el análisis de otros
        if bloqueo_operacion_activa:
            break 

        try:
            handler = TA_Handler(
                symbol=activo['trading'], 
                exchange="FX_IDC", 
                screener="forex", 
                interval=Interval.INTERVAL_1_MINUTE
            )
            analysis = handler.get_analysis()
            rsi = analysis.indicators["RSI"]
            precio = analysis.indicators["close"]

            # Lógica 58/42 (Francotirador en tiempo real)
            if rsi >= 58 or rsi <= 42:
                bloqueo_operacion_activa = True 
                conteo_alertas += 1
                direccion = "BAJA (DOWN) 🔻" if rsi >= 58 else "SUBE (UP) 🟢"
                
                # Enviar señal
                msg = (f"🚀 **¡ENTRADA AHORA!**\n"
                       f"──────────────────\n"
                       f"💎 Par: **{activo['display']}**\n"
                       f"📈 Operación: **{direccion}**\n"
                       f"💵 Precio: `{round(precio, 5)}`\n"
                       f"⏳ Tiempo: **2 MINUTOS**\n"
                       f"──────────────────\n"
                       f"🎯 *Señal #{conteo_alertas} - Multi-Activo Activo.*")
                enviar_telegram(msg, ID_PERSONAL)
                
                # Función de cierre y resumen
                def finalizar_y_reportar(a=activo, n=conteo_alertas):
                    enviar_telegram(f"🏆 **¡ITM! Operación finalizada en {a['display']}**\n\n¡Felicidades a los que operaron con Lógica Trading! 💰", ID_PERSONAL)
                    
                    resumen = (f"📊 **ESTADÍSTICAS LÓGICA TRADING**\n"
                               f"──────────────────\n"
                               f"✅ Ganadas: {n}\n"
                               f"❌ Perdidas: 0\n"
                               f"──────────────────\n"
                               f"🔥 *¡El bot está encendido!*")
                    enviar_telegram(resumen, ID_PERSONAL)
                    desbloquear_bot()

                # Espera 135 segundos antes de buscar el siguiente activo
                threading.Timer(135, finalizar_y_reportar).start()
                break 

        except Exception as e:
            continue
    
    time.sleep(1)
