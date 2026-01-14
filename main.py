import time
import requests
from tradingview_ta import TA_Handler, Interval

# --- DATOS DE LÓGICA TRADING ---
TOKEN = "8386038643:AAEngPQbBuu41WBWm7pCYQxm3yEowoJzYaw"
ID_PERSONAL = "6717348273"

# Activos que cargan rápido en el celular
activos = [
    {"symbol": "XAUUSD", "ex": "OANDA", "n": "ORO ✨"},
    {"symbol": "EURUSD", "ex": "FX_IDC", "n": "EUR/USD 🇪🇺"},
    {"symbol": "GBPUSD", "ex": "FX_IDC", "n": "GBP/USD 🇬🇧"},
    {"symbol": "USDJPY", "ex": "FX_IDC", "n": "USD/JPY 🇯🇵"}
]

print("📱 MODO CELULAR ACTIVADO - LÓGICA TRADING")

while True:
    for a in activos:
        try:
            handler = TA_Handler(
                symbol=a['symbol'], exchange=a['ex'],
                screener="forex", interval=Interval.INTERVAL_1_MINUTE
            )
            rsi = handler.get_analysis().indicators["RSI"]
            print(f"📊 {a['n']}: {round(rsi, 2)}")

            # NIVEL 60/40: El nivel de los profesionales para no fallar
            if rsi >= 60.0 or rsi <= 40.0:
                dir_msg = "BAJA (DOWN) 🔻" if rsi >= 60.0 else "SUBE (UP) 🟢"
                msg = (f"🔔 **¡ENTRADA AHORA!**\n"
                       f"💎 {a['n']}\n"
                       f"📈 {dir_msg}\n"
                       f"📊 RSI: {round(rsi, 2)}\n"
                       f"🎯 *¡Entra ya a Pocket Option!*")
                
                requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                              json={"chat_id": ID_PERSONAL, "text": msg, "parse_mode": "Markdown"})
                
                # Esperamos 2 minutos para que operes tranquilo desde el cel
                time.sleep(120) 
        except:
            continue
    time.sleep(2)
