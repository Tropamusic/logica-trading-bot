import time
import requests
import threading
from tradingview_ta import TA_Handler, Interval

# --- CONFIGURACIÓN ---
TOKEN = "8386038643:AAEngPQbBuu41WBWm7pCYQxm3yEowoJzYaw"
ID_PERSONAL = "6717348273"

# ACTIVOS TOP EN POCKET OPTION (Mercado Real)
activos = [
    {"symbol": "XAUUSD", "ex": "OANDA", "n": "ORO ✨", "scr": "forex"},
    {"symbol": "BTCUSD", "ex": "BITSTAMP", "n": "BITCOIN ₿", "scr": "crypto"},
    {"symbol": "EURUSD", "ex": "FX_IDC", "n": "EUR/USD 🇪🇺", "scr": "forex"},
    {"symbol": "GBPUSD", "ex": "FX_IDC", "n": "GBP/USD 🇬🇧", "scr": "forex"},
    {"symbol": "USDJPY", "ex": "FX_IDC", "n": "USD/JPY 🇯🇵", "scr": "forex"},
    {"symbol": "USOIL", "ex": "TVC", "n": "PETRÓLEO 🛢️", "scr": "cfd"}
]

bloqueo = False

def enviar(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    try: requests.post(url, json={"chat_id": ID_PERSONAL, "text": msg, "parse_mode": "Markdown"}, timeout=10)
    except: print("⚠️ Error de conexión con Telegram...")

print("✅ BOT LÓGICA TRADING CONFIGURADO PARA POCKET OPTION")
print("📡 Escaneando señales de alta precisión...")

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
            
            data = handler.get_analysis()
            rsi = data.indicators["RSI"]
            rec = data.summary["RECOMMENDATION"]
            precio = data.indicators["close"]
            
            # Monitor para que veas el trabajo del bot
            print(f"🔍 {a['n']} | RSI: {round(rsi, 2)} | {rec}")

            # Lógica de Confluencia: RSI + Fuerza del mercado
            disparar = False
            if rsi >= 57.8 and "SELL" in rec:
                dir_msg = "VENTA (DOWN) 🔻"
                disparar = True
            elif rsi <= 42.2 and "BUY" in rec:
                dir_msg = "COMPRA (UP) 🟢"
                disparar = True

            if disparar:
                bloqueo = True
                
                msg = (f"🚀 **¡SEÑAL LÓGICA TRADING!**\n"
                       f"──────────────────\n"
                       f"💎 Activo: **{a['n']}**\n"
                       f"📈 Dirección: **{dir_msg}**\n"
                       f"📊 RSI: `{round(rsi, 2)}` | `{rec}`\n"
                       f"⏳ Tiempo: **2 MINUTOS**\n"
                       f"──────────────────\n"
                       f"🎯 *¡Entra ya en Pocket Option!*")
                
                enviar(msg)
                
                # Función de cierre y desbloqueo tras 2 minutos
                def finalizar():
                    global bloqueo
                    enviar(f"🏁 **Operación finalizada en {a['n']}.**\nBuscando siguiente profit...")
                    bloqueo = False
                
                threading.Timer(120, finalizar).start()
                break

        except:
            continue

    time.sleep(0.5)
