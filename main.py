import time
import requests
import threading
from tradingview_ta import TA_Handler, Interval

# --- DATOS DE LÓGICA TRADING ---
TOKEN = "8596292166:AAHL3VHIZOS1rKh9NsteznCcbHoOdtnIK90" 
ID_PERSONAL = "6717348273"

# VARIABLES DE CONTROL DE FLUJO
bloqueo = False
contador_senales = 0
LIMITE_SENALES = 5             # <--- Límite de 5 operaciones
TIEMPO_ENFRIAMIENTO = 1800     # <--- 30 Minutos (1800 segundos)

# Activos para monitoreo real
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
    print("✅ Pausa de experiencia (2 min) completada.")

print("🚀 BOT LÓGICA TRADING - NUBE READY")
print(f"🛡️ Configuración: {LIMITE_SENALES} señales -> 30 min de descanso.")

while True:
    # 1. Verificación de Límite de señales para enfriar la API
    if contador_senales >= LIMITE_SENALES:
        msg_descanso = (f"🧊 **MODO ENFRIAMIENTO TOTAL**\n"
                        f"──────────────────\n"
                        f"Se han enviado {LIMITE_SENALES} señales con éxito.\n"
                        f"Descansando **30 minutos** para proteger la API y asegurar precisión.\n"
                        f"──────────────────\n"
                        f"💤 *¡Toma un descanso, Lógica Trading!*")
        print("🧊 Iniciando descanso de 30 minutos...")
        enviar_telegram(msg_descanso)
        
        time.sleep(TIEMPO_ENFRIAMIENTO) 
        
        contador_senales = 0 # Reinicio de contador
        enviar_telegram("🔄 **¡API Refrescada!** Buscando nuevas oportunidades en el mercado...")

    if bloqueo:
        time.sleep(10)
        continue

    for a in activos:
        if bloqueo or contador_senales >= LIMITE_SENALES: break
        
        try:
            handler = TA_Handler(
                symbol=a['symbol'], exchange=a['ex'],
                screener="forex", interval=Interval.INTERVAL_1_MINUTE
            )
            analisis = handler.get_analysis()
            rsi = analisis.indicators["RSI"]
            
            print(f"📊 {a['n']}: RSI {round(rsi, 2)} | Señales: {contador_senales}/{LIMITE_SENALES}")

            # Estrategia RSI 58/42
            if rsi >= 58.0 or rsi <= 42.0:
                bloqueo = True
                contador_senales += 1
                
                direccion = "BAJA (DOWN) 🔻" if rsi >= 58.0 else "SUBE (UP) 🟢"
                
                msg = (f"🔔 **SEÑAL #{contador_senales} DETECTADA**\n"
                       f"──────────────────\n"
                       f"💎 Activo: **{a['n']}**\n"
                       f"📈 Operación: **{direccion}**\n"
                       f"📊 RSI: `{round(rsi, 2)}`\n"
                       f"⏳ Bloqueo: **2 MINUTOS**\n"
                       f"──────────────────\n"
                       f"🎯 *Lógica Trading: Entra con precisión.*")
                
                enviar_telegram(msg)
                
                # Instrucción de seguridad: 2 minutos de pausa
                threading.Timer(120, desbloquear).start()
            
            time.sleep(5) # Espacio entre activos para evitar el error 429

        except Exception as e:
            if "429" in str(e):
                print("⚠️ Error 429 detectado. Esperando un momento...")
                time.sleep(60)
            continue

    time.sleep(10) # Pausa entre ciclos de escaneo
