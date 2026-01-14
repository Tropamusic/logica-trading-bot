import time
import requests
import threading
from tradingview_ta import TA_Handler, Interval

# --- DATOS DE LÓGICA TRADING ---
TOKEN = "8386038643:AAEngPQbBuu41WBWm7pCYQxm3yEowoJzYaw"
ID_PERSONAL = "6717348273"

# ACTIVOS PROFESIONALES DE ALTA LIQUIDEZ (Pocket Option Ready)
activos = [
    {"symbol": "XAUUSD", "ex": "OANDA", "n": "ORO ✨"},
    {"symbol": "EURUSD", "ex": "FX_IDC", "n": "EUR/USD 🇪🇺"},
    {"symbol": "GBPUSD", "ex": "FX_IDC", "n": "GBP/USD 🇬🇧"},
    {"symbol": "USDJPY", "ex": "FX_IDC", "n": "USD/JPY 🇯🇵"},
    {"symbol": "AUDUSD", "ex": "FX_IDC", "n": "AUD/USD 🇦🇺"},
    {"symbol": "USDCAD", "ex": "FX_IDC", "n": "USD/CAD 🇨🇦"},
    {"symbol": "USDCHF", "ex": "FX_IDC", "n": "USD/CHF 🇨🇭"}
]

bloqueo = False

def enviar(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    try:
        requests.post(url, json={"chat_id": ID_PERSONAL, "text": msg, "parse_mode": "Markdown"}, timeout=10)
    except:
        pass

print("🚀 LÓGICA TRADING: Bot Profesional Activado.")
print("📉 Enfocado en ORO y Divisas Principales (RSI 58/42).")

while True:
    if bloqueo:
        time.sleep(1)
        continue

    for a in activos:
        if bloqueo: break
        try:
            handler = TA_Handler(
                symbol=a['symbol'],
                exchange=a['ex'],
                screener="forex",
                interval=Interval.INTERVAL_1_MINUTE
            )
            
            data = handler.get_analysis().indicators
            rsi = data["RSI"]
            
            # Monitor en consola para control total
            print(f"📊 {a['n']}: RSI {round(rsi, 2)}")

            # LÓGICA RSI ORIGINAL 58/42
            if rsi >= 58.0 or rsi <= 42.0:
                bloqueo = True
                direccion = "BAJA (DOWN) 🔻" if rsi >= 58.0 else "SUBE (UP) 🟢"
                
                msg = (f"🚀 **¡ENTRADA PROFESIONAL!**\n"
                       f"──────────────────\n"
                       f"💎 Par: **{a['n']}**\n"
                       f"📈 Operación: **{direccion}**\n"
                       f"📊 RSI: `{round(rsi, 2)}`\n"
                       f"⏳ Tiempo: **2 MINUTOS**\n"
                       f"──────────────────\n"
                       f"🎯 *Lógica Trading: Ejecuta en Pocket Option.*")
                
                enviar(msg)
                
                # PAUSA DE 2 MINUTOS PARA EVITAR SATURACIÓN
                def liberar():
                    global bloqueo
                    enviar(f"🏁 **Análisis finalizado.**\nBuscando siguiente entrada...")
                    bloqueo = False
                
                threading.Timer(120, liberar).start()
                break 

        except:
            continue

    time.sleep(0.5)
