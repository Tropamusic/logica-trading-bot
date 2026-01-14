import time
import requests
import threading
from tradingview_ta import TA_Handler, Interval

# --- DATOS DE LÓGICA TRADING ---
TOKEN = "8596292166:AAHL3VHIZOS1rKh9NsteznCcbHoOdtnIK90" 
ID_PERSONAL = "6717348273"

bloqueo = False

# Activos seleccionados para Mercado Real
activos = [
    {"symbol": "XAUUSD", "ex": "OANDA", "n": "ORO ✨"},
    {"symbol": "EURUSD", "ex": "FX_IDC", "n": "EUR/USD 🇪🇺"},
    {"symbol": "GBPUSD", "ex": "FX_IDC", "n": "GBP/USD 🇬🇧"},
    {"symbol": "USDJPY", "ex": "FX_IDC", "n": "USD/JPY 🇯🇵"}
]

def enviar_telegram(mensaje):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    try:
        requests.post(url, json={"chat_id": ID_PERSONAL, "text": mensaje, "parse_mode": "Markdown"}, timeout=10)
    except:
        pass

def desbloquear():
    global bloqueo
    bloqueo = False
    print("✅ Pausa terminada. Buscando nuevas oportunidades...")

print("🚀 MULTI-BOT LÓGICA TRADING ACTIVADO")
print("📡 Monitoreando: Oro, EURUSD, GBPUSD, USDJPY")

while True:
    if bloqueo:
        time.sleep(10)
        continue

    for a in activos:
        if bloqueo: break # Si sale señal en uno, deja de buscar en los otros
        
        try:
            handler = TA_Handler(
                symbol=a['symbol'], exchange=a['ex'],
                screener="forex", interval=Interval.INTERVAL_1_MINUTE
            )
            analisis = handler.get_analysis()
            rsi = analisis.indicators["RSI"]
            
            print(f"📊 {a['n']}: RSI {round(rsi, 2)}")

            # Lógica LuxAlgo 58/42
            if rsi >= 58.0 or rsi <= 42.0:
                bloqueo = True
                dir_msg = "BAJA (DOWN) 🔻" if rsi >= 58.0 else "SUBE (UP) 🟢"
                
                msg = (f"🔔 **¡SEÑAL ENCONTRADA!**\n"
                       f"──────────────────\n"
                       f"💎 Activo: **{a['n']}**\n"
                       f"📈 Operación: **{dir_msg}**\n"
                       f"📊 RSI: `{round(rsi, 2)}`\n"
                       f"⏳ Pausa: **2 MINUTOS**\n"
                       f"──────────────────\n"
                       f"🎯 *¡Entra ahora en Pocket Option!*")
                
                enviar_telegram(msg)
                # Tu regla de los 2 minutos de experiencia
                threading.Timer(120, desbloquear).start()
            
            # Pequeña pausa entre activos para no saturar la API
            time.sleep(3) 

        except Exception as e:
            if "429" in str(e):
                print("⚠️ Límite de API. Esperando enfriamiento...")
                time.sleep(20)
            continue

    time.sleep(5) # Pausa antes de la siguiente vuelta completa
