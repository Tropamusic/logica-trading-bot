import time
import requests
from tradingview_ta import TA_Handler, Interval

# --- DATOS DE LÓGICA TRADING ---
TOKEN = "8386038643:AAEngPQbBuu41WBWm7pCYQxm3yEowoJzYaw"
ID_PERSONAL = "6717348273"

def enviar(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    try: requests.post(url, json={"chat_id": ID_PERSONAL, "text": msg, "parse_mode": "Markdown"})
    except: pass

# CONFIGURACIÓN SNIPER PARA ORO
oro_handler = TA_Handler(
    symbol="XAUUSD",
    exchange="OANDA",
    screener="forex",
    interval=Interval.INTERVAL_1_MINUTE
)

print("🏆 LÓGICA TRADING: ESTRATEGIA ORO LUXALGO ACTIVADA")
print("📡 Monitoreando Rupturas y Volumen en tiempo real...")

while True:
    try:
        # Extraemos el análisis de TradingView
        analisis = oro_handler.get_analysis()
        rsi = analisis.indicators["RSI"]
        precio = analisis.indicators["close"]
        
        # Simulamos el 'Oscilador de Volumen' de tu script
        # Si la recomendación es fuerte, significa que hay volumen respaldando el movimiento
        recomendacion = analisis.summary["RECOMMENDATION"]

        print(f"📊 ORO: ${precio} | RSI: {round(rsi, 2)} | {recomendacion}")

        # LÓGICA DE ENTRADA (Basada en tu script de Soportes/Resistencias)
        # 1. RUPTURA DE RESISTENCIA (Venta en el rechazo/Bear Wick)
        if rsi >= 58.0 and "SELL" in recomendacion:
            msg = (f"🔱 **ORO: RECHAZO EN RESISTENCIA**\n"
                   f"──────────────────\n"
                   f"📈 Operación: **BAJA (DOWN) 🔻**\n"
                   f"💵 Precio: `${precio}`\n"
                   f"📊 RSI: `{round(rsi, 2)}` (Sobrecompra)\n"
                   f"⏳ Tiempo: **2 MINUTOS**\n"
                   f"──────────────────\n"
                   f"⚠️ *Busca la mecha superior (Bear Wick) en Pocket Option.*")
            enviar(msg)
            time.sleep(120) # Pausa de experiencia para no saturar

        # 2. RUPTURA DE SOPORTE (Compra en el rebote/Bull Wick)
        elif rsi <= 42.0 and "BUY" in recomendacion:
            msg = (f"🔱 **ORO: REBOTE EN SOPORTE**\n"
                   f"──────────────────\n"
                   f"📈 Operación: **SUBE (UP) 🟢**\n"
                   f"💵 Precio: `${precio}`\n"
                   f"📊 RSI: `{round(rsi, 2)}` (Sobreventa)\n"
                   f"⏳ Tiempo: **2 MINUTOS**\n"
                   f"──────────────────\n"
                   f"🎯 *Lógica Trading: Entra en el soporte real.*")
            enviar(msg)
            time.sleep(120)

    except Exception as e:
        print(f"Error: {e}")
    
    time.sleep(1) # Escaneo ultra rápido
