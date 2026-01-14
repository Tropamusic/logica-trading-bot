import time
import requests
from tradingview_ta import TA_Handler, Interval

# --- CONFIGURACIÓN LÓGICA TRADING ---
TOKEN = "8386038643:AAEngPQbBuu41WBWm7pCYQxm3yEowoJzYaw"
ID_PERSONAL = "6717348273"

activos = [
    {"symbol": "XAUUSD", "ex": "OANDA", "n": "ORO ✨"},
    {"symbol": "GBPJPY", "ex": "OANDA", "n": "GBP/JPY 💷"},
    {"symbol": "EURUSD", "ex": "FX_IDC", "n": "EUR/USD 🇪🇺"},
    {"symbol": "BTCUSD", "ex": "BITSTAMP", "n": "BITCOIN ₿"}
    # Puedes seguir agregando los que quieras aquí...
]

def enviar_alerta(msj):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    try: requests.post(url, json={"chat_id": ID_PERSONAL, "text": msj, "parse_mode": "Markdown"})
    except: pass

print("🚀 BOT LÓGICA TRADING ACTIVADO - CON PAUSA DE 2 MINUTOS")

while True:
    for a in activos:
        try:
            handler = TA_Handler(symbol=a['symbol'], exchange=a['ex'], screener="forex", interval=Interval.INTERVAL_1_MINUTE)
            analysis = handler.get_analysis()
            rsi = analysis.indicators["RSI"]
            
            print(f"🔍 {a['n']}: RSI {round(rsi, 2)}")

            # LÓGICA 58 / 42
            if rsi >= 57.7 or rsi <= 42.3:
                direccion = "BAJA (DOWN) 🔻" if rsi >= 57.7 else "SUBE (UP) 🟢"
                
                msg = (f"🚀 **¡SEÑAL LÓGICA TRADING!**\n"
                       f"──────────────────\n"
                       f"💎 Par: **{a['n']}**\n"
                       f"📈 Operación: **{direccion}**\n"
                       f"⏳ Tiempo: **2 MINUTOS**\n"
                       f"──────────────────\n"
                       f"🎯 *¡Entra ahora! Esperando cierre...*")
                
                enviar_alerta(msg)
                print(f"✅ SEÑAL ENVIADA. Entrando en pausa de 2 min...")
                
                # LA PAUSA QUE PEDISTE: El bot se duerme 120 segundos
                time.sleep(120) 
                print("🔄 Pausa terminada. Reanudando escaneo...")
                break # Sale del bucle de activos para reiniciar el ciclo limpio
                
        except Exception:
            continue
    
    time.sleep(1)
