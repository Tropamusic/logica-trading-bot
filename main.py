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
TIEMPO_DESCANSO_MINUTOS = 30

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
        activos = [
            {"trading": "EURUSD", "display": "EUR/USD"},
            {"trading": "GBPUSD", "display": "GBP/USD"},
            {"trading": "USDJPY", "display": "USD/JPY"},
            {"trading": "AUDUSD", "display": "AUD/USD"}
        ]
        
        for activo in activos:
            if conteo_alertas >= LIMITE_ALERTAS: break
            
            try:
                handler = TA_Handler(symbol=activo['trading'], exchange="FX_IDC", screener="forex", interval=Interval.INTERVAL_1_MINUTE)
                analysis = handler.get_analysis()
                rsi = analysis.indicators["RSI"]
                precio_entrada = analysis.indicators["close"]
                
                if rsi >= 55 or rsi <= 45:
                    conteo_alertas += 1
                    direccion = "BAJA (DOWN) 🔻" if rsi >= 55 else "SUBE (UP) 🟢"
                    
                    msg = (f"⚠️  **ALERTA #{conteo_alertas} / {LIMITE_ALERTAS}** ⚠️\n"
                           f"──────────────────\n"
                           f"💱 Par: **{activo['display']}**\n"
                           f"📈 Operación: **{direccion}**\n"
                           f"⏰ Tiempo: 2 Minutos\n"
                           f"──────────────────\n"
                           f"📢 **Gestiona tu riesgo y opera con disciplina.**")
                    enviar_telegram(msg, ID_PERSONAL)
                    
                    time.sleep(125) 
                    
                    check = handler.get_analysis()
                    precio_final = check.indicators["close"]
                    ganada = (rsi >= 55 and precio_final < precio_entrada) or (rsi <= 45 and precio_final > precio_entrada)
                    
                    if ganada:
                        res_msg = f"✅ **RESULTADO: ¡WIN!** ✅\n💰 Par: {activo['display']}\n🔥 *Sube tu captura al VIP, Lógica Trading.*"
                    else:
                        res_msg = f"❌ **RESULTADO: LOSS** ❌\n📊 Par: {activo['display']}\nTranquilo, la gestión protege tu capital."
                    
                    enviar_telegram(res_msg, ID_PERSONAL)
                    
                    if conteo_alertas < LIMITE_ALERTAS:
                        time.sleep(300) 
                    
            except: continue
            time.sleep(2)
    else:
        # --- LÓGICA DE DESCANSO CON PRE-AVISO ---
        ahora = datetime.now(MI_ZONA_HORARIA)
        reinicio = (ahora + timedelta(minutes=TIEMPO_DESCANSO_MINUTOS)).strftime('%I:%M %p')
        
        msg_descanso = (f"😴 **BLOQUE COMPLETADO (4/4)**\n"
                        f"──────────────────\n"
                        f"Hemos terminado esta sesión. Descanso de 30 min.\n"
                        f"🔄 Regresamos a las: **{reinicio}**")
        enviar_telegram(msg_descanso, ID_PERSONAL)
        
        # Esperar 25 minutos (Descanso total - 5 min de aviso)
        time.sleep(1500) 
        
        # MENSAJE PRE-AVISO (5 min antes)
        msg_preaviso = (f"⏳ **¡ATENCIÓN EQUIPO!**\n"
                        f"──────────────────\n"
                        f"Faltan **5 MINUTOS** para iniciar el próximo bloque.\n"
                        f"Vayan preparando sus brokers. ¡Vamos por más!")
        enviar_telegram(msg_preaviso, ID_PERSONAL)
        
        # Esperar los últimos 5 minutos
        time.sleep(300)
        
        conteo_alertas = 0 
        enviar_telegram(f"⚡ **¡ESTAMOS DE VUELTA!**\nBuscando oportunidades en el mercado ahora mismo.", ID_PERSONAL)
