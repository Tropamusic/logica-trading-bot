import time
import requests
from tradingview_ta import TA_Handler, Interval
from datetime import datetime

# --- CONFIGURACIÓN ---
TOKEN = "8386038643:AAEngPQbBuu41WBWm7pCYQxm3yEowoJzYaw"
CANAL_PRINCIPAL = "6717348273"
CANAL_RESULTADOS = "-1003621701961"
LINK_CANAL_PRINCIPAL = "https://t.me/+h_f-r3K_qJxlNjh h" # Tu enlace
BOT_NAME = "Lógica Trading 📊"

HORARIOS_ACTIVOS = [(8, 11), (14, 17), (20, 23)]

conteo_operaciones = 0
wins_totales, loss_totales = 0, 0
sesion_anunciada = False 

def enviar_telegram(mensaje, canal_id, con_boton=False):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": canal_id,
        "text": mensaje,
        "parse_mode": "Markdown"
    }
    if con_boton:
        payload["reply_markup"] = {
            "inline_keyboard": [[
                {"text": "📥 ¡OBTENER SEÑALES AQUÍ!", "url": LINK_CANAL_PRINCIPAL}
            ]]
        }
    try: requests.post(url, json=payload, timeout=10)
    except: pass

def esta_en_horario():
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
        
        if (60 <= rsi < 67) or (40 >= rsi > 33):
            dir_pre = "VENDER (DOWN) 🔴" if rsi > 50 else "COMPRAR (UP) 🟢"
            enviar_telegram(f"⚠️ *LÓGICA TRADING: PRE-AVISO*\nPair: {par_display}\nAcción: *{dir_pre}*\nPrepárate...", CANAL_PRINCIPAL)
            
            time.sleep(110)
            
            nuevo_analisis = handler.get_analysis()
            nuevo_rsi = nuevo_analisis.indicators["RSI"]
            
            if (nuevo_rsi >= 64) or (nuevo_rsi <= 36):
                direccion = "🔻 TRADE DOWN (BAJA)" if nuevo_rsi >= 50 else "⬆️ TRADE UP (SUBE)"
                precio_entrada = nuevo_analisis.indicators["close"]
                
                enviar_telegram(f"💎 *{BOT_NAME} - SEÑAL VIP*\n━━━━━━━━━━━━━━━\n💱 Pair: {par_display}\n⏰ Tiempo: 2 Minutos\n📈 Operación: *{direccion}*\n━━━━━━━━━━━━━━━", CANAL_PRINCIPAL)
                conteo_operaciones += 1
                
                time.sleep(125)
                
                precio_final = handler.get_analysis().indicators["close"]
                es_win = (direccion == "🔻 TRADE DOWN (BAJA)" and precio_final < precio_entrada) or \
                         (direccion == "⬆️ TRADE UP (SUBE)" and precio_final > precio_entrada)
                
                res_msg = f"✅ *RESULTADO: WIN* ✅\n{par_display} - Operación Exitosa" if es_win else f"❌ *RESULTADO: LOSS* ❌\n{par_display} - Análisis fallido"
                if es_win: wins_totales += 1 
                else: loss_totales += 1
                
                enviar_telegram(res_msg, CANAL_PRINCIPAL)
                # Enviar a bitácora con el botón de invitación
                enviar_telegram(f"📑 *BITÁCORA DE OPERACIÓN*\n\n{res_msg}\n📊 Marcador: {wins_totales}W - {loss_totales}L", CANAL_RESULTADOS, con_boton=True)
                
                time.sleep(20)
    except: pass

while True:
    if esta_en_horario():
        if not sesion_anunciada:
            enviar_telegram(f"🔔 *ATENCIÓN TRADERS*\n\nLa sesión de {BOT_NAME} ha comenzado.\nAnalizando mercado en tiempo real... 📡", CANAL_PRINCIPAL)
            sesion_anunciada = True
            conteo_operaciones, wins_totales, loss_totales = 0, 0, 0
        
        activos = [{"trading":"AUDUSD","display":"AUD/USD(OTC)"}, {"trading":"EURUSD","display":"EUR/USD(OTC)"}, {"trading":"GBPUSD","display":"GBP/USD(OTC)"}, {"trading":"USDJPY","display":"USD/JPY(OTC)"}]
        for activo in activos:
            if conteo_operaciones < 4 and esta_en_horario():
                analizar_y_operar(activo['trading'], activo['display'])
    else:
        sesion_anunciada = False
        time.sleep(60)
        
