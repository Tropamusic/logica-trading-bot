import time
import requests
from tradingview_ta import TA_Handler, Interval
from datetime import datetime

# --- CONFIGURACIÓN ---
TOKEN = "8386038643:AAEngPQbBuu41WBWm7pCYQxm3yEowoJzYaw"
CANAL_PRINCIPAL = "6717348273"  # Donde envías las señales
CANAL_RESULTADOS = "-1003621701961"  # Tu nuevo canal de transparencia
BOT_NAME = "Lógica Trading 📊"

HORARIOS_ACTIVOS = [
    (8, 11),   # Mañana
    (14, 17),  # Tarde
    (20, 23)   # Noche
]

conteo_operaciones = 0
wins_totales = 0  
loss_totales = 0
sesion_anunciada = False 

def enviar_telegram(mensaje, canal_id):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={canal_id}&text={mensaje}&parse_mode=Markdown"
    try: requests.get(url, timeout=10)
    except: pass

def esta_en_horario():
    hora_actual = datetime.now().hour
    for inicio, fin in HORARIOS_ACTIVOS:
        if inicio <= hora_actual < fin:
            return True
    return False

def esperar_al_minuto_cero():
    segundos_actuales = datetime.now().second
    if segundos_actuales > 0:
        time.sleep(60 - segundos_actuales)

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
            esperar_al_minuto_cero()
            
            nuevo_analisis = handler.get_analysis()
            nuevo_rsi = nuevo_analisis.indicators["RSI"]
            
            if (nuevo_rsi >= 64) or (nuevo_rsi <= 36):
                direccion = "🔻 TRADE DOWN (BAJA)" if nuevo_rsi >= 50 else "⬆️ TRADE UP (SUBE)"
                precio_entrada = nuevo_analisis.indicators["close"]
                
                msg = (f"💎 *{BOT_NAME} - SEÑAL VIP*\n"
                       f"━━━━━━━━━━━━━━━\n"
                       f"💱 Pair: {par_display}\n"
                       f"⏰ Tiempo: 2 Minutos\n"
                       f"📈 Operación: *{direccion}*\n"
                       f"━━━━━━━━━━━━━━━")
                enviar_telegram(msg, CANAL_PRINCIPAL)
                conteo_operaciones += 1
                
                time.sleep(125) # Espera el resultado (2 min)
                
                # Verificación de resultado (Simple lógica de precio)
                precio_final = handler.get_analysis().indicators["close"]
                es_win = (direccion == "🔻 TRADE DOWN (BAJA)" and precio_final < precio_entrada) or \
                         (direccion == "⬆️ TRADE UP (SUBE)" and precio_final > precio_entrada)
                
                if es_win:
                    wins_totales += 1
                    res_msg = f"✅ *RESULTADO: WIN* ✅\n{par_display} - Operación Exitosa"
                else:
                    loss_totales += 1
                    res_msg = f"❌ *RESULTADO: LOSS* ❌\n{par_display} - Análisis fallido"
                
                # Enviar resultado a ambos canales
                enviar_telegram(res_msg, CANAL_PRINCIPAL)
                enviar_telegram(f"📊 *REPORTE PÚBLICO*\n{res_msg}\nMarcador Sesión: {wins_totales}W - {loss_totales}L", CANAL_RESULTADOS)
                
                time.sleep(20)
    except: pass

print(f"🚀 {BOT_NAME} CON TRANSPARENCIA ACTIVA")

while True:
    if esta_en_horario():
        if not sesion_anunciada:
            msg_inicio = f"🔔 *ATENCIÓN TRADERS*\n\nLa sesión de {BOT_NAME} ha comenzado.\nAnalizando mercado en tiempo real... 📡"
            enviar_telegram(msg_inicio, CANAL_PRINCIPAL)
            sesion_anunciada = True
            conteo_operaciones, wins_totales, loss_totales = 0, 0, 0

        if conteo_operaciones < 4:
            activos = [
                {"trading": "AUDUSD", "display": "AUD/USD(OTC)"},
                {"trading": "EURUSD", "display": "EUR/USD(OTC)"},
                {"trading": "GBPUSD", "display": "GBP/USD(OTC)"},
                {"trading": "USDJPY", "display": "USD/JPY(OTC)"},
                {"trading": "EURGBP", "display": "EUR/GBP(OTC)"}
            ]
            for activo in activos:
                if conteo_operaciones < 4 and esta_en_horario():
                    analizar_y_operar(activo['trading'], activo['display'])
        else:
            if sesion_anunciada:
                reporte = (f"📊 *SESIÓN FINALIZADA*\n\n✅ Ganadas: {wins_totales}\n❌ Perdidas: {loss_totales}\n🎯 Efectividad: {(wins_totales/4)*100 if wins_totales>0 else 0}%\n\n¡Retira tus ganancias!")
                enviar_telegram(reporte, CANAL_PRINCIPAL)
                enviar_telegram(f"📢 *CIERRE DE SESIÓN PÚBLICO*\n{reporte}", CANAL_RESULTADOS)
                sesion_anunciada = False
                time.sleep(3600)
    else:
        sesion_anunciada = False
        time.sleep(60)
        
