import os
import time
from flask import Flask, render_template, request
from PIL import Image

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def texto_a_binario(texto):
    texto_completo = texto + "$$$" # Delimitador de fin de mensaje
    return ''.join([format(ord(char), '08b') for char in texto_completo])

def binario_a_texto(binario):
    # Ya no necesitamos cortar el delimitador aquí, lo cortaremos en binario antes
    caracteres = [chr(int(binario[i:i+8], 2)) for i in range(0, len(binario), 8) if len(binario[i:i+8]) == 8]
    return ''.join(caracteres)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/ocultar', methods=['POST'])
def ocultar():
    if 'imagen' not in request.files:
        return "No se subió ninguna imagen"
    
    archivo = request.files['imagen']
    mensaje = request.form['mensaje']
    
    # 1. Extraemos la extensión del archivo original (ej. '.png', '.bmp', '.jpg')
    nombre_base, extension = os.path.splitext(archivo.filename)
    extension = extension.lower()
    
    timestamp = int(time.time())
    nombre_original = f"original_{timestamp}{extension}"
    nombre_estego = f"secreta_{timestamp}.bmp"
    
    ruta_original = os.path.join(app.config['UPLOAD_FOLDER'], nombre_original)
    ruta_estego = os.path.join(app.config['UPLOAD_FOLDER'], nombre_estego)
    
    archivo.save(ruta_original)
    
    img = Image.open(ruta_original).convert('RGB')
    pixeles = img.load()
    ancho, alto = img.size
    
    binario = texto_a_binario(mensaje)
    idx_bit = 0
    longitud_bits = len(binario)
    
    log_detallado = []
    log_detallado.append(f"[*] INICIANDO PROCESO DE CODIFICACIÓN LSB")
    log_detallado.append(f"[*] Mensaje a ocultar: '{mensaje}'")
    log_detallado.append(f"[*] Bits a inyectar (incluye delimitador '$$$'): {longitud_bits}")
    log_detallado.append("-" * 50)
    
    pixeles_mostrados = 0
    
    for y in range(alto):
        for x in range(ancho):
            if idx_bit < longitud_bits:
                r, g, b = pixeles[x, y]
                orig_r, orig_g, orig_b = r, g, b
                
                if idx_bit < longitud_bits:
                    r = (r & 254) | int(binario[idx_bit])
                    idx_bit += 1
                if idx_bit < longitud_bits:
                    g = (g & 254) | int(binario[idx_bit])
                    idx_bit += 1
                if idx_bit < longitud_bits:
                    b = (b & 254) | int(binario[idx_bit])
                    idx_bit += 1
                    
                pixeles[x, y] = (r, g, b)
                
                if pixeles_mostrados < 5:
                    log_detallado.append(f"Píxel ({x}, {y}):")
                    log_detallado.append(f"  ORIGINAL   -> R:{format(orig_r, '08b')}  G:{format(orig_g, '08b')}  B:{format(orig_b, '08b')}")
                    log_detallado.append(f"  MODIFICADO -> R:{format(r, '08b')}  G:{format(g, '08b')}  B:{format(b, '08b')}")
                    log_detallado.append("")
                    pixeles_mostrados += 1
                elif pixeles_mostrados == 5:
                    log_detallado.append("... (Proceso repetido para los siguientes píxeles) ...")
                    pixeles_mostrados += 1
    
    # 2. Guardar la imagen estenográfica forzando siempre a formato BMP
    img.save(ruta_estego, "BMP")
    if extension not in ['.bmp']:
        log_detallado.append("-" * 50)
        log_detallado.append(f"[!] AVISO DE CONVERSIÓN: La imagen original era {extension.upper()}.")
        log_detallado.append("[!] Se convirtió automáticamente a BMP para evitar la compresión y proteger el mensaje.")
    
    return render_template('index.html', 
                           img_original=nombre_original, 
                           img_resultado=nombre_estego,
                           log_procesado='\n'.join(log_detallado))

@app.route('/revelar_directo', methods=['POST'])

def revelar_directo():
    nombre_archivo = request.form['filename']
    ruta_imagen = os.path.join(app.config['UPLOAD_FOLDER'], nombre_archivo)
    return procesar_revelado(ruta_imagen)

@app.route('/revelar', methods=['POST'])
def revelar():
    if 'imagen_secreta' not in request.files:
        return "No se subió ninguna imagen"
        
    archivo = request.files['imagen_secreta']
    ruta_temporal = os.path.join(app.config['UPLOAD_FOLDER'], 'temp_revelar.png')
    archivo.save(ruta_temporal)
    return procesar_revelado(ruta_temporal)

def procesar_revelado(ruta_imagen):
    try:
        img = Image.open(ruta_imagen).convert('RGB')
    except Exception as e:
        return render_template('index.html', error_revelar="Error al abrir la imagen.")

    pixeles = img.load()
    ancho, alto = img.size
    bits_extraidos = ""
    
    # --- LOG DEL PROCESO DE REVELADO ---
    log_revelado = []
    log_revelado.append("[*] INICIANDO PROCESO DE EXTRACCIÓN LSB")
    log_revelado.append("[*] Leyendo únicamente el último bit de cada canal de color...")
    log_revelado.append("-" * 50)
    
    pixeles_mostrados = 0
    
    for y in range(alto):
        for x in range(ancho):
            r, g, b = pixeles[x, y]
            
            # Extraemos el último bit
            bit_r = str(r & 1)
            bit_g = str(g & 1)
            bit_b = str(b & 1)
            
            bits_extraidos += bit_r + bit_g + bit_b
            
            # Mostramos visualmente de dónde salen los bits
            if pixeles_mostrados < 5:
                log_revelado.append(f"Píxel ({x}, {y}) -> Rojo:{r}(termina en {bit_r}) Verde:{g}(termina en {bit_g}) Azul:{b}(termina en {bit_b}) | Extraído: '{bit_r}{bit_g}{bit_b}'")
                pixeles_mostrados += 1
            elif pixeles_mostrados == 5:
                log_revelado.append("... (Proceso repetido para barrer toda la imagen) ...")
                pixeles_mostrados += 1
            
    # CORRECCIÓN DEL BUG: Generamos la versión binaria exacta de '$$$'
    delimitador_binario = ''.join([format(ord(c), '08b') for c in "$$$"])
    
    log_revelado.append("-" * 50)
    log_revelado.append(f"[*] Buscando secuencia del delimitador en el mar de bits: {delimitador_binario}")
    
    if delimitador_binario in bits_extraidos:
        # Cortamos todos los bits basura que haya después del delimitador
        bits_utiles = bits_extraidos.split(delimitador_binario)[0]
        log_revelado.append(f"[*] ¡Delimitador encontrado! Se recuperaron {len(bits_utiles)} bits de mensaje oculto.")
        
        log_revelado.append("\n[*] Traducción de bloques de 8 bits a caracteres:")
        # Mostramos cómo se traduce cada bloque
        bloques = [bits_utiles[i:i+8] for i in range(0, min(len(bits_utiles), 40), 8)]
        for bloque in bloques:
            if len(bloque) == 8:
                log_revelado.append(f"    {bloque} -> Letra: '{chr(int(bloque, 2))}'")
        if len(bits_utiles) > 40:
             log_revelado.append("    ...")
             
        mensaje_descifrado = binario_a_texto(bits_utiles)
        log_revelado.append(f"\n[+] Proceso finalizado. Mensaje reconstruido.")
        
        return render_template('index.html', 
                               mensaje_revelado=mensaje_descifrado,
                               log_revelado='\n'.join(log_revelado))
    else:
        return render_template('index.html', error_revelar="Error: No se encontró ningún mensaje oculto. Asegúrate de usar la imagen procesada.")


# ESTO DEBE SER LO ÚLTIMO DEL ARCHIVO
if __name__ == '__main__':
    app.run(debug=True)