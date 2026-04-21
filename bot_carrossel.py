import os
import textwrap
from PIL import Image, ImageDraw, ImageFont
import google.generativeai as genai
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

TOKEN = os.environ.get("8770690142:AAGqjUAmnIiZXTp9E-pvoqq51JyefmQPe44")
GEMINI_API_KEY = os.environ.get("AIzaSyD8CUadzjLpd0dgS0HuoFQCGMpFn5uQw1E")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.5-flash')

PEGANDO_TEMA, PEGANDO_ARROBA = range(2)

def criar_imagem_carrossel(texto, numero_imagem, total_imagens, arroba):
    largura, altura = 1080, 1080
    cor_fundo = (15, 15, 15)
    cor_texto = (255, 255, 255)
    cor_destaque = (0, 255, 150)
    img = Image.new('RGB', (largura, altura), color=cor_fundo)
    draw = ImageDraw.Draw(img)
    try:
        fonte_titulo = ImageFont.truetype("DejaVuSans-Bold.ttf", 70)
        fonte_texto = ImageFont.truetype("DejaVuSans.ttf", 55)
        fonte_rodape = ImageFont.truetype("DejaVuSans.ttf", 35)
    except IOError:
        fonte_titulo = ImageFont.load_default()
        fonte_texto = ImageFont.load_default()
        fonte_rodape = ImageFont.load_default()

    margem = 80
    y_texto = 220

    if numero_imagem == 1:
        linhas = textwrap.wrap(texto.upper(), width=15)
        for linha in linhas:
            w, h = draw.textbbox((0,0), linha, font=fonte_titulo)[2:]
            draw.text(((largura-w)/2, y_texto), linha, font=fonte_titulo, fill=cor_destaque)
            y_texto += h + 20
    else:
        linhas = textwrap.wrap(texto, width=25)
        for linha in linhas:
            draw.text((margem, y_texto), linha, font=fonte_texto, fill=cor_texto)
            y_texto += 70

    if numero_imagem == total_imagens:
        w, h = draw.textbbox((0,0), arroba, font=fonte_rodape)[2:]
        draw.text(((largura-w)/2, altura-120), arroba, font=fonte_rodape, fill=cor_destaque)

    numeracao = f"{numero_imagem}/{total_imagens}"
    w, h = draw.textbbox((0,0), numeracao, font=fonte_rodape)[2:]
    draw.text((largura-w-margem, margem), numeracao, font=fonte_rodape, fill=cor_texto)

    nome_arquivo = f"carrossel_{numero_imagem}.png"
    img.save(nome_arquivo)
    return nome_arquivo

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Fala! Eu sou o Clover Carrossel 🤖\n\nManda /criar que eu te ajudo a fazer um carrossel completo pro Insta.")

async def iniciar_criacao(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Qual o tema do carrossel que você quer criar?")
    return PEGANDO_TEMA

async def receber_tema(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['tema'] = update.message.text
    await update.message.reply_text("Show! E qual @ você quer que apareça na última imagem?\n\nEx: @seuinstagram")
    return PEGANDO_ARROBA

async def receber_arroba_e_gerar(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    arroba = update.message.text
    tema = context.user_data['tema']
    if not arroba.startswith('@'):
        arroba = '@' + arroba
    await update.message.reply_text(f"Perfeito! Criando carrossel sobre '{tema}' para {arroba}... 🧠✨ Isso pode levar uns 20s.")
    try:
        prompt = f"""
        Crie 5 textos curtos para um carrossel do Instagram sobre: {tema}.
        Regra 1: Tom persuasivo, direto e que gera curiosidade.
        Regra 2: Cada texto tem que caber numa imagem 1080x1080. Máximo 2 frases curtas.
        Regra 3: O primeiro texto é a CAPA. Tem que ser um título forte e chamativo.
        Regra 4: O último texto é a CTA. Termine com: 'Curtiu? Me segue pra mais: {arroba}'
        Regra 5: Não use hashtags ou emojis.
        Formato: Separe cada um dos 5 textos com ---
        """
        response = model.generate_content(prompt)
        textos = [t.strip() for t in response.text.split('---') if t.strip()]
        total = len(textos)
        for i, texto in enumerate(textos, 1):
            arquivo_imagem = criar_imagem_carrossel(texto, i, total, arroba)
            await update.message.reply_photo(photo=open(arquivo_imagem, 'rb'))
            os.remove(arquivo_imagem)
        await update.message.reply_text("Pronto! Carrossel finalizado ✅\nManda /criar pra fazer outro.")
    except Exception as e:
        await update.message.reply_text(f"Deu erro ao gerar: {e}\n\nTenta de novo com /criar")
    return ConversationHandler.END

async def cancelar(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Criação cancelada. Manda /criar quando quiser recomeçar.")
    return ConversationHandler.END

def main():
    application = Application.builder().token(TOKEN).build()
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('criar', iniciar_criacao)],
        states={
            PEGANDO_TEMA: [MessageHandler(filters.TEXT & ~filters.COMMAND, receber_tema)],
            PEGANDO_ARROBA: [MessageHandler(filters.TEXT & ~filters.COMMAND, receber_arroba_e_gerar)],
        },
        fallbacks=[CommandHandler('cancelar', cancelar)],
    )
    application.add_handler(CommandHandler("start", start))
    application.add_handler(conv_handler)
    print("Bot Universal rodando...")
    application.run_polling()

if __name__ == '__main__':
    main()