import time
import requests
from datetime import datetime, timedelta
import pytz 

# --- CONFIGURACIÓN ---
TOKEN = "8386038643:AAEngPQbBuu41WBWm7pCYQxm3yEowoJzYaw"
ID_PERSONAL = "6717348273"
BOT_NAME = "Lógica Trading 📊"

MI_ZONA_HORARIA = pytz.timezone('America/Caracas') 

# Variables de control
conteo_alertas = 0
LIMITE_ALERTAS = 4
TIEMPO_DESCANSO_HORA = 3600 # 1 hora en segundos

def enviar_telegram(mensaje, destino):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": destino, "text": mensaje, "parse_mode": "Markdown"}
    try: requests.post(url, json=payload, timeout=10)
    except: pass

def obtener_analisis_pro(par_trading):
    # Usamos la API de TradingView para obtener RSI y recomendación
    from tradingview_ta import TA_Handler, Interval
    handler = TA_Handler(symbol=par_trading, exchange="FX_IDC", screener="forex", interval=Interval.INTERVAL_1_MINUTE)
    try:
        analysis = handler.get_analysis()
        return {
            "rsi": analysis.indicators["RSI"],
            "precio": analysis.indicators["close"],
            "rec": analysis.summary["RECOMMENDATION"]
        }
    except: return None

# --- BUCLE DE TRABAJO ---
print(f"🚀 {BOT_NAME} - Modo Asistente con Descanso Iniciado")

while True:
    ahora = datetime.now(MI_ZONA_HORARIA)
    
    if conteo_alertas < LIMITE_ALERTAS:
        # LISTA DE ACTIVOS
        activos = [
            {"trading": "EURUSD", "display": "EUR/USD"},
            {"trading": "GBPUSD", "display": "GBP/USD"},
            {"trading": "USDJPY", "display": "USD/JPY"},
            {"trading": "AUDUSD", "display": "AUD/USD"}
        ]
        
        for activo in activos:
            datos = obtener_analisis_pro(activo['trading'])
            
            if datos:
                rsi = datos['rsi']
                # Filtro de señales
                es_venta = rsi >= 60
                es_compra = rsi <= 40
                
                if es_venta or es_compra:
                    conteo_alertas += 1
                    accion = "VENTA (BAJA) 🔴" if es_venta else "COMPRA (SUBE) 🟢"
                    
                    # Mensaje privado para LogicaDeApuesta
                    msg = (f"🎯 **ALERTA #{conteo_alertas} / {LIMITE_ALERTAS}**\n"
                           f"──────────────────\n"
                           f"💹 Par: **{activo['display']}**\n"
                           f"⚡ Acción: **{accion}**\n"
                           f"💰 Precio: {datos['precio']:.5f}\n"
                           f"──────────────────\n"
                           f"📢 *Reenvía al VIP si la ves clara.*")
                    
                    enviar_telegram(msg, ID_PERSONAL)
                    
                    # Pausa de 2 minutos antes de buscar la siguiente (como pediste)
                    print(f"Esperando 2 minutos para la próxima...")
                    time.sleep(120) 
                    
                    if conteo_alertas >= LIMITE_ALERTAS:
                        break
            time.sleep(2) # Pausa mínima entre escaneo de activos
            
    else:
        # MODO DESCANSO 1 HORA
        proxima_sesion = (datetime.now(MI_ZONA_HORARIA) + timedelta(hours=1)).strftime('%I:%M %p')
        aviso_descanso = (f"😴 **MODO DESCANSO ACTIVADO**\n"
                          f"──────────────────\n"
                          f"Ya envié las {LIMITE_ALERTAS} alertas.\n"
                          f"Estaré inactivo por 1 hora.\n"
                          f"🔄 Regreso a las: **{proxima_sesion}**")
        
        enviar_telegram(aviso_descanso, ID_PERSONAL)
        print("Descansando 1 hora...")
        time.sleep(TIEMPO_DESCANSO_HORA)
        
        # Reiniciar contador después de la hora
        conteo_alertas = 0
        enviar_telegram(f"⚡ **¡DESCANSO TERMINADO!**\nListo para buscar {LIMITE_ALERTAS} alertas más.", ID_PERSONAL)
