import time
import requests
import threading
from tradingview_ta import TA_Handler, Interval

# --- DATOS DE LÓGICA TRADING ---
TOKEN = "8596292166:AAHL3VHIZOS1rKh9NsteznCcbHoOdtnIK90" 
ID_PERSONAL = "6717348273"

# CONTADORES DE SESIÓN
bloqueo = False
contador_senales = 0
wins = 0
losses = 0
LIMITE_SENALES = 5
TIEMPO_ENFRIAMIENTO = 1800 

analistas = [
    {"handler": TA_Handler(symbol="XAUUSD", exchange="OANDA", screener="forex", interval=Interval.INTERVAL_1_MINUTE), "n": "ORO ✨"},
    {"handler": TA_Handler(symbol="EURUSD", exchange="FX_IDC", screener="forex", interval=Interval.INTERVAL_1_MINUTE), "n": "EUR/USD 🇪🇺"},
    {"handler": TA_Handler(symbol="GBPUSD", exchange="FX_IDC", screener="forex", interval=Interval.INTERVAL_1_MINUTE), "n": "GBP/USD 🇬🇧"},
    {"handler": TA_Handler(symbol="USDJPY", exchange="FX_IDC", screener="forex", interval=Interval.INTERVAL_1_MINUTE), "n": "USD/JPY 🇯🇵"}
]

def enviar_telegram(mensaje):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    try:
        requests.post(url, json={"chat_id": ID_PERSONAL, "text": mensaje, "parse_mode": "Markdown"}, timeout=10)
    except: pass

def verificar_resultado(handler, nombre_activo, precio_entrada, direccion):
    """Verifica el resultado real tras 2 minutos"""
    global wins, losses, bloqueo
    time.sleep(120)
    try:
        precio_final = handler.get_analysis().indicators["close"]
        
        if (direccion == "BAJA" and precio_final < precio_entrada) or \
           (direccion == "SUBE" and precio_final > precio_entrada):
            res_txt = "WIN (GANADA) ✅"
            icono = "💰"
            wins += 1
        else:
            res_txt = "LOSS (PERDIDA) ❌"
            icono = "📉"
            losses += 1
            
        msg_res = (f"{icono} **RESULTADO: {nombre_activo}**\n"
                   f"🏁: {res_txt}\n"
                   f"Entrada: `{precio_entrada}` | Cierre: `{precio_final}`")
        enviar_telegram(msg_res)
    except: pass
    bloqueo = False

print("🚀 LÓGICA TRADING: MODO ESTADÍSTICAS REALES")

while True:
    # REPORTE DE SESIÓN AL LLEGAR AL LÍMITE
    if contador_senales >= LIMITE_SENALES:
        efectividad = (wins / LIMITE_SENALES) * 100
        resumen = (f"📊 **RESUMEN DE SESIÓN: LÓGICA TRADING**\n"
                   f"──────────────────\n"
                   f"✅ Ganadas: **{wins}**\n"
                   f"❌ Perdidas: **{losses}**\n"
                   f"🎯 Efectividad: **{round(efectividad, 2)}%**\n"
                   f"──────────────────\n"
                   f"🧊 *Iniciando descanso de 30 min...*")
        enviar_telegram(resumen)
        
        time.sleep(TIEMPO_ENFRIAMIENTO)
        contador_senales = 0
        wins = 0
        losses = 0
        enviar_telegram("🔄 **Sesión reiniciada.** ¡Vamos por más profit!")

    if bloqueo:
        time.sleep(10)
        continue

    for a in analistas:
        if bloqueo or contador_senales >= LIMITE_SENALES: break
        
        try:
            analisis = a["handler"].get_analysis()
            rsi = analisis.indicators["RSI"]
            precio_actual = analisis.indicators["close"]
            
            print(f"📊 {a['n']}: RSI {round(rsi, 2)} | {contador_senales}/{LIMITE_SENALES}")

            if rsi >= 58.0 or rsi <= 42.0:
                bloqueo = True
                contador_senales += 1
                dir_op = "BAJA" if rsi >= 58.0 else "SUBE"
                emoji = "🔻" if dir_op == "BAJA" else "🟢"
                
                enviar_telegram(f"🔔 **SEÑAL #{contador_senales}: {a['n']}**\n"
                                f"📈 Operación: **{dir_op} {emoji}**\n"
                                f"📊 RSI: `{round(rsi, 2)}` | Precio: `{precio_actual}`")
                
                threading.Thread(target=verificar_resultado, args=(a["handler"], a["n"], precio_actual, dir_op)).start()
            
            time.sleep(6) 

        except Exception as e:
            if "429" in str(e): time.sleep(120)
            continue

    time.sleep(10)
