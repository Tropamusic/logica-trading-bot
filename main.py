import time
import requests
from tradingview_ta import TA_Handler, Interval
from datetime import datetime

# --- CONFIGURACIÓN DE CANALES ACTUALIZADA ---
TOKEN = "8386038643:AAEngPQbBuu41WBWm7pCYQxm3yEowoJzYaw"
CANAL_PRINCIPAL = "6717348273"  
CANAL_RESULTADOS = "-1003621701961" 
LINK_CANAL_PRINCIPAL = "https://t.me/+4bqyiiDGXTA4ZTRh" 
LINK_BITACORA = "https://t.me/LogicaTradingResultados"
BOT_NAME = "Lógica Trading 📊"

HORARIOS_ACTIVOS = [(8, 11), (14, 17), (20, 23)]
conteo_operaciones = 0
wins_totales, loss_totales = 0, 0
sesion_anunciada = False 
offset = 0 

def enviar_telegram(mensaje, canal_id, con_boton=False, es_bienvenida=False):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": canal_id, "text": mensaje, "parse_mode": "Markdown"}
    if con_boton:
        payload["reply_markup"] = {"inline_keyboard": [[{"text": "📥 UNIRSE AL VIP", "url": LINK_CANAL_PRINCIPAL}]]}
    if es_bienvenida:
        payload["reply_markup"] = {"inline_keyboard": [
            [{"text": "🚀 Canal Principal", "url": LINK_CANAL_PRINCIPAL}],
            [{"text": "📈 Bitácora", "url": LINK_BITACORA}]
        ]}
    try: requests.post(url, json=payload, timeout=10)
    except: pass

def manejar_mensajes():
    global offset
    url = f"https://api.telegram.org/bot{TOKEN}/getUpdates?offset={offset}&timeout=1"
    try:
        res = requests.get(url).json()
        for update in res.get("result", []):
            offset = update["update_id"] + 1
            if "message" in update and "text" in update["message"]:
                chat_id = update["message"]["chat"]["id"]
                if update["message"]["text"] == "/start":
                    msg = f"¡Bienvenido a *{BOT_NAME}*!\n\nAnalizamos el mercado 24/7. Únete abajo:"
                    enviar_telegram(msg, chat_id, es_bienvenida=True)
    except: pass

def esta_en_horario():
    # El horario actual es 20:00 - 23:00, así que ahora está ACTIVO
    hora_actual = datetime.now().hour
    for inicio, fin in HORARIOS_ACTIVOS:
        if inicio <= hora_actual < fin: return True
    return False

def analizar_y_operar(par_trading, par_display):
    global conteo_operaciones, wins_totales, loss_totales
    handler = TA_Handler(symbol=par_trading, exchange="FX_IDC", screener="forex", interval=Interval.INTERVAL_1_MINUTE)
    try:
        analysis = handler.get_analysis()
        rsi = analysis.indicators["RSI"]
        
        # FASE 1: PRE-AVISO (RSI entre 60-67 o 33-40)
        if (60 <= rsi < 67) or (40 >= rsi > 33):
            dir_pre = "VENDER (DOWN) 🔴" if rsi > 50 else "COMPRAR (UP) 🟢"
            enviar_telegram(f"⚠️ *PRE-AVISO*\nPair: {par_display}\nAcción: *{dir_pre}*", CANAL_PRINCIPAL)
            
            # Espera 1 minuto y medio para ver si llega al punto de entrada real
            time.sleep(110)
            
            nuevo = handler.get_analysis()
            rsi_nuevo = nuevo.indicators["RSI"]
            
            # FASE 2: SEÑAL REAL (RSI rompe 64 o 36)
            if (rsi_nuevo >= 64) or (rsi_nuevo <= 36):
                direccion = "🔻 TRADE DOWN (BAJA)" if rsi_nuevo >= 50 else "⬆️ TRADE UP (SUBE)"
                precio_e = nuevo.indicators["close"]
                
                enviar_telegram(f"💎 *{BOT_NAME} - SEÑAL*\n━━━━━━━━━━━━━━━\n💱 Pair: {par_display}\n⏰ 2 Minutos\n📈 Operación: *{direccion}*", CANAL_PRINCIPAL)
                
                conteo_operaciones += 1
                time.sleep(125) # Espera los 2 minutos de la operación
                
                # FASE 3: RESULTADO
                precio_f = handler.get_analysis().indicators["close"]
                es_win = (direccion == "🔻 TRADE DOWN (BAJA)" and precio_f < precio_e) or (direccion == "⬆️ TRADE UP (SUBE)" and precio_f > precio_e)
                
                res_msg = f"✅ *RESULTADO: WIN* ✅" if es_win else f"❌ *RESULTADO: LOSS* ❌"
                if es_win: wins_totales += 1 
                else: loss_totales += 1
                
                enviar_telegram(res_msg + f"\n{par_display}", CANAL_PRINCIPAL)
                enviar_telegram(f"📑 *BITÁCORA*\n{res_msg}\n📊 Marcador: {wins_totales}W - {loss_totales}L", CANAL_RESULTADOS, con_boton=True)
    except Exception as e:
        print(f"Error en análisis: {e}")

# --- BUCLE PRINCIPAL ---
while True:
    manejar_mensajes()
    if esta_en_horario():
        if not sesion_anunciada:
            enviar_telegram(f"🔔 *SESIÓN INICIADA*\n\nAnalizando mercado... 📡", CANAL_PRINCIPAL)
            sesion_anunciada = True
            conteo_operaciones, wins_totales, loss_totales = 0, 0, 0
            
        activos = [
            {"trading":"AUDUSD","display":"AUD/USD(OTC)"}, 
            {"trading":"EURUSD","display":"EUR/USD(OTC)"}, 
            {"trading":"GBPUSD","display":"GBP/USD(OTC)"}, 
            {"trading":"USDJPY","display":"USD/JPY(OTC)"}
        ]
        
        for activo in activos:
            if conteo_operaciones < 4 and esta_en_horario():
                analizar_y_operar(activo['trading'], activo['display'])
    else:
        sesion_anunciada = False
    
    time.sleep(2) # Pausa ligera para no saturar el CPU
                
