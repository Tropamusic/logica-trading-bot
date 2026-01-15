import time
import requests
import threading
from tradingview_ta import TA_Handler, Interval

# --- DATOS DE LÓGICA TRADING ---
TOKEN = "8596292166:AAHL3VHIZOS1rKh9NsteznCcbHoOdtnIK90" 
ID_PERSONAL = "6717348273"

bloqueo = False
contador_senales = 0
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
    """Espera 2 minutos y verifica si la señal fue real y ganadora"""
    time.sleep(120)
    try:
        precio_final = handler.get_analysis().indicators["close"]
        resultado = ""
        icono = ""
        
        if direccion == "BAJA" and precio_final < precio_entrada:
            resultado = "WIN (GANADA) ✅"
            icono = "💰"
        elif direccion == "SUBE" and precio_final > precio_entrada:
            resultado = "WIN (GANADA) ✅"
            icono = "💰"
        else:
            resultado = "LOSS (PERDIDA) ❌"
            icono = "📉"
            
        msg_resultado = (f"{icono} **RESULTADO REAL: {nombre_activo}**\n"
                         f"──────────────────\n"
                         f"🏁 Resultado: **{resultado}**\n"
                         f"Precio Entrada: `{precio_entrada}`\n"
                         f"Precio Cierre: `{precio_final}`\n"
                         f"──────────────────\n"
                         f"🔄 *Sistema listo para buscar otra señal.*")
        enviar_telegram(msg_resultado)
    except:
        pass
    
    global bloqueo
    bloqueo = False

print("🚀 LÓGICA TRADING: MODO RESULTADOS REALES ACTIVADO")

while True:
    if contador_senales >= LIMITE_SENALES:
        time.sleep(TIEMPO_ENFRIAMIENTO)
        contador_senales = 0

    if bloqueo:
        time.sleep(10)
        continue

    for a in analistas:
        if bloqueo or contador_senales >= LIMITE_SENALES: break
        
        try:
            analisis = a["handler"].get_analysis()
            rsi = analisis.indicators["RSI"]
            precio_actual = analisis.indicators["close"]
            
            print(f"📊 {a['n']}: RSI {round(rsi, 2)}")

            # Lógica de Señal
            if rsi >= 58.0 or rsi <= 42.0:
                bloqueo = True
                contador_senales += 1
                dir_op = "BAJA" if rsi >= 58.0 else "SUBE"
                emoji = "🔻" if dir_op == "BAJA" else "🟢"
                
                msg = (f"🔔 **SEÑAL DETECTADA: {a['n']}**\n"
                       f"──────────────────\n"
                       f"📈 Operación: **{dir_op} {emoji}**\n"
                       f"📊 RSI: `{round(rsi, 2)}`\n"
                       f"💵 Precio Entrada: `{precio_actual}`\n"
                       f"──────────────────\n"
                       f"⏱️ *Verificando resultado en 2 min...*")
                
                enviar_telegram(msg)
                
                # Lanzamos la verificación en segundo plano para no detener el bot
                threading.Thread(target=verificar_resultado, args=(a["handler"], a["n"], precio_actual, dir_op)).start()
            
            time.sleep(6) 

        except Exception as e:
            if "429" in str(e): time.sleep(120)
            continue

    time.sleep(10)
