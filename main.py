import time
import requests
import threading
from datetime import datetime, timedelta
import pytz 
from tradingview_ta import TA_Handler, Interval

# --- CONFIGURACIÓN DE LÓGICA TRADING ---
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

# --- RESPUESTAS AUTOMÁTICAS PARA NUEVOS USUARIOS ---
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
                        bienvenida = f"👋 **¡Hola! Bienvenido a {BOT_NAME}**\n\nÚnete a nuestro canal VIP para señales gratuitas:\n{LINK_VIP}"
                        enviar_telegram(bienvenida, chat_id)
                    offset = update["update_id"] + 1
        except: pass
        time.sleep(2)

threading.Thread(target=responder_mensajes, daemon=True).start()

# --- BUCLE DE ANÁLISIS DE MERCADO ---
while True:
    if conteo_alertas < LIMITE_ALERTAS:
        # Pares principales para analizar
        activos = [
            {"trading": "EURUSD", "display": "EUR/USD"},
            {"trading": "GBPUSD", "display": "GBP/USD"},
            {"trading": "USDJPY", "display": "USD/JPY"},
            {"trading": "AUDUSD", "display": "AUD/USD"}
        ]
        
        for activo in activos:
            if conteo_alertas >= LIMITE_ALERTAS: break
            
            try:
                # Análisis basado en TradingView (Velas de 1 min)
                handler = TA_Handler(symbol=activo['trading'], exchange="FX_IDC", screener="forex", interval=Interval.INTERVAL_1_MINUTE)
                analysis = handler.get_analysis()
                rsi = analysis.indicators["RSI"]
                precio_entrada = analysis.indicators["close"]
                
                # Sincronizado con tu configuración 55/45
                es_venta = rsi >= 55
                es_compra = rsi <= 45
                
                if es_venta or es_compra:
                    conteo_alertas += 1
                    direccion = "BAJA (DOWN) 🔻" if es_venta else "SUBE (UP) 🟢"
                    
                    # Alerta para Lógica Trading
                    msg = (f"⚠️  **ALERTA #{conteo_alertas} / {LIMITE_ALERTAS}** ⚠️\n"
                           f"──────────────────\n"
                           f"💱 Par: **{activo['display']}**\n"
                           f"📈 Operación: **{direccion}**\n"
                           f"⏰ Tiempo: 2 Minutos\n"
                           f"──────────────────\n"
                           f"📢 **Gestiona tu riesgo y opera con disciplina.**")
                    enviar_telegram(msg, ID_PERSONAL)
                    
                    # Esperar 2 minutos de expiración
                    time.sleep(125) 
                    
                    # Verificación de resultado
                    check = handler.get_analysis()
                    precio_final = check.indicators["close"]
                    ganada = (es_venta and precio_final < precio_entrada) or (es_compra and precio_final > precio_entrada)
                    
                    if ganada:
                        res_msg = f"✅ **RESULTADO: ¡WIN!** ✅\n💰 Par: {activo['display']}\n🔥 *¡Sube tu captura al VIP, Lógica Trading!*"
                    else:
                        res_msg = f"❌ **RESULTADO: LOSS** ❌\n📊 Par: {activo['display']}\nTranquilo, mantenemos la gestión de riesgo."
                    
                    enviar_telegram(res_msg, ID_PERSONAL)
                    
                    if conteo_alertas < LIMITE_ALERTAS:
                        time.sleep(300) # Pausa de 5 min entre señales
                    
            except: continue
            time.sleep(2)
    else:
        # --- DESCANSO DE 30 MINUTOS CON PRE-AVISO ---
        reinicio_dt = datetime.now(MI_ZONA_HORARIA) + timedelta(minutes=TIEMPO_DESCANSO_MINUTOS)
        reinicio_str = reinicio_dt.strftime('%I:%M %p')
        
        msg_descanso = (f"😴 **BLOQUE COMPLETADO (4/4)**\n"
                        f"──────────────────\n"
                        f"Sesión terminada. Descanso de 30 min.\n"
                        f"🔄 Regresamos a las: **{reinicio_str}**")
        enviar_telegram(msg_descanso, ID_PERSONAL)
        
        # Esperar 25 minutos
        time.sleep(1500) 
        
        # Pre-aviso para los usuarios
        msg_preaviso = (f"⏳ **¡ATENCIÓN EQUIPO!**\n"
                        f"──────────────────\n"
                        f"Faltan **5 MINUTOS** para el próximo bloque.\n"
                        f"Preparen sus brokers. ¡Vamos por más profits!")
        enviar_telegram(msg_preaviso, ID_PERSONAL)
        
        # Últimos 5 minutos
        time.sleep(300)
        
        conteo_alertas = 0 
        enviar_telegram(f"⚡ **¡ESTAMOS DE VUELTA!**\nBuscando nuevas señales para Lógica Trading.", ID_PERSONAL)
