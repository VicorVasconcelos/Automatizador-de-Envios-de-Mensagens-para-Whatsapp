from PIL import Image

try:
    with Image.open("logo.ico") as img:
        print(f"Ícone OK! Tamanhos disponíveis: {img.info.get('sizes', 'N/A')}")
except Exception as e:
    print(f"Erro: {e}")
