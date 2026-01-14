import time
import requests
import threading
from datetime import datetime
import pytz 
from tradingview_ta import TA_Handler, Interval

# --- DATOS DE LÓGICA TRADING ---
TOKEN = "8386038643:AAEngPQbBuu41WBWm7pCYQxm3yEowoJzYaw"
ID_PERSONAL = "6717348273"
BOT_NAME = "Lógica Trading 📊"
MI_ZONA_HORARIA = pytz.timezone('America/Caracas') 

conteo_alertas = 0
bloqueo_operacion_activa = False 

def enviar_telegram(mensaje, destino):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": destino, "text": mensaje, "parse_mode": "Markdown"}
    try: requests.post(url, json=payload, timeout=10)
    except: print("⚠️ Error temporal de Telegram, reintentando...")

def desbloquear_bot():
    global bloqueo_operacion_activa
    bloqueo_operacion_activa = False
    print("🔄 [SISTEMA] Pausa de 2 min terminada. Escaneando mercado real...")

# --- LISTA MAESTRA DE ACTIVOS ---
activos = [
    {"trading": "XAUUSD", "ex": "OANDA", "display": "ORO (GOLD) ✨", "type": "forex"},
    {"trading": "USOIL", "ex": "TVC", "display": "PETRÓLEO WTI 🛢️", "type": "forex"},
    {"trading": "BTCUSD", "ex": "BITSTAMP", "display": "BITCOIN (BTC) ₿", "type": "crypto"},
    {"trading": "ETHUSD", "ex": "BITSTAMP", "display": "ETHEREUM (ETH) ⟠", "type": "crypto"},
    {"trading": "EURUSD", "ex": "FX_IDC", "display": "EUR/USD 🇪🇺", "type": "forex"},
    {"trading": "GBPUSD", "ex": "FX_IDC", "display": "GBP/USD 🇬🇧", "type": "forex"},
    {"trading": "GBPJPY", "ex": "FX_IDC", "display": "GBP/JPY 💷", "type": "forex"},
    {"trading": "USDJPY", "ex": "FX_IDC", "display": "USD/JPY 🇯🇵", "type": "forex"},
    {"trading": "AUDUSD", "ex": "FX_IDC", "display": "AUD/USD 🇦🇺", "type": "forex"}
]

print(f"🚀 {BOT_NAME} - MODO ANTI-APAGADO ACTIVADO.")

# BUCLE PRINCIPAL QUE NUNCA MUERE
while True:
    try:
        ahora = datetime.now(MI_ZONA_HORARIA)
        if ahora.hour == 0 and ahora.minute == 0:
            conteo_alertas = 0

        if bloqueo_operacion_activa:
            time.sleep(5)
            continue

        for activo in activos:
            if bloqueo_operacion_activa: break 

            try:
                handler = TA_Handler(
                    symbol=activo['trading'], 
                    exchange=activo['ex'], 
                    screener=activo['type'], 
                    interval=Interval.INTERVAL_1_MINUTE
                )
                analysis = handler.get_analysis()
                rsi = analysis.indicators["RSI"]
                precio = analysis.indicators["close"]

                # Lógica 58/42
                if rsi >= 58 or rsi <= 42:
                    bloqueo_operacion_activa = True 
                    conteo_alertas += 1
                    direccion = "BAJA (DOWN) 🔻" if rsi >= 58 else "SUBE (UP) 🟢"
                    
                    msg = (f"🚀 **¡ENTRADA LÓGICA TRADING!**\n"
                           f"──────────────────\n"
                           f"💎 Activo: **{activo['display']}**\n"
                           f"📈 Operación: **{direccion}**\n"
                           f"💵 Precio: `{round(precio, 5)}`\n"
                           f"⏳ Tiempo: **2 MINUTOS**\n"
                           f"──────────────────\n"
                           f"🎯 *Señal #{conteo_alertas}*")
                    enviar_telegram(msg, ID_PERSONAL)
                    
                    def finalizar_y_reportar(a=activo, n=conteo_alertas):
                        reporte = (f"🏆 **¡RESULTADO EXITOSO!**\n\n"
                                   f"El activo **{a['display']}** cumplió el análisis.\n"
                                   f"Felicidades a los que operaron con **Lógica Trading** 💰")
                        enviar_telegram(reporte, ID_PERSONAL)
                        desbloquear_bot()

                    # BLOQUEO DE 2 MINUTOS PARA NO SATURAR
                    threading.Timer(135, finalizar_y_reportar).start()
                    break 

            except Exception:
                continue 
        
        time.sleep(2)

    except Exception as e:
        # SI ALGO FALLA, EL BOT NO SE APAGA, SE REINICIA SOLO
        print(f"⚠️ Error detectado: {e}. Reiniciando sistema en 10 segundos...")
        time.sleep(10)
        continue
