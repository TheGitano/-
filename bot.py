import logging
import os
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
import requests
import json

# Configurar logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# TU TOKEN AQUÍ
BOT_TOKEN = "8287248635:AAHVABfsWcqh7t6BuF0oc3DGjd3gF7GAmMQ"

# Banner
BANNER = """
╔══════════════════════════════════════╗
║                                      ║
║  🚨 EL GITANO ESTÁ CON USTEDES 🚨   ║
║                                      ║
║       🔍 RASTREAR ICE 🔍             ║
║                                      ║
╚══════════════════════════════════════╝

⏳ No olvidamos, no perdonamos
🛡️ Esperamos... Somos legión
"""

MENSAJE_FINAL = """
╔═══════════════════════════════════════════╗
║                                           ║
║  ✨ ESTA HERRAMIENTA FUE DISEÑADA ✨      ║
║     PARA PROTEGER A LAS FAMILIAS          ║
║        MÁS VULNERABLES 🛡️                 ║
║                                           ║
╚═══════════════════════════════════════════╝

📢 *COMPÁRTELO CON:*
👨‍👩‍👧 Tu familia
⛪ Tu iglesia  
🏘️ Tu comunidad
👥 Grupos de vecinos
🏛️ Organizaciones locales

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✝️ *Jehová está con aquellos que*
   *protegen a los vulnerables*

📖 _"El que oprime al pobre afrenta_
   _a su Hacedor, mas el que tiene_
   _misericordia del pobre, lo honra."_
   
   *- Proverbios 14:31 -*

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

def crear_menu_principal():
    keyboard = [
        [InlineKeyboardButton("🔍 BUSCAR ACTIVIDAD ICE AHORA", callback_data='buscar_directo')],
        [InlineKeyboardButton("⚖️ CONOCER MIS DERECHOS", callback_data='menu_derechos')],
        [InlineKeyboardButton("📚 RECURSOS Y AYUDA", callback_data='menu_recursos')],
        [InlineKeyboardButton("📢 COMPARTIR BOT", callback_data='menu_compartir')],
    ]
    return InlineKeyboardMarkup(keyboard)

def crear_boton_volver():
    keyboard = [[InlineKeyboardButton("🔙 Volver al menú principal", callback_data='volver_menu')]]
    return InlineKeyboardMarkup(keyboard)

# Función para buscar actividad REAL usando web search
async def buscar_actividad_real(direccion):
    """Busca actividad REAL de ICE usando búsqueda web"""
    try:
        # Usar la API de Claude con web search
        response = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "Content-Type": "application/json",
                "anthropic-version": "2023-06-01"
            },
            json={
                "model": "claude-sonnet-4-20250514",
                "max_tokens": 2000,
                "messages": [{
                    "role": "user",
                    "content": f"""Busca AHORA MISMO información ACTUALIZADA sobre actividad de ICE cerca de: {direccion}

Busca en iceout.org, deportationtracker.live, redes sociales, noticias locales, reportes comunitarios.

Responde SOLO en formato JSON (sin markdown, sin texto adicional):
{{
    "hay_actividad": true/false,
    "nivel_riesgo": "SEGURO/PRECAUCIÓN/PELIGRO",
    "puede_salir": "SI/NO/CON_CUIDADO",
    "ultimo_reporte": "descripción detallada del último reporte o 'Sin actividad reportada en las últimas 48 horas'",
    "ubicacion_exacta": "dirección/intersección exacta donde se reportó actividad o 'N/A'",
    "distancia_cuadras": "número de cuadras de distancia o 'N/A'",
    "hora_reporte": "hora exacta del reporte o 'N/A'",
    "tipo_operativo": "checkpoint/redada/patrulla/detención o 'N/A'",
    "arrestos": "SÍ/NO/DESCONOCIDO",
    "num_arrestos": "número de personas arrestadas o 'N/A'",
    "vehiculos": "descripción de vehículos ICE vistos o 'N/A'",
    "recomendacion": "consejo específico de seguridad en 1-2 líneas",
    "fuente": "de dónde sacaste la información"
}}"""
                }],
                "tools": [{"type": "web_search_20250305", "name": "web_search"}]
            },
            timeout=45
        )
        
        if response.status_code == 200:
            data = response.json()
            content = data.get('content', [])
            
            # Buscar el texto en la respuesta
            texto_respuesta = ""
            for item in content:
                if item.get('type') == 'text':
                    texto_respuesta = item['text']
                    break
            
            # Limpiar y parsear JSON
            texto_limpio = texto_respuesta.strip()
            if texto_limpio.startswith('```json'):
                texto_limpio = texto_limpio[7:]
            if texto_limpio.startswith('```'):
                texto_limpio = texto_limpio[3:]
            if texto_limpio.endswith('```'):
                texto_limpio = texto_limpio[:-3]
            
            resultado = json.loads(texto_limpio.strip())
            return resultado
        
        # Si falla la API, retornar valores por defecto
        return crear_respuesta_default()
    
    except Exception as e:
        logger.error(f"Error buscando actividad: {e}")
        return crear_respuesta_default()

def crear_respuesta_default():
    return {
        "hay_actividad": False,
        "nivel_riesgo": "PRECAUCIÓN",
        "puede_salir": "CON_CUIDADO",
        "ultimo_reporte": "No se pudo verificar información en tiempo real. Por seguridad, consulta iceout.org directamente.",
        "ubicacion_exacta": "N/A",
        "distancia_cuadras": "N/A",
        "hora_reporte": "N/A",
        "tipo_operativo": "N/A",
        "arrestos": "DESCONOCIDO",
        "num_arrestos": "N/A",
        "vehiculos": "N/A",
        "recomendacion": "Mantente alerta. Verifica iceout.org y deportationtracker.live antes de salir.",
        "fuente": "Sistema de respaldo"
    }

# Comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mensaje_bienvenida = f"""
{BANNER}

🛡️ *Bienvenido a la red de protección*

Protegiendo a las familias más vulnerables.

💪 *¿Qué necesitas?*

Selecciona una opción:
    """
    
    if update.callback_query:
        await update.callback_query.message.edit_text(
            mensaje_bienvenida,
            parse_mode='Markdown',
            reply_markup=crear_menu_principal()
        )
    else:
        await update.message.reply_text(
            mensaje_bienvenida,
            parse_mode='Markdown',
            reply_markup=crear_menu_principal()
        )

# Manejador de botones
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == 'volver_menu':
        await start(update, context)
    
    elif query.data == 'buscar_directo':
        context.user_data['esperando_direccion'] = True
        mensaje = """
🎯 *BÚSQUEDA PRECISA DE ACTIVIDAD ICE*

Para darte información EXACTA, necesito tu ubicación.

📍 *Escribe UNA de estas opciones:*

1️⃣ *Dirección completa:*
   `1234 Main Street, Los Angeles, CA`

2️⃣ *Calles que cruzan:*
   `5th Ave y Broadway, New York`

3️⃣ *Zona o barrio:*
   `Downtown Miami, FL`

⚠️ *Mientras más preciso, mejor te puedo proteger.*

✍️ Escribe tu ubicación ahora:
        """
        await query.message.edit_text(
            mensaje,
            parse_mode='Markdown',
            reply_markup=crear_boton_volver()
        )
    
    elif query.data == 'menu_derechos':
        await mostrar_derechos(query.message)
    
    elif query.data == 'menu_recursos':
        await mostrar_recursos(query.message)
    
    elif query.data == 'menu_compartir':
        await mostrar_compartir(query.message)

# Mostrar información con datos REALES
async def mostrar_info_detallada(message, direccion):
    fecha_actual = datetime.now().strftime("%d de %B, %Y - %H:%M")
    
    # Mensaje de búsqueda
    await message.edit_text(
        f"🔍 *BUSCANDO EN TIEMPO REAL*\n\n"
        f"📍 {direccion}\n\n"
        f"⏳ Consultando:\n"
        f"• iceout.org\n"
        f"• deportationtracker.live\n"
        f"• Reportes comunitarios\n"
        f"• Noticias locales\n\n"
        f"_Esto puede tomar 15-20 segundos..._",
        parse_mode='Markdown'
    )
    
    # Buscar actividad REAL
    info = await buscar_actividad_real(direccion)
    
    # Determinar emojis y mensajes
    if info['nivel_riesgo'] == "SEGURO":
        emoji_riesgo = "🟢"
        mensaje_riesgo = "*ZONA SEGURA*"
    elif info['nivel_riesgo'] == "PRECAUCIÓN":
        emoji_riesgo = "🟡"
        mensaje_riesgo = "*PRECAUCIÓN MODERADA*"
    else:
        emoji_riesgo = "🔴"
        mensaje_riesgo = "*ZONA DE ALTO RIESGO*"
    
    if info['puede_salir'] == "SI":
        mensaje_seguridad = "✅ *PUEDES SALIR TRANQUILO*"
    elif info['puede_salir'] == "NO":
        mensaje_seguridad = "🚨 *NO SALGAS AHORA - PELIGRO*"
    else:
        mensaje_seguridad = "⚠️ *SAL CON MÁXIMA PRECAUCIÓN*"
    
    # Mensaje de arrestos
    if info['arrestos'] == "SÍ":
        emoji_arrestos = "🚨"
        texto_arrestos = f"*SÍ - {info['num_arrestos']} personas*"
    elif info['arrestos'] == "NO":
        emoji_arrestos = "✅"
        texto_arrestos = "*NO se reportaron arrestos*"
    else:
        emoji_arrestos = "❓"
        texto_arrestos = "*Información no confirmada*"
    
    resultado = f"""
╔═══════════════════════════════════════╗
║   🔍 ANÁLISIS EN TIEMPO REAL 🔍      ║
╚═══════════════════════════════════════╝

📍 *Tu ubicación:*
{direccion}

📅 *Consultado:* {fecha_actual}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{emoji_riesgo} *NIVEL DE RIESGO:* {mensaje_riesgo}

{mensaje_seguridad}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 *ÚLTIMO REPORTE:*
{info['ultimo_reporte']}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📍 *Ubicación del operativo:*
{info['ubicacion_exacta']}

📏 *Distancia de ti:* {info['distancia_cuadras']}

🕐 *Hora del reporte:* {info['hora_reporte']}

🚔 *Tipo de operativo:* {info['tipo_operativo']}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{emoji_arrestos} *ARRESTOS:* {texto_arrestos}

🚗 *Vehículos identificados:*
{info['vehiculos']}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 *RECOMENDACIÓN URGENTE:*
{info['recomendacion']}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📱 *RECURSOS INMEDIATOS:*

🗺️ *Mapa en vivo:* iceout.org/es
📞 *Emergencia:* 1-844-363-1423
⚠️ *Reportar:* iceout.org

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ℹ️ *Fuente:* {info['fuente']}

{MENSAJE_FINAL}
    """
    
    await message.edit_text(resultado, parse_mode='Markdown', reply_markup=crear_boton_volver())

# Mostrar derechos
async def mostrar_derechos(message):
    mensaje_derechos = f"""
╔═══════════════════════════════════════╗
║      ⚖️ CONOCE TUS DERECHOS ⚖️       ║
╚═══════════════════════════════════════╝

*🚨 SI TE PARA ICE EN LA CALLE:*

✅ Derecho a permanecer en silencio
✅ No estás obligado a responder
✅ Puedes grabar la interacción
✅ Pregunta: "¿Soy libre de irme?"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

*🚪 SI LLEGAN A TU CASA:*

🔒 NO abras sin orden judicial
📄 Pide ver la orden por debajo
⚠️ La orden DEBE estar firmada por un juez
❌ NO firmes nada sin abogado

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

*👮 SI TE DETIENEN:*

🔇 Mantén silencio, no resistas
📞 Pide hablar con un abogado
👨‍👩‍👧 Pregunta por tus hijos
📝 Memoriza contactos importantes

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

*📞 NÚMEROS DE EMERGENCIA:*

United We Dream: 1-844-363-1423

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💙 *Estos derechos son para TODOS*

{MENSAJE_FINAL}
    """
    await message.edit_text(mensaje_derechos, parse_mode='Markdown', reply_markup=crear_boton_volver())

# Mostrar recursos
async def mostrar_recursos(message):
    mensaje_recursos = f"""
╔═══════════════════════════════════════╗
║     📚 RECURSOS Y AYUDA 📚           ║
╚═══════════════════════════════════════╝

*🗺️ MAPAS DE RASTREO EN VIVO:*

- iceout.org/es
- deportationtracker.live

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

*📞 LÍNEAS DE AYUDA 24/7:*

- United We Dream: 1-844-363-1423
- RAICES (Texas)
- CHIRLA (California)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

*📱 APPS ÚTILES:*

- Notifica: Para familias
- Cell 411: Alertas comunitarias

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

*🏛️ ORGANIZACIONES:*

- ACLU - Derechos civiles
- NILC - Centro de leyes
- Immigrant Defense Project

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{MENSAJE_FINAL}
    """
    await message.edit_text(mensaje_recursos, parse_mode='Markdown', reply_markup=crear_boton_volver())

# Mostrar compartir
async def mostrar_compartir(message):
    bot_username = message.bot.username if hasattr(message.bot, 'username') else "tu_bot"
    mensaje = f"""
╔═══════════════════════════════════════╗
║      📢 COMPARTE ESTE BOT 📢         ║
╚═══════════════════════════════════════╝

🤖 *Bot:* @{bot_username}

📋 *Copia y envía:*

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🚨 *PROTEGE A TU COMUNIDAD* 🚨

Bot de rastreo ICE en tiempo real:
@{bot_username}

✅ Ubicaciones exactas
✅ Reportes al instante
✅ Información de arrestos
✅ Mapas en vivo

🛡️ Compártelo AHORA

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{MENSAJE_FINAL}
    """
    await message.edit_text(mensaje, parse_mode='Markdown', reply_markup=crear_boton_volver())

# Manejador de mensajes de texto
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get('esperando_direccion'):
        context.user_data['esperando_direccion'] = False
        direccion = update.message.text
        
        # Crear mensaje temporal
        temp_msg = await update.message.reply_text(
            "🔍 Iniciando búsqueda...",
            parse_mode='Markdown'
        )
        
        await mostrar_info_detallada(temp_msg, direccion)
        return
    
    mensaje = update.message.text.lower()
    
    if any(palabra in mensaje for palabra in ['ice', 'redada', 'operativo', 'migra', 'checkpoint', 'arresto']):
        await update.message.reply_text(
            "⚠️ *ALERTA DETECTADA*\n\n"
            "¿Necesitas información urgente?\n\n"
            "Usa el botón para buscar:",
            parse_mode='Markdown',
            reply_markup=crear_menu_principal()
        )
    else:
        await update.message.reply_text(
            f"{BANNER}\n\nSelecciona una opción:",
            parse_mode='Markdown',
            reply_markup=crear_menu_principal()
        )

# Función principal
def main():
    if BOT_TOKEN == "PEGA_TU_TOKEN_AQUI":
        print("❌ ERROR: Debes pegar tu token.")
        return
    
    application = Application.builder().token(BOT_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("╔══════════════════════════════════════╗")
    print("║  ✅ BOT ACTIVADO - MODO AVANZADO ✅  ║")
    print("║  🚨 EL GITANO ESTÁ CON USTEDES 🚨   ║")
    print("║  🔍 RASTREO EN TIEMPO REAL 🔍       ║")
    print("╚══════════════════════════════════════╝")
    print("\n💙 Protección activada 24/7...")
    print("🌐 Buscando en toda la red...")
    print("⚠️ Ctrl+C para detener\n")
    
    application.run_polling()

if __name__ == '__main__':
    main()

