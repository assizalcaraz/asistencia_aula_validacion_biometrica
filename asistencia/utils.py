from django.shortcuts import render

def mostrar_error(request, titulo="Error", mensaje="Ocurrió un problema inesperado."):
    return render(request, "error.html", {
        "titulo": titulo,
        "mensaje": mensaje
    })
