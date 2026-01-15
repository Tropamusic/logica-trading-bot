import time
import requests
import threading
from tradingview_ta import TA_Handler, Interval

# --- DATOS DE LÓGICA TRADING ---
TOKEN = "8596292166:AAHL3VHIZOS1rKh9NsteznCcbHoOdtnIK90" 
ID_PERSONAL = "6717348273"
BOT_NAME = "🔱 LÓGICA TRADING PRO"

bloqueo = False
contador_senales = 0
wins, losses = 0, 0
historial_log = []
LIMITE_SENALES = 5
TIEMPO_ENFRIAMIENTO = 1800 

# Mantenemos tus 10 activos configurados
activos_config = [
    {"s": "XAUUSD", "e": "OANDA", "n": "ORO ✨"},
    {"s": "EURUSD", "e": "FX_IDC", "n": "EUR/USD 🇪🇺"},
    {"s": "GBPUSD", "e": "FX_IDC", "n": "GBP/USD 🇬🇧"},
    {"s": "USDJPY", "e": "FX_IDC", "n": "USD/JPY 🇯🇵"},
    {"s": "AUDUSD", "e": "FX_IDC", "n": "AUD/USD 🇦🇺"},
    {"s": "USDCAD", "e": "FX_IDC", "n": "USD/CAD 🇨🇦"},
    {"s": "EURJPY", "e": "FX_IDC", "n": "EUR/JPY 🇪🇺🇯🇵"},
    {"s": "GBPJPY", "e": "FX_IDC", "n": "GBP/JPY 🇬🇧🇯🇵"},
    {"s": "NZDUSD", "e": "FX_IDC", "n": "NZD/USD 🇳🇿"},
    {"s": "USDCHF", "e": "FX_IDC", "n": "USD/CHF 🇨🇭"}
]

analistas = []
for a in activos_config:
    analistas.append({
        "handler": TA_Handler(symbol=a['s'], exchange=a['e'], screener="forex", interval=Interval.INTERVAL_1_MINUTE),
        "n": a['n']
    })

def enviar_telegram(mensaje):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    try: requests.post(url, json={"chat_id": ID_PERSONAL, "text": mensaje, "parse_mode": "Markdown"}, timeout=10)
    except: pass

def verificar_resultado(handler, nombre_activo, precio_entrada, direccion):
    global wins, losses, bloqueo, historial_log
    time.sleep(120) 
    try:
        precio_final = handler.get_analysis().indicators["close"]
        exito = (direccion == "BAJA" and precio_final < precio_entrada) or (direccion == "SUBE" and precio_final > precio_entrada)
        res_txt = "WIN ✅" if exito else "LOSS ❌"
        if exito: wins += 1
        else: losses += 1
        historial_log.append(f"- {nombre_activo}: {res_txt}")
        enviar_telegram(f"🏁 **{res_txt}: {nombre_activo}**\nEntrada: `{precio_entrada}` | Cierre: `{precio_final}`")
    except: pass
    bloqueo = False

print(f"🚀 {BOT_NAME} - MODO ACTIVIDAD ALTA")
enviar_telegram(f"🚀 **{BOT_NAME} REESTABLECIDO**\n📡 Buscando señales con alta sensibilidad...")

while True:
    if contador_senales >= LIMITE_SENALES:
        # (Código de reporte se mantiene igual para no cambiar nada de lo que pediste)
        total = wins + losses
        efect = (wins / total * 100) if total > 0 else 0
        diario = "\n".join(historial_log)
        enviar_telegram(f"📊 **REPORTE**\nEfectividad: {round(efect, 2)}%\n{diario}")
        time.sleep(TIEMPO_ENFRIAMIENTO)
        contador_senales, wins, losses, historial_log = 0, 0, 0, []

    if bloqueo:
        time.sleep(5) # Reducido para reaccionar más rápido tras el desbloqueo
        continue

    for a in analistas:
        if bloqueo or contador_senales >= LIMITE_SENALES: break
        try:
            # Captura de datos ultra rápida
            analisis = a["handler"].get_analysis()
            rsi = analisis.indicators["RSI"]
            precio_actual = analisis.indicators["close"]
            
            # IMPRESIÓN EN CONSOLA PARA QUE VEAS QUE ESTÁ VIVO
            print(f"👀 Escaneando {a['n']}: RSI {round(rsi, 2)}")

            # REGLA DE ACTIVIDAD: Si toca tus niveles, envía sin dudar
            if rsi >= 58.0 or rsi <= 42.0:
                bloqueo = True
                contador_senales += 1
                dir_op = "BAJA" if rsi >= 58.0 else "SUBE"
                
                enviar_telegram(f"🔔 **SEÑAL #{contador_senales}: {a['n']}**\n📈 Operación: **{dir_op}**\n📊 RSI: `{round(rsi, 2)}` | Precio: `{precio_actual}`")
                
                threading.Thread(target=verificar_resultado, args=(a["handler"], a["n"], precio_actual, dir_op)).start()
            
            time.sleep(2) # Reducido de 5 a 2 segundos para no perder señales en mercado rápido
        except Exception as e:
            time.sleep(10)
            continue
    time.sleep(2)
