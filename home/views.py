from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_protect
import matplotlib.pyplot as plt
import numpy as np
import io
import base64
from sympy import sympify, lambdify, Symbol, diff

x = Symbol('x')  # variable simbólica global

# Métodos numéricos
def biseccion(f, a, b, tol, niter):
    resultados = []
    if f(a) * f(b) > 0:
        return ["No hay cambio de signo en el intervalo."]
    for i in range(niter):
        c = (a + b) / 2
        resultados.append(f"Iteración {i+1}: c = {c}, f(c) = {f(c)}")
        if abs(f(c)) < tol or (b - a) / 2 < tol:
            break
        if f(a) * f(c) < 0:
            b = c
        else:
            a = c
    return resultados

def newton(f, df, x0, tol, niter):
    resultados = []
    for i in range(niter):
        fx = f(x0)
        dfx = df(x0)
        if dfx == 0:
            return ["Derivada cero. No se puede continuar."]
        x1 = x0 - fx / dfx
        resultados.append(f"Iteración {i+1}: x = {x1}, f(x) = {f(x1)}")
        if abs(x1 - x0) < tol:
            break
        x0 = x1
    return resultados

def newton_modificado(f, df, x0, tol, niter):
    resultados = []
    dfx0 = df(x0)
    for i in range(niter):
        fx = f(x0)
        if dfx0 == 0:
            return ["Derivada cero. No se puede continuar."]
        x1 = x0 - fx / dfx0
        resultados.append(f"Iteración {i+1}: x = {x1}, f(x) = {f(x1)}")
        if abs(x1 - x0) < tol:
            break
        x0 = x1
    return resultados

# Función para graficar
def generar_grafico(f, x_min, x_max):
    x_vals = np.linspace(x_min, x_max, 400)
    y_vals = [f(val) for val in x_vals]

    plt.figure(figsize=(6, 4))
    plt.axhline(0, color='black', linewidth=1)
    plt.plot(x_vals, y_vals, label="f(x)")
    plt.title("Gráfico de la función")
    plt.xlabel("x")
    plt.ylabel("f(x)")
    plt.grid(True)
    plt.legend()

    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    plt.close()
    buffer.seek(0)
    img_base64 = base64.b64encode(buffer.read()).decode('utf-8')
    return img_base64

# Vista principal
@csrf_protect
def index(request):
    historial = request.session.get("historial", [])

    if request.method == "POST":
        if "limpiar_historial" in request.POST:
            request.session["historial"] = []
            return redirect("index")

        funcion_str = request.POST.get("funcion")
        metodo = request.POST.get("metodo")
        tol = float(request.POST.get("tol"))
        niter = int(request.POST.get("niter"))
        x_min = float(request.POST.get("x_min"))
        x_max = float(request.POST.get("x_max"))

        try:
            f_expr = sympify(funcion_str)
            f = lambdify(x, f_expr, 'numpy')
            df = lambdify(x, diff(f_expr, x), 'numpy')
        except:
            return render(request, "home/index.html", {
                "resultados": "Error al interpretar la función.",
                "historial": historial,
            })

        resultados = []

        if metodo == "biseccion":
            a = float(request.POST.get("a"))
            b = float(request.POST.get("b"))
            resultados = biseccion(f, a, b, tol, niter)
        elif metodo == "newton":
            x0 = float(request.POST.get("x0"))
            resultados = newton(f, df, x0, tol, niter)
        elif metodo == "newton_modificado":
            x0 = float(request.POST.get("x0"))
            resultados = newton_modificado(f, df, x0, tol, niter)

        # Guardar en historial
        historial.append({
            "funcion": funcion_str,
            "metodo": metodo,
            "tolerancia": tol,
            "niter": niter
        })
        request.session["historial"] = historial

        # Generar gráfica
        try:
            grafico_base64 = generar_grafico(f, x_min, x_max)
        except:
            grafico_base64 = None

        return render(request, "home/index.html", {
            "resultados": "<br>".join(resultados),
            "grafico_base64": grafico_base64,
            "historial": historial,
            "funcion": funcion_str,
            "metodo": metodo,
            "a": request.POST.get("a"),
            "b": request.POST.get("b"),
            "x0": request.POST.get("x0"),
            "tol": tol,
            "niter": niter,
            "x_min": x_min,
            "x_max": x_max,
        })

    return render(request, "home/index.html", {
        "historial": historial,
    })
