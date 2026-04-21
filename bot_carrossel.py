import telebot
from PIL import Image, ImageDraw, ImageFont
import io
import textwrap
import google.generativeai as genai

TOKEN = "8770690142:AAGqjUAmnIiZXTp9E-pvoqq51JyefmQPe44"
GEMINI_API_KEY = "AIzaSyD8CUadzjLpd0dgS0HuoFQCGMpFn5uQw1E"

bot = telebot.TeleBot(TOKEN)
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-pro-latest')

# Fontes
try:
    FONTE_TITULO = ImageFont.truetype("arialbd.ttf", 80)
    FONTE_TEXTO = ImageFont.truetype("arial.ttf", 45)
    FONTE_PEQUENA = ImageFont.truetype("arial.ttf", 35)
except:
    FONTE_TITULO = ImageFont.load_default()
    FONTE_TEXTO = ImageFont.load_default()
    FONTE_PEQUENA = ImageFont.load_default()

def gerar_conteudo_com_ia(tema):
    prompt = f"""
    Você é um social media expert que cria carrosséis virais para Instagram e TikTok.
    Crie o roteiro de um carrossel de 5 slides sobre o tema: "{tema}"

    Regras importantes:
    1. Adapte a linguagem para o tema. Se for sério, seja profissional. Se for leve, seja descontraído.
    2. Use gatilhos de curiosidade e frases curtas. Textão não engaja.
    3. Estrutura fixa de 5 slides:
    4. Responda EXATAMENTE neste formato, sem adicionar nada antes ou depois:

    CAPA: Título Chamativo e Curto | Subtítulo: Arraste pro lado pra descobrir
    DICA1: Título do Ponto 1 | Texto de 1-2 frases explicando o ponto 1
    DICA2: Título do Ponto 2 | Texto de 1-2 frases explicando o ponto 2
    DICA3: Título do Ponto 3 | Texto de 1-2 frases explicando o ponto 3
    CTA: Chamada pra Ação | Texto final incentivando seguir, salvar ou comentar
    """

    response = model.generate_content(prompt)
    return response.text

def criar_slide(titulo, texto, cor_fundo, num_slide, total_slides):
    largura, altura = 1080, 1350
    img = Image.new('RGB', (largura, altura), color=cor_fundo)
    draw = ImageDraw.Draw(img)

    # Título
    linhas_titulo = textwrap.wrap(titulo.upper(), width=14)
    y = 160
    for linha in linhas_titulo:
        w, h = draw.textbbox((0, 0), linha, font=FONTE_TITULO)[2:]
        draw.text(((largura - w) / 2, y), linha, font=FONTE_TITULO, fill="white")
        y += h + 20

    # Texto
    linhas_texto = textwrap.wrap(texto, width=28)
    y = 700
    for linha in linhas_texto:
        w, h = draw.textbbox((0, 0), linha, font=FONTE_TEXTO)[2:]
        draw.text(((largura - w) / 2, y), linha, font=FONTE_TEXTO, fill="white")
        y += h + 15

    # Numeração e @
    draw.text((largura - 120, altura - 80), f"{num_slide}/{total_slides}", font=FONTE_PEQUENA, fill="white")
    draw.text((60, altura - 80), "@seu_insta", font=FONTE_PEQUENA, fill="white")

    bio = io.BytesIO()
    bio.name = 'image.jpeg'
    img.save(bio, 'JPEG', quality=95)
    bio.seek(0)
    return bio

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Fala! Manda o tema do seu carrossel:\n\n/criar 3 dicas para dormir melhor\n/criar como fazer bolo de chocolate\n/criar por que sua empresa precisa de tráfego pago\n\nQualquer nicho. Eu crio na hora.")

@bot.message_handler(commands=['criar'])
def criar(message):
    tema = message.text.replace('/criar ', '').strip()
    if not tema:
        bot.reply_to(message, "Manda assim: /criar seu tema aqui")
        return

    msg_espera = bot.reply_to(message, f"Criando carrossel sobre '{tema}'... 🧠✨")

    try:
        conteudo_ia = gerar_conteudo_com_ia(tema)

        slides = []
        cores = ["#1A237E", "#283593", "#303F9F", "#3949AB", "#1A237E"] # Tons de azul/roxo universal
        for linha in conteudo_ia.strip().split('\n'):
            if '|' in linha and ':' in linha:
                partes = linha.split('|', 1)
                titulo = partes[0].split(':', 1)[1].strip()
                texto = partes[1].strip()
                slides.append({"titulo": titulo, "texto": texto})

        if len(slides)!= 5:
            bot.edit_message_text("A IA se confundiu com o tema. Tenta reformular ou ser mais específico.", message.chat.id, msg_espera.message_id)
            return

        medias = []
        for i, slide in enumerate(slides):
            img_bio = criar_slide(slide["titulo"], slide["texto"], cores[i], i + 1, 5)
            medias.append(telebot.types.InputMediaPhoto(img_bio))

        bot.send_media_group(message.chat.id, medias)
        bot.edit_message_text("Carrossel pronto! 🔥 Pode postar.", message.chat.id, msg_espera.message_id)

    except Exception as e:
        bot.edit_message_text(f"Deu erro: {e}\nConfere se a chave da API do Gemini tá correta.", message.chat.id, msg_espera.message_id)

print("Bot Universal rodando...")
from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return "Bot tá online!"

def run():
  app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

keep_alive()
bot.polling()