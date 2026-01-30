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
        [InlineKeyboardButton("🚨 BUSCAR ACTIVIDAD ICE AHORA", callback_data='buscar_directo')],
        [InlineKeyboardButton("⚖️ MIS DERECHOS", callback_data='menu_derechos')],
        [InlineKeyboardButton("📚 RECURSOS", callback_data='menu_recursos')],
        [InlineKeyboardButton("📢 COMPARTIR", callback_data='menu_compartir')],
    ]
    return InlineKeyboardMarkup(keyboard)

def crear_boton_volver():
    keyboard = [[InlineKeyboardButton("🔙 Volver", callback_data='volver_menu')]]
    return InlineKeyboardMarkup(keyboard)

# Función POTENTE de búsqueda real
async def buscar_actividad_real_completa(direccion):
    """Busca TODO sobre ICE en la zona usando web search real"""
    try:
        response = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "Content-Type": "application/json",
                "anthropic-version": "2023-06-01"
            },
            json={
                "model": "claude-sonnet-4-20250514",
                "max_tokens": 3000,
                "messages": [{
                    "role": "user",
                    "content": f"""BÚSQUEDA URGENTE DE ACTIVIDAD ICE CERCA DE: {direccion}

Busca AHORA MISMO en iceout.org, deportationtracker.live, noticias locales, redes sociales, reportes comunitarios.

Responde en formato JSON (sin markdown):
{{
    "nivel_riesgo": "SEGURO/PRECAUCIÓN/PELIGRO_ALTO",
    "puede_salir_ahora": "SI/NO/ESPERA",
    "resumen_urgente": "descripción breve de la situación en 1-2 líneas",
    "ultimo_reporte_cercano": "descripción detallada del reporte más cercano o 'No hay reportes recientes en esta zona específica'",
    "ubicacion_operativo": "dirección exacta del operativo más cercano o 'N/A'",
    "distancia_estimada": "distancia en cuadras/millas o 'N/A'",
    "hora_ultimo_reporte": "hora del último reporte o 'N/A'",
    "tipo_operativo": "redada/checkpoint/patrulla/detención en hogar/otro o 'N/A'",
    "arrestos_confirmados": "SI/NO/DESCONOCIDO",
    "num_arrestos": "número de arrestos o 'N/A'",
    "detalles_arrestos": "detalles de los arrestos si hay o 'N/A'",
    "vehiculos_descripcion": "descripción de vehículos ICE o 'N/A'",
    "agentes_descripcion": "descripción de agentes o 'N/A'",
    "recomendacion_inmediata": "qué debe hacer la persona AHORA en 2 líneas",
    "noticias": [
        {{"titulo": "título de la noticia", "url": "URL completa", "fuente": "medio"}},
        {{"titulo": "título 2", "url": "URL 2", "fuente": "medio 2"}}
    ],
    "videos": [
        {{"titulo": "título del video", "url": "URL completa", "plataforma": "YouTube/Twitter/etc"}}
    ],
    "fuentes_consultadas": "lista de fuentes donde buscaste"
}}

IMPORTANTE: Incluye TODAS las noticias y videos que encuentres sobre actividad ICE en esa zona."""
                }],
                "tools": [{"type": "web_search_20250305", "name": "web_search"}]
            },
            timeout=60
        )
        
        if response.status_code == 200:
            data = response.json()
            content = data.get('content', [])
            
            texto_respuesta = ""
            for item in content:
                if item.get('type') == 'text':
                    texto_respuesta = item['text']
                    break
            
            # Limpiar JSON
            texto_limpio = texto_respuesta.strip()
            if texto_limpio.startswith('```json'):
                texto_limpio = texto_limpio[7:]
            if texto_limpio.startswith('```'):
                texto_limpio = texto_limpio[3:]
            if texto_limpio.endswith('```'):
                texto_limpio = texto_limpio[:-3]
            
            resultado = json.loads(texto_limpio.strip())
            return resultado
        
        return crear_respuesta_default()
    
    except Exception as e:
        logger.error(f"Error: {e}")
        return crear_respuesta_default()

def crear_respuesta_default():
    return {
        "nivel_riesgo": "PRECAUCIÓN",
        "puede_salir_ahora": "ESPERA",
        "resumen_urgente": "No se pudo verificar en tiempo real. Consulta iceout.org directamente.",
        "ultimo_reporte_cercano": "Sistema temporalmente no disponible",
        "ubicacion_operativo": "N/A",
        "distancia_estimada": "N/A",
        "hora_ultimo_reporte": "N/A",
        "tipo_operativo": "N/A",
        "arrestos_confirmados": "DESCONOCIDO",
        "num_arrestos": "N/A",
        "detalles_arrestos": "N/A",
        "vehiculos_descripcion": "N/A",
        "agentes_descripcion": "N/A",
        "recomendacion_inmediata": "Por precaución, verifica iceout.org/es antes de salir. Mantén tus documentos contigo.",
        "noticias": [],
        "videos": [],
        "fuentes_consultadas": "Sistema de respaldo"
    }

# Comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mensaje_bienvenida = f"""
{BANNER}

🛡️ *PROTECCIÓN INMEDIATA*

Para familias vulnerables.

💪 *¿Qué necesitas?*
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
🎯 *BÚSQUEDA INMEDIATA*

📍 *Escribe tu ubicación AHORA:*

Ejemplos:
- `5th Ave y Broadway`
- `Downtown Miami`
- `1234 Main St, LA`
- `Cerca de Mercado Central`

⚡ *Mientras más preciso, mejor*
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

# Mostrar información COMPLETA
async def mostrar_info_completa(message, direccion):
    fecha_actual = datetime.now().strftime("%d/%B/%Y %H:%M")
    
    await message.edit_text(
        f"🔍 *BUSCANDO AHORA...*\n\n"
        f"📍 {direccion}\n\n"
        f"⏳ Escaneando toda la red...\n"
        f"_15-30 segundos..._",
        parse_mode='Markdown'
    )
    
    # Buscar TODO
    info = await buscar_actividad_real_completa(direccion)
    
    # Determinar urgencia
    if info['nivel_riesgo'] == "SEGURO":
        emoji = "🟢"
        estado = "*ZONA SEGURA*"
    elif info['nivel_riesgo'] == "PRECAUCIÓN":
        emoji = "🟡"
        estado = "*MANTÉN PRECAUCIÓN*"
    else:
        emoji = "🔴"
        estado = "*⚠️ PELIGRO - NO SALGAS ⚠️*"
    
    if info['puede_salir_ahora'] == "SI":
        accion = "✅ *Puedes salir*"
    elif info['puede_salir_ahora'] == "NO":
        accion = "🚨 *NO SALGAS AHORA*"
    else:
        accion = "⏸️ *ESPERA 30 min*"
    
    # Formatear noticias
    texto_noticias = ""
    if info['noticias']:
        texto_noticias = "\n\n📰 *NOTICIAS ENCONTRADAS:*\n"
        for i, noticia in enumerate(info['noticias'][:5], 1):
            texto_noticias += f"\n{i}. [{noticia['titulo']}]({noticia['url']})\n   📱 {noticia['fuente']}"
    else:
        texto_noticias = "\n\n📰 *No hay noticias recientes de esta zona*"
    
    # Formatear videos
    texto_videos = ""
    if info['videos']:
        texto_videos = "\n\n🎥 *VIDEOS ENCONTRADOS:*\n"
        for i, video in enumerate(info['videos'][:3], 1):
            texto_videos += f"\n{i}. [{video['titulo']}]({video['url']})\n   📱 {video['plataforma']}"
    else:
        texto_videos = "\n\n🎥 *No hay videos recientes*"
    
    resultado = f"""
╔═══════════════════════════════════════╗
║   🔍 INFORMACIÓN EN TIEMPO REAL 🔍   ║
╚═══════════════════════════════════════╝

📍 *{direccion}*
📅 {fecha_actual}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{emoji} *RIESGO:* {estado}
{accion}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💬 *SITUACIÓN:*
{info['resumen_urgente']}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 *ÚLTIMO REPORTE:*
{info['ultimo_reporte_cercano']}

📍 *Ubicación del operativo:*
{info['ubicacion_operativo']}

📏 *Distancia de ti:* {info['distancia_estimada']}
🕐 *Hora:* {info['hora_ultimo_reporte']}
🚔 *Tipo:* {info['tipo_operativo']}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🚨 *ARRESTOS:*
- Confirmados: {info['arrestos_confirmados']}
- Cantidad: {info['num_arrestos']}
- Detalles: {info['detalles_arrestos']}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🚗 *VEHÍCULOS:* {info['vehiculos_descripcion']}
👮 *AGENTES:* {info['agentes_descripcion']}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 *QUÉ HACER AHORA:*
{info['recomendacion_inmediata']}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{texto_noticias}
{texto_videos}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📱 *EMERGENCIA:*
- Línea 24/7: 1-844-363-1423
- Mapa: iceout.org/es

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ℹ️ *Fuentes:* {info['fuentes_consultadas']}

{MENSAJE_FINAL}
    """
    
    await message.edit_text(resultado, parse_mode='Markdown', reply_markup=crear_boton_volver(), disable_web_page_preview=False)

# Mostrar derechos
async def mostrar_derechos(message):
    mensaje_derechos = f"""
╔═══════════════════════════════════════╗
║      ⚖️ TUS DERECHOS ⚖️              ║
╚═══════════════════════════════════════╝

*🚨 EN LA CALLE:*
✅ Permanecer en silencio
✅ No responder preguntas
✅ Preguntar: "¿Soy libre de irme?"
✅ Grabar en espacios públicos

*🚪 EN TU CASA:*
🔒 NO abrir sin orden judicial firmada
📄 Pedir ver orden por debajo
❌ NO firmar nada
⚠️ Orden debe tener firma de juez

*👮 SI TE DETIENEN:*
🔇 Silencio absoluto
📞 "Quiero hablar con un abogado"
👨‍👩‍👧 Preguntar por tus hijos
📝 Memorizar contactos

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📞 *EMERGENCIA:* 1-844-363-1423

{MENSAJE_FINAL}
    """
    await message.edit_text(mensaje_derechos, parse_mode='Markdown', reply_markup=crear_boton_volver())

# Mostrar recursos
async def mostrar_recursos(message):
    mensaje_recursos = f"""
╔═══════════════════════════════════════╗
║     📚 RECURSOS 📚                    ║
╚═══════════════════════════════════════╝

*🗺️ MAPAS EN VIVO:*
- [iceout.org/es](https://iceout.org/es)
- [deportationtracker.live](https://deportationtracker.live)

*📞 LÍNEAS 24/7:*
- United We Dream: 1-844-363-1423
- RAICES (Texas)
- CHIRLA (California)

*📱 APPS:*
- Notifica
- Cell 411

*🏛️ ORGANIZACIONES:*
- ACLU
- NILC
- Immigrant Defense Project

{MENSAJE_FINAL}
    """
    await message.edit_text(mensaje_recursos, parse_mode='Markdown', reply_markup=crear_boton_volver(), disable_web_page_preview=True)

# Mostrar compartir
async def mostrar_compartir(message):
    bot_username = message.bot.username if hasattr(message.bot, 'username') else "tu_bot"
    mensaje = f"""
╔═══════════════════════════════════════╗
║      📢 COMPARTE AHORA 📢            ║
╚═══════════════════════════════════════╝

🤖 @{bot_username}

*Copia y envía:*

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🚨 PROTECCIÓN ICE - BOT GRATIS

Bot de rastreo en tiempo real:
@{bot_username}

✅ Info inmediata
✅ Noticias y videos
✅ Sin rodeos

🛡️ COMPARTE AHORA

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{MENSAJE_FINAL}
    """
    await message.edit_text(mensaje, parse_mode='Markdown', reply_markup=crear_boton_volver())

# Manejador de mensajes
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get('esperando_direccion'):
        context.user_data['esperando_direccion'] = False
        direccion = update.message.text
        
        temp_msg = await update.message.reply_text("🔍 Buscando...", parse_mode='Markdown')
        await mostrar_info_completa(temp_msg, direccion)
        return
    
    await update.message.reply_text(
        f"{BANNER}\n\n¿Qué necesitas?",
        parse_mode='Markdown',
        reply_markup=crear_menu_principal()
    )

# Función principal
def main():
    if BOT_TOKEN == "PEGA_TU_TOKEN_AQUI":
        print("❌ ERROR: Token faltante")
        return
    
    application = Application.builder().token(BOT_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("╔══════════════════════════════════════╗")
    print("║  ✅ BOT SÚPER POTENTE ACTIVO ✅     ║")
    print("║  🚨 EL GITANO PROTEGE 24/7 🚨       ║")
    print("║  🔍 BÚSQUEDA TOTAL ACTIVADA 🔍      ║")
    print("╚══════════════════════════════════════╝")
    print("\n💙 Protegiendo vidas...")
    print("🌐 Escaneando toda la red...")
    print("📰 Buscando noticias y videos...")
    print("⚠️ Ctrl+C para detener\n")
    
    application.run_polling()

if __name__ == '__main__':
    main()

