import time
import requests
import threading
from tradingview_ta import TA_Handler, Interval

# --- DATOS DE LÓGICA TRADING ---
TOKEN = "8386038643:AAEngPQbBuu41WBWm7pCYQxm3yEowoJzYaw"
ID_PERSONAL = "6717348273"

# LISTA COMPLETA DE ACTIVOS (Mercado Real)
activos = [
    {"symbol": "XAUUSD", "ex": "OANDA", "n": "ORO ✨", "scr": "forex"},
    {"symbol": "BTCUSD", "ex": "BITSTAMP", "n": "BITCOIN ₿", "scr": "crypto"},
    {"symbol": "USOIL", "ex": "TVC", "n": "PETRÓLEO 🛢️", "scr": "cfd"},
    {"symbol": "EURUSD", "ex": "FX_IDC", "n": "EUR/USD 🇪🇺", "scr": "forex"},
    {"symbol": "GBPUSD", "ex": "FX_IDC", "n": "GBP/USD 🇬🇧", "scr": "forex"},
    {"symbol": "GBPJPY", "ex": "FX_IDC", "n": "GBP/JPY 💷", "scr": "forex"},
    {"symbol": "USDJPY", "ex": "FX_IDC", "n": "USD/JPY 🇯🇵", "scr": "forex"}
]

bloqueo = False

def enviar(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    try:
        requests.post(url, json={"chat_id": ID_PERSONAL, "text": msg, "parse_mode": "Markdown"}, timeout=10)
    except:
        pass

print("🚀 LÓGICA TRADING: Volviendo al RSI Clásico (58/42)")
print("📡 Escaneo directo activado. Sin filtros adicionales.")

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
                screener=a['scr'],
                interval=Interval.INTERVAL_1_MINUTE
            )
            
            data = handler.get_analysis().indicators
            rsi = data["RSI"]
            precio = data["close"]
            
            # Monitor en consola (Para ver que el bot lee todo)
            print(f"📊 {a['n']}: RSI {round(rsi, 2)}")

            # LÓGICA ORIGINAL 58/42
            if rsi >= 58.0 or rsi <= 42.0:
                bloqueo = True
                direccion = "BAJA (DOWN) 🔻" if rsi >= 58.0 else "SUBE (UP) 🟢"
                
                msg = (f"🚀 **¡ENTRADA LÓGICA TRADING!**\n"
                       f"──────────────────\n"
                       f"💎 Activo: **{a['n']}**\n"
                       f"📈 Operación: **{direccion}**\n"
                       f"📊 RSI: `{round(rsi, 2)}`\n"
                       f"⏳ Tiempo: **2 MINUTOS**\n"
                       f"──────────────────\n"
                       f"🎯 *¡Entra ya en Pocket Option!*")
                
                enviar(msg)
                
                # REGLA: 2 minutos de espera para evitar saturación
                def liberar():
                    global bloqueo
                    enviar(f"✅ **Operación finalizada.**\nBuscando nueva señal...")
                    bloqueo = False
                
                threading.Timer(120, liberar).start()
                break 

        except:
            continue

    time.sleep(0.5)
