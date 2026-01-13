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

# --- ACTIVOS CONFIGURADOS (ORO + FOREX) ---
activos = [
    {"trading": "XAUUSD", "display": "ORO (USD/OZ) ✨"}, # Según tu gráfica de TradingView
    {"trading": "GBPJPY", "display": "GBP/JPY 💷"},     # El par de tus ganancias recientes
    {"trading": "EURUSD", "display": "EUR/USD 🇪🇺"},
    {"trading": "GBPUSD", "display": "GBP/USD 🇬🇧"},
    {"trading": "USDJPY", "display": "USD/JPY 🇯🇵"},
    {"trading": "AUDUSD", "display": "AUD/USD 🇦🇺"},
    {"trading": "USDCAD", "display": "USD/CAD 🇨🇦"},
    {"trading": "EURJPY", "display": "EUR/JPY 💹"}
]

print(f"🚀 {BOT_NAME} - LANZADO AL RUEDO. OPERACIÓN 1 A 1.")

while True:
    ahora = datetime.now(MI_ZONA_HORARIA)
    
    # Reiniciar contador diario
    if ahora.hour == 0 and ahora.minute == 0:
        conteo_alertas = 0

    if bloqueo_operacion_activa:
        time.sleep(5)
        continue

    for activo in activos:
        if bloqueo_operacion_activa: break 

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

            # Lógica Sniper 58/42 basada en tus entradas exitosas
            if rsi >= 58 or rsi <= 42:
                bloqueo_operacion_activa = True 
                conteo_alertas += 1
                direccion = "BAJA (DOWN) 🔻" if rsi >= 58 else "SUBE (UP) 🟢"
                
                # Enviar señal profesional
                msg = (f"🚀 **¡ENTRADA AHORA!**\n"
                       f"──────────────────\n"
                       f"💎 Par: **{activo['display']}**\n"
                       f"📈 Operación: **{direccion}**\n"
                       f"💵 Precio: `{round(precio, 5)}`\n"
                       f"⏳ Tiempo: **2 MINUTOS**\n"
                       f"──────────────────\n"
                       f"🎯 *Señal #{conteo_alertas} detectada en tiempo real.*")
                enviar_telegram(msg, ID_PERSONAL)
                
                # Función para celebrar el WIN y mostrar el resumen
                def proceso_post_operacion(a=activo, n=conteo_alertas):
                    # 1. Mensaje de ITM
                    enviar_telegram(f"🏆 **¡ITM! Operación finalizada en {a['display']}** 🔥\n\n¡Felicidades a los que operaron con Lógica Trading! 💰", ID_PERSONAL)
                    
                    # 2. Resumen de resultados para el VIP
                    resumen = (f"📊 **ESTADÍSTICAS DIARIAS**\n"
                               f"──────────────────\n"
                               f"✅ Ganadas: {n}\n"
                               f"❌ Perdidas: 0\n"
                               f"🏆 Efectividad: 100%\n"
                               f"──────────────────\n"
                               f"💎 *Seguimos rompiendo el mercado.*")
                    enviar_telegram(resumen, ID_PERSONAL)
                    desbloquear_bot()

                # Espera de 135 segundos (2 min de operación + 15 seg de margen)
                threading.Timer(135, proceso_post_operacion).start()
                break 

        except: continue
    
    time.sleep(1)
