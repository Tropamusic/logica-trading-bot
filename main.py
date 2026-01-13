import time
import requests
import threading
from datetime import datetime, timedelta
import pytz 
from tradingview_ta import TA_Handler, Interval

# --- CONFIGURACIÓN ---
TOKEN = "8386038643:AAEngPQbBuu41WBWm7pCYQxm3yEowoJzYaw"
ID_PERSONAL = "6717348273"
LINK_VIP = "https://t.me/+tYm_D39iB8YxZDRh"
BOT_NAME = "Lógica Trading 📊"

MI_ZONA_HORARIA = pytz.timezone('America/Caracas') 

conteo_alertas = 0
LIMITE_ALERTAS = 4
TIEMPO_DESCANSO_HORA = 3600 

def enviar_telegram(mensaje, destino):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": destino, "text": mensaje, "parse_mode": "Markdown"}
    try: requests.post(url, json=payload, timeout=10)
    except: pass

# --- RESPUESTAS AUTOMÁTICAS ---
def responder_mensajes():
    offset = 0
    while True:
        try:
            url = f"https://api.telegram.org/bot{TOKEN}/getUpdates?offset={offset}&timeout=10"
            res = requests.get(url).json()
            if "result" in res:
                for update in res["result"]:
                    message = update.get("message")
                    if message and "/start" in message.get("text", ""):
                        chat_id = message["chat"]["id"]
                        bienvenida = f"👋 **Bienvenido a {BOT_NAME}**\n\nÚnete al VIP aquí:\n{LINK_VIP}"
                        enviar_telegram(bienvenida, chat_id)
                    offset = update["update_id"] + 1
        except: pass
        time.sleep(2)

threading.Thread(target=responder_mensajes, daemon=True).start()

# --- BUCLE DE ANÁLISIS ---
while True:
    if conteo_alertas < LIMITE_ALERTAS:
        activos = [{"trading": "EURUSD", "display": "EUR/USD"}, {"trading": "GBPUSD", "display": "GBP/USD"}, {"trading": "USDJPY", "display": "USD/JPY"}]
        
        for activo in activos:
            try:
                handler = TA_Handler(symbol=activo['trading'], exchange="FX_IDC", screener="forex", interval=Interval.INTERVAL_1_MINUTE)
                analysis = handler.get_analysis()
                rsi = analysis.indicators["RSI"]
                precio_entrada = analysis.indicators["close"]
                
                # Sensibilidad 55/45
                es_venta = rsi >= 55
                es_compra = rsi <= 45
                
                if es_venta or es_compra:
                    conteo_alertas += 1
                    dir_txt = "BAJA (DOWN) 🔻" if es_venta else "SUBE (UP) 🟢"
                    
                    # 1. Enviar Alerta de Entrada
                    msg = (f"⚠️  **ALERTA #{conteo_alertas} / {LIMITE_ALERTAS}** ⚠️\n"
                           f"──────────────────\n"
                           f"💱 Par: **{activo['display']}**\n"
                           f"📈 Operación: **{dir_txt}**\n"
                           f"⏰ Tiempo: 2 Minutos\n"
                           f"──────────────────\n"
                           f"📢 ¿Opera con Responsabilidad?")
                    enviar_telegram(msg, ID_PERSONAL)
                    
                    # 2. Esperar los 2 minutos de la operación + 5 segundos de margen
                    print(f"Operación en curso para {activo['display']}...")
                    time.sleep(125) 
                    
                    # 3. Verificar Resultado
                    check = handler.get_analysis()
                    precio_final = check.indicators["close"]
                    
                    ganada = (es_venta and precio_final < precio_entrada) or (es_compra and precio_final > precio_entrada)
                    
                    if ganada:
                        res_msg = f"✅ **RESULTADO: ¡WIN!** ✅\n💰 Par: {activo['display']}\n🔥 *¡Felicidades a los que la tomaron!*"
                    else:
                        res_msg = f"❌ **RESULTADO: LOSS** ❌\n📊 Par: {activo['display']}\nTranquilos, la gestión de riesgo nos protege."
                    
                    enviar_telegram(res_msg, ID_PERSONAL)
                    
                    # 4. PAUSA RECOMENDADA (5 minutos para no saturar)
                    print("Esperando 5 minutos para la próxima señal...")
                    time.sleep(300) 
                    
                    if conteo_alertas >= LIMITE_ALERTAS: break
            except: continue
    else:
        time.sleep(TIEMPO_DESCANSO_HORA)
        conteo_alertas = 0
