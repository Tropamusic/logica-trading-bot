import time
import requests
import threading
from tradingview_ta import TA_Handler, Interval

# --- CONFIGURACIÓN LÓGICA TRADING ---
TOKEN = "8386038643:AAEngPQbBuu41WBWm7pCYQxm3yEowoJzYaw"
ID_PERSONAL = "6717348273"

# LISTA COMPLETA DE ACTIVOS (TODOS LOS MERCADOS)
activos = [
    # Metales y Energía
    {"symbol": "XAUUSD", "ex": "OANDA", "n": "ORO ✨"},
    {"symbol": "USOIL", "ex": "TVC", "n": "PETRÓLEO 🛢️"},
    # Forex - Pares Mayores
    {"symbol": "EURUSD", "ex": "FX_IDC", "n": "EUR/USD 🇪🇺"},
    {"symbol": "GBPUSD", "ex": "FX_IDC", "n": "GBP/USD 🇬🇧"},
    {"symbol": "USDJPY", "ex": "FX_IDC", "n": "USD/JPY 🇯🇵"},
    {"symbol": "AUDUSD", "ex": "FX_IDC", "n": "AUD/USD 🇦🇺"},
    {"symbol": "USDCAD", "ex": "FX_IDC", "n": "USD/CAD 🇨🇦"},
    {"symbol": "USDCHF", "ex": "FX_IDC", "n": "USD/CHF 🇨🇭"},
    {"symbol": "NZDUSD", "ex": "FX_IDC", "n": "NZD/USD 🇳🇿"},
    # Forex - Cruces Volátiles (Tus favoritos)
    {"symbol": "GBPJPY", "ex": "FX_IDC", "n": "GBP/JPY 💷"},
    {"symbol": "EURJPY", "ex": "FX_IDC", "n": "EUR/JPY 💹"},
    {"symbol": "EURGBP", "ex": "FX_IDC", "n": "EUR/GBP 🇪🇺🇬🇧"},
    {"symbol": "AUDJPY", "ex": "FX_IDC", "n": "AUD/JPY 🇦🇺🇯🇵"},
    # Cripto (Para tener acción 24/7)
    {"symbol": "BTCUSD", "ex": "BITSTAMP", "n": "BITCOIN ₿"},
    {"symbol": "ETHUSD", "ex": "BITSTAMP", "n": "ETHEREUM ⟠"}
]

print(f"🚀 LÓGICA TRADING: Escaneando {len(activos)} activos simultáneamente...")

def enviar_alerta(msj):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    try:
        requests.post(url, json={"chat_id": ID_PERSONAL, "text": msj, "parse_mode": "Markdown"}, timeout=10)
    except:
        print("❌ Error enviando a Telegram")

while True:
    for a in activos:
        try:
            handler = TA_Handler(
                symbol=a['symbol'],
                exchange=a['ex'],
                screener="forex" if "USD" in a['symbol'] or "JPY" in a['symbol'] else "crypto",
                interval=Interval.INTERVAL_1_MINUTE
            )
            analysis = handler.get_analysis()
            rsi = analysis.indicators["RSI"]
            
            # Monitor en consola para ver el flujo constante
            print(f"🕒 {a['n']}: RSI {round(rsi, 2)}")

            # LÓGICA 58 / 42 (Ajuste Sniper para MT5)
            if rsi >= 57.7 or rsi <= 42.3:
                direccion = "BAJA (DOWN) 🔻" if rsi >= 57.7 else "SUBE (UP) 🟢"
                
                msg = (f"🚀 **¡SEÑAL LÓGICA TRADING!**\n"
                       f"──────────────────\n"
                       f"💎 Par: **{a['n']}**\n"
                       f"📈 Operación: **{direccion}**\n"
                       f"📊 RSI actual: `{round(rsi, 2)}`\n"
                       f"⏳ Tiempo: **2 MINUTOS**\n"
                       f"──────────────────\n"
                       f"🎯 *¡Operación detectada! Entra ya.*")
                
                enviar_alerta(msg)
                print(f"✅ ¡ALERTA DISPARADA EN {a['symbol']}!")
                # Esperamos un poco para no saturar con el mismo activo
                time.sleep(5) 
                
        except Exception:
            continue
    
    # Pausa de 1 segundo entre ciclos de escaneo total
    time.sleep(1)
