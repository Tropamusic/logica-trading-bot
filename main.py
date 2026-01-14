import time
import requests
import threading
from tradingview_ta import TA_Handler, Interval

# --- DATOS DE LÓGICA TRADING ---
TOKEN = "8596292166:AAHL3VHIZOS1rKh9NsteznCcbHoOdtnIK90" 
ID_PERSONAL = "6717348273"

bloqueo = False

def enviar_telegram(mensaje):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": ID_PERSONAL,
        "text": mensaje,
        "parse_mode": "Markdown"
    }
    try:
        requests.post(url, json=payload, timeout=10)
    except:
        print("⚠️ Error de conexión con Telegram.")

def desbloquear():
    global bloqueo
    bloqueo = False
    print("🔄 Sistema listo. Escaneando Mercado Real...")

# Configuración Sniper para ORO (Mercado Real OANDA)
oro = TA_Handler(
    symbol="XAUUSD",
    exchange="OANDA",
    screener="forex",
    interval=Interval.INTERVAL_1_MINUTE
)

print("🚀 LÓGICA TRADING ACTIVADA")
print("🔱 Bot operando en ORO (RSI 58/42)")
print("🛡️ Seguridad: Bloqueo de 2 min tras señal.")

while True:
    if bloqueo:
        time.sleep(5)
        continue

    try:
        # Analizamos TradingView
        analisis = oro.get_analysis()
        rsi = analisis.indicators["RSI"]
        precio = analisis.indicators["close"]
        
        print(f"📊 ORO: ${precio} | RSI: {round(rsi, 2)}")

        # Lógica de señales LuxAlgo
        if rsi >= 58.0 or rsi <= 42.0:
            bloqueo = True
            direccion = "BAJA (DOWN) 🔻" if rsi >= 58.0 else "SUBE (UP) 🟢"
            
            msg = (f"🔱 **ORO: SEÑAL DE ALTA PRECISIÓN**\n"
                   f"──────────────────\n"
                   f"📈 Operación: **{direccion}**\n"
                   f"📊 RSI Real: `{round(rsi, 2)}`\n"
                   f"💵 Precio: `${precio}`\n"
                   f"⏳ Pausa de Seguridad: **2 MINUTOS**\n"
                   f"──────────────────\n"
                   f"🎯 *Lógica Trading: Opera solo en Mercado Real.*")
            
            enviar_telegram(msg)
            
            # Aplicamos tu instrucción de los 2 minutos de experiencia
            threading.Timer(120, desbloquear).start()

    except Exception as e:
        print(f"📡 Buscando señal estable... ({e})")
    
    time.sleep(2)
