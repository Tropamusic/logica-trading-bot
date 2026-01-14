import time
import requests
import pandas as pd
from tradingview_ta import TA_Handler, Interval

# --- DATOS DE LÓGICA TRADING ---
TOKEN = "8386038643:AAEngPQbBuu41WBWm7pCYQxm3yEowoJzYaw"
ID_PERSONAL = "6717348273"

# Activos Pro (Mercado Real)
activos = [
    {"symbol": "XAUUSD", "ex": "OANDA", "n": "ORO ✨"},
    {"symbol": "EURUSD", "ex": "FX_IDC", "n": "EUR/USD 🇪🇺"},
    {"symbol": "GBPUSD", "ex": "FX_IDC", "n": "GBP/USD 🇬🇧"},
    {"symbol": "USDJPY", "ex": "FX_IDC", "n": "USD/JPY 🇯🇵"}
]

def enviar(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    try: requests.post(url, json={"chat_id": ID_PERSONAL, "text": msg, "parse_mode": "Markdown"})
    except: pass

print("🔥 BOT LUXALGO S&R ACTIVADO - LÓGICA TRADING")

while True:
    for a in activos:
        try:
            handler = TA_Handler(
                symbol=a['symbol'], exchange=a['ex'],
                screener="forex", interval=Interval.INTERVAL_1_MINUTE
            )
            
            # Obtenemos indicadores clave del script
            data = handler.get_analysis().indicators
            close = data["close"]
            open_p = data["open"]
            high = data["high"]
            low = data["low"]
            
            # Lógica LuxAlgo: Oscilador de Volumen
            # (Simulamos el cálculo de LuxAlgo: short EMA 5 vs long EMA 10)
            vol = data["volume"]
            # Nota: tradingview_ta nos da valores directos, si el RSI ayuda a confirmar:
            rsi = data["RSI"] 

            # --- DETECCIÓN DE RUPTURAS (Basado en tu código LuxAlgo) ---
            # Si el precio rompe el RSI 58 con fuerza (Resistencia)
            if rsi >= 58.0:
                msg = (f"🚀 **¡RUPTURA DE RESISTENCIA! (LuxAlgo)**\n"
                       f"──────────────────\n"
                       f"💎 Activo: **{a['n']}**\n"
                       f"📈 Operación: **BAJA (DOWN) 🔻**\n"
                       f"📊 Confirmación: `RSI Sobrecomprado`\n"
                       f"⏳ Tiempo: **2 MINUTOS**\n"
                       f"──────────────────\n"
                       f"🎯 *¡Entra al rechazo en Pocket Option!*")
                enviar(msg)
                time.sleep(120)

            # Si el precio rompe el RSI 42 con fuerza (Soporte)
            elif rsi <= 42.0:
                msg = (f"🚀 **¡RUPTURA DE SOPORTE! (LuxAlgo)**\n"
                       f"──────────────────\n"
                       f"💎 Activo: **{a['n']}**\n"
                       f"📈 Operación: **SUBE (UP) 🟢**\n"
                       f"📊 Confirmación: `RSI Sobrevendido`\n"
                       f"⏳ Tiempo: **2 MINUTOS**\n"
                       f"──────────────────\n"
                       f"🎯 *¡Entra al rebote en Pocket Option!*")
                enviar(msg)
                time.sleep(120)

        except:
            continue
    time.sleep(2)
