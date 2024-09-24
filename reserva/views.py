from django.shortcuts import render
from django.contrib import messages

def home(request):
    output = ""
    
    if request.method == 'POST':
        # Usamos el método 'get' para evitar errores si la clave no existe
        codigo = request.POST.get('codigo', '')
        clave = request.POST.get('clave', '')
        
        if codigo and clave:
            try:
                # Ejecutar el código Python (esto es solo un ejemplo, exec() es peligroso)
                local_vars = {}
                exec(codigo, {}, local_vars)
                output = f"Resultado: {local_vars}"
            except Exception as e:
                output = f"Error al ejecutar el código: {str(e)}"
        else:
            output = "Por favor, introduce el código y la clave."

        ejecutarCodigo(request, codigo, clave)
    # Renderizar la página con el resultado
    return render(request, 'index.html', {'output': output})

def ejecutarCodigo(request, codigo, clave):
    messages.success(request, str(codigo))
    print(codigo, clave)


