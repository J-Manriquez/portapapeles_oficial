# utils.py

import time

def measure_time(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(f"{func.__name__} tomó {(end_time - start_time) * 1000:.2f} ms")
        return result
    return wrapper

def process_text(text_data, cant_lineas):
    """
    Procesa el texto para mostrarlo de forma limpia y ordenada
    """
    # Comprueba si text_data es un diccionario y extrae el texto
    if isinstance(text_data, dict):
        text = text_data.get('text', '')
    else:
        text = str(text_data)

    # Eliminamos espacios extras y tabulaciones al inicio y final
    text = text.strip()
    
    # Dividimos el texto en líneas
    lines = text.splitlines()
    
    # Eliminamos líneas vacías consecutivas y espacios extras
    clean_lines = []
    prev_empty = False
    for line in lines:
        line = line.strip()
        
        # Si la línea está vacía
        if not line:
            if not prev_empty:  # Solo mantenemos una línea vacía
                clean_lines.append('')
                prev_empty = True
        else:
            clean_lines.append(line)
            prev_empty = False
    
    # Tomamos solo las primeras 'cant_lineas' para la vista previa
    preview_lines = clean_lines[:cant_lineas]
    
    # Si hay más líneas, indicamos cuántas más hay
    if len(clean_lines) > cant_lineas:
        remaining_lines = len(clean_lines) - cant_lineas
        preview_lines.append(f"+ {remaining_lines} líneas más")
        
    # Unimos las líneas con saltos de línea
    return '\n'.join(preview_lines)