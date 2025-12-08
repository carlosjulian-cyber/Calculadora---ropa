import streamlit as st
import pandas as pd
from datetime import datetime

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Calculadora Ropa Dic-25", layout="centered")

st.title("👗 Calculadora de Ventas")
st.markdown("---")

# --- LÓGICA DE COSTOS (Basada en las columnas N, O, P del Excel) ---
def obtener_costo_porcentaje(pago, articulo):
    # Normalizamos texto a mayúsculas para evitar errores
    pago = pago.upper()
    articulo = articulo.upper()
    
    # Lógica extraída de tu Excel (Filas 12 en adelante)
    
    # CHARLIE tiene costos más altos
    if pago == "CHARLIE":
        if "PROMO" in articulo:
            return 0.46
        elif "MAYOR" in articulo:
            return 0.60
        else: # Vestido o Tejido normal
            return 0.40
            
    # RITA, TOMI, MERY suelen tener el mismo costo base
    elif pago in ["RITA", "TOMI", "MERY"]:
        if "PROMO" in articulo:
            return 0.41
        elif "MAYOR" in articulo:
            return 0.35
        elif "SOL" in articulo: # Visto en fila 27
            return 0.30
        else: # Vestido o Tejido normal
            return 0.20
            
    # Por defecto si no encuentra coincidencia (Seguridad)
    return 0.20

# --- ENTRADA DE DATOS (INPUTS) ---
st.sidebar.header("📝 Cargar Nueva Venta")

# Fecha Automática
fecha_actual = datetime.now()
dia_auto = fecha_actual.day
mes_auto = fecha_actual.month
anio_auto = fecha_actual.year

st.sidebar.info(f"📅 Fecha: {dia_auto}/{mes_auto}/{anio_auto}")

# Campos solicitados
nombre = st.sidebar.text_input("Nombre del Cliente")
provincia = st.sidebar.selectbox("Provincia", 
    ["Buenos Aires", "CABA", "Córdoba", "Santa Fe", "Mendoza", "Neuquen", "Santa Cruz", "Chubut", "San Juan", "San Luis", "Tucumán", "La Pampa", "Santiago del Estero", "Jujuy", "Tierra del Fuego"])

col1, col2 = st.sidebar.columns(2)
with col1:
    total_fac = st.number_input("Total Factura ($)", min_value=0.0, step=1000.0)
with col2:
    financiacion = st.number_input("Financiación ($)", min_value=0.0, step=500.0)

pago = st.sidebar.selectbox("Pago (Quién cobra)", ["RITA", "CHARLIE", "TOMI", "MERY"])
factura = st.sidebar.radio("¿Factura?", ["Si", "No"], horizontal=True)
articulo = st.sidebar.selectbox("Artículo", 
    ["Vestido", "Tejido", "Vestido Mayor", "Tejido Mayor", "Vestido Promo", "Tejido Promo", "Vestido Sol"])

financiacion_2 = st.sidebar.number_input("Financiación 2 ($)", min_value=0.0, step=500.0)

# --- CÁLCULOS (LAS FÓRMULAS DEL EXCEL) ---

if total_fac > 0:
    # 1. Neto yb IVA
    neto_gravado = total_fac / 1.21
    iva = total_fac - neto_gravado
    
    # 2. IIBB (3.5% del Neto según tu Excel)
    iibb = neto_gravado * 0.035
    
    # 3. Comisión (Coeficiente calculado de tus datos: 0.072479)
    # Ejemplo fila 1: 43269.96 / 597000 = 0.072479
    comision = total_fac * 0.072479
    
    # 4. Obtener Costo % según tabla
    costo_pct = obtener_costo_porcentaje(pago, articulo)
    
    # 5. Cálculo del Costo en $ y Bolsillo
    # Según ingeniería inversa de fila 1 y 2:
    # Base Calculo = Total - Financiacion - Comision
    base_calculo = total_fac - financiacion - comision
    
    costo_pesos = base_calculo * costo_pct
    bolsillo = base_calculo - costo_pesos

    # --- MOSTRAR RESULTADOS ---
    
    st.subheader(f"Resultados para: {nombre}")
    
    # Tarjetas métricas grandes
    m1, m2, m3 = st.columns(3)
    m1.metric("Total Facturado", f"${total_fac:,.2f}")
    m2.metric("Bolsillo (Ganancia)", f"${bolsillo:,.2f}", delta_color="normal")
    m3.metric("Costo", f"${costo_pesos:,.2f}")

    st.markdown("### 📊 Desglose Detallado")
    
    datos_resultado = {
        "Concepto": [
            "Fecha (Día)", "Provincia", "Neto Gravado", "IVA", "Financiación", 
            "IIBB (3.5%)", "Comisión", "Pago A", "Factura", "Artículo", 
            "Costo %", "Costo $", "Financiación 2"
        ],
        "Valor": [
            f"{dia_auto}", provincia, f"${neto_gravado:,.2f}", f"${iva:,.2f}", f"${financiacion:,.2f}",
            f"${iibb:,.2f}", f"${comision:,.2f}", pago, factura, articulo, 
            f"{costo_pct*100}%", f"${costo_pesos:,.2f}", f"${financiacion_2:,.2f}"
        ]
    }
    
    df_resultado = pd.DataFrame(datos_resultado)
    st.table(df_resultado)

    # Botón para simular "Guardar" (Genera un CSV para descargar)
    registro = pd.DataFrame([{
        "Fecha": f"{dia_auto}/{mes_auto}",
        "Nombre": nombre,
        "Provincia": provincia,
        "Neto": neto_gravado,
        "IVA": iva,
        "Total Fac": total_fac,
        "Financiacion": financiacion,
        "IIBB": iibb,
        "Comision": comision,
        "Pago": pago,
        "Factura": factura,
        "Articulo": articulo,
        "Costo %": costo_pct,
        "Costo $": costo_pesos,
        "Bolsillo": bolsillo,
        "Financ 2": financiacion_2
    }])
    
    csv = registro.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="💾 Descargar fila para Excel",
        data=csv,
        file_name=f"Venta_{nombre}_{dia_auto}-{mes_auto}.csv",
        mime="text/csv",
    )

else:
    st.warning("👈 Por favor, ingresa el 'Total Factura' en el menú de la izquierda para ver los cálculos.")

