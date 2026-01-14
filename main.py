import time
import requests
import threading
from tradingview_ta import TA_Handler, Interval

# --- CREDENCIALES ---
TOKEN = "8386038643:AAEngPQbBuu41WBWm7pCYQxm3yEowoJzYaw"
ID_PERSONAL = "6717348273"

# --- ACTIVOS DE ELITE (Donde está el dinero real) ---
activos = [
    {"symbol": "XAUUSD", "ex": "OANDA", "n": "ORO ✨", "scr": "forex"},
    {"symbol": "NAS100USD", "ex": "CAPITALCOM", "n": "NASDAQ 100 💻", "scr": "indices"},
    {"symbol": "BTCUSD", "ex": "BITSTAMP", "n": "BITCOIN ₿", "scr": "crypto"},
    {"symbol": "GBPUSD", "ex": "FX_IDC", "n": "GBP/USD 🇬🇧", "scr": "forex"},
    {"symbol": "EURUSD", "ex": "FX_IDC", "n": "EUR/USD 🇪🇺", "scr": "forex"},
    {"symbol": "USOIL", "ex": "TVC", "n": "PETRÓLEO 🛢️", "scr": "cfd"}
]

bloqueo = False

def enviar_mensaje(texto):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    try: requests.post(url, json={"chat_id": ID_PERSONAL, "text": texto, "parse_mode": "Markdown"})
    except: pass

print("🧠 SISTEMA 'LÓGICA TRADING PRO' INICIADO")
print("🎯 Objetivo: Ganar dinero operando con instituciones.")

while True:
    if bloqueo:
        time.sleep(1)
        continue

    for a in activos:
        try:
            handler = TA_Handler(
                symbol=a['symbol'],
                exchange=a['ex'],
                screener=a['scr'],
                interval=Interval.INTERVAL_1_MINUTE
            )
            
            analisis = handler.get_analysis()
            rsi = analisis.indicators["RSI"]
            recomendacion = analisis.summary["RECOMMENDATION"]
            precio = analisis.indicators["close"]

            # MONITOR DE CONSOLA
            print(f"📡 {a['n']} | RSI: {round(rsi, 2)} | Status: {recomendacion}")

            # LÓGICA DE GANANCIA (CONFLUENCIA)
            # Solo entra si el RSI es extremo Y la recomendación es FUERTE
            # Esto evita señales falsas en mercados laterales.
            
            disparar = False
            if rsi >= 57.5 and "SELL" in recomendacion:
                direccion = "VENTA (DOWN) 🔻"
                disparar = True
            elif rsi <= 42.5 and "BUY" in recomendacion:
                direccion = "COMPRA (UP) 🟢"
                disparar = True

            if disparar:
                bloqueo = True
                
                msg = (f"💰 **¡OPERACIÓN DE ALTA PROBABILIDAD!**\n"
                       f"──────────────────\n"
                       f"💎 Activo: **{a['n']}**\n"
                       f"📈 Dirección: **{direccion}**\n"
                       f"💵 Precio: `{precio}`\n"
                       f"🔥 Fuerza: `{recomendacion}`\n"
                       f"⏳ Tiempo: **2 MINUTOS**\n"
                       f"──────────────────\n"
                       f"💸 *¡Haz dinero con Lógica Trading!*")
                
                enviar_mensaje(msg)
                
                # Función de cierre: 2 minutos exactos de experiencia
                def liberar_sistema():
                    global bloqueo
                    enviar_mensaje(f"🏁 **Operación finalizada.**\nRevisando resultados y buscando la próxima ganancia...")
                    bloqueo = False
                
                threading.Timer(120, liberar_sistema).start()
                break 

        except:
            continue

    time.sleep(0.5)
