import time
import requests
import threading
from tradingview_ta import TA_Handler, Interval

# --- DATOS DE LÓGICA TRADING ---
TOKEN = "8386038643:AAEngPQbBuu41WBWm7pCYQxm3yEowoJzYaw"
ID_PERSONAL = "6717348273"

# ACTIVOS PROFESIONALES (MERCADO REAL)
activos = [
    {"symbol": "XAUUSD", "ex": "OANDA", "n": "ORO ✨"},
    {"symbol": "EURUSD", "ex": "FX_IDC", "n": "EUR/USD 🇪🇺"},
    {"symbol": "GBPUSD", "ex": "FX_IDC", "n": "GBP/USD 🇬🇧"},
    {"symbol": "USDJPY", "ex": "FX_IDC", "n": "USD/JPY 🇯🇵"},
    {"symbol": "AUDUSD", "ex": "FX_IDC", "n": "AUD/USD 🇦🇺"},
    {"symbol": "USDCAD", "ex": "FX_IDC", "n": "USD/CAD 🇨🇦},
    {"symbol": "USDCHF", "ex": "FX_IDC", "n": "USD/CHF 🇨🇭"}
]

bloqueo = False

def enviar(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    try:
        requests.post(url, json={"chat_id": ID_PERSONAL, "text": msg, "parse_mode": "Markdown"}, timeout=10)
    except:
        print("⚠️ Error de conexión con Telegram...")

def liberar():
    global bloqueo
    enviar("🏁 **Análisis finalizado.** Buscando nueva entrada segura en Mercado Real...")
    bloqueo = False
    print("🔄 Bot desbloqueado. Escaneando...")

print("🚀 LÓGICA TRADING: BOT MERCADO REAL + RSI ACTIVADO")
print("📉 Estrategia: RSI 58/42 - Sin pausas por error.")

# BUCLE INFINITO (NUNCA SE APAGA)
while True:
    try:
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
                           f"📊 RSI Real: `{round(rsi, 2)}`\n"
                           f"⏳ Tiempo: **2 MINUTOS**\n"
                           f"──────────────────\n"
                           f"🎯 *Lógica Trading: Ejecuta en Mercado Real.*")
                    
                    enviar(msg)
                    
                    # Temporizador de 2 minutos (120 seg)
                    threading.Timer(120, liberar).start()
                    break 

            except Exception:
                continue 

        time.sleep(0.5)

    except Exception as e:
        print(f"⚠️ Reiniciando sistema... Error: {e}")
        time.sleep(5)
        continue
