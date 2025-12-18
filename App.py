import streamlit as st
import pandas as pd
from datetime import datetime

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Calculadora Ropa Dic-25", layout="centered")

st.title("👗 Calculadora de Ventas")
st.markdown("---")

# --- LÓGICA DE COSTOS ---
def obtener_costo_porcentaje(pago, articulo):
    pago = pago.upper()
    articulo = articulo.upper()
    
    if pago == "CHARLIE":
        if "PROMO" in articulo:
            return 0.46
        elif "MAYOR" in articulo:
            return 0.60
        else: 
            return 0.40
            
    elif pago in ["RITA", "TOMI", "MERY"]:
        if "PROMO" in articulo:
            return 0.41
        elif "MAYOR" in articulo:
            return 0.35
        elif "SOL" in articulo:
            return 0.30
        else: 
            return 0.20
            
    return 0.20

# --- ENTRADA DE DATOS (INPUTS) ---
st.sidebar.header("📝 Cargar Nueva Venta")

# Fecha Automática
fecha_actual = datetime.now()
dia_auto = fecha_actual.day
mes_auto = fecha_actual.month
anio_auto = fecha_actual.year

st.sidebar.info(f"📅 Fecha: {dia_auto}/{mes_auto}/{anio_auto}")

# Campos
nombre = st.sidebar.text_input("Nombre del Cliente")
provincia = st.sidebar.selectbox("Provincia", 
    ["Buenos Aires", "CABA", "Córdoba", "Santa Fe", "Mendoza", "Neuquen", "Santa Cruz", "Chubut", "San Juan", "San Luis", "Tucumán", "La Pampa", "Santiago del Estero", "Jujuy", "Tierra del Fuego"])

total_fac = st.sidebar.number_input("💰 Total Factura ($)", min_value=0.0, step=1000.0)

st.sidebar.markdown("---")
st.sidebar.markdown("**Descuentos / Costos:**")

financiacion_cuotas = st.sidebar.number_input("💳 Financiación (Desc. Cuotas)", min_value=0.0, step=500.0, help="Se resta del cálculo")
descuento_efectivo = st.sidebar.number_input("💵 Desc. Efectivo (Columna V)", min_value=0.0, step=500.0, help="SOLO REGISTRO. No afecta el cálculo actual.")

st.sidebar.markdown("---")

pago = st.sidebar.selectbox("Pago (Quién cobra)", ["RITA", "CHARLIE", "TOMI", "MERY"])
factura = st.sidebar.radio("¿Factura?", ["Si", "No"], horizontal=True)
articulo = st.sidebar.selectbox("Artículo", 
    ["Vestido", "Tejido", "Vestido Mayor", "Tejido Mayor", "Vestido Promo", "Tejido Promo", "Vestido Sol"])

# --- CÁLCULOS ---

if total_fac > 0:
    # 1. Neto e IVA
    neto_gravado = total_fac / 1.21
    iva = total_fac - neto_gravado
    
    # 2. IIBB (3.5% del Neto)
    iibb = neto_gravado * 0.035
    
    # 3. Comisión (Coeficiente 0.072479)
    comision = total_fac * 0.072479
    
    # 4. Obtener Costo %
    costo_pct = obtener_costo_porcentaje(pago, articulo)
    
    # 5. CÁLCULO DEL BOLSILLO
    # CORRECCIÓN: NO restamos descuento_efectivo aquí, solo Financiación G y Comisión.
    base_calculo = total_fac - financiacion_cuotas - comision
    
    costo_pesos = base_calculo * costo_pct
    bolsillo = base_calculo - costo_pesos

    # --- MOSTRAR RESULTADOS ---
    
    st.subheader(f"Resultados para: {nombre}")
    
    m1, m2, m3 = st.columns(3)
    m1.metric("Total Facturado", f"${total_fac:,.2f}")
    m2.metric("Bolsillo (Ganancia)", f"${bolsillo:,.2f}", delta_color="normal")
    m3.metric("Costo", f"${costo_pesos:,.2f}")

    st.markdown("### 📊 Desglose (Para Excel)")
    
    datos_resultado = {
        "Concepto": [
            "Fecha", "Neto Gravado", "IVA", 
            "(-) Desc. Cuotas (G)", "Reg. Efectivo (V)", 
            "IIBB", "Comisión", "Pago A", "Artículo", 
            "Costo %", "Costo $"
        ],
        "Valor": [
            f"{dia_auto}/{mes_auto}", f"${neto_gravado:,.2f}", f"${iva:,.2f}", 
            f"${financiacion_cuotas:,.2f}", f"${descuento_efectivo:,.2f}",
            f"${iibb:,.2f}", f"${comision:,.2f}", pago, articulo, 
            f"{costo_pct*100}%", f"${costo_pesos:,.2f}"
        ]
    }
    
    df_resultado = pd.DataFrame(datos_resultado)
    st.table(df_resultado)

    # Botón Descarga CSV (Aquí SÍ incluimos la columna V para que puedas sumar al final de mes)
    registro = pd.DataFrame([{
        "Fecha": f"{dia_auto}/{mes_auto}",
        "Nombre": nombre,
        "Provincia": provincia,
        "Neto": neto_gravado,
        "IVA": iva,
        "Total Fac": total_fac,
        "Financ. Cuotas (G)": financiacion_cuotas,
        "Desc. Efectivo (V)": descuento_efectivo,
        "IIBB": iibb,
        "Comision": comision,
        "Pago": pago,
        "Factura": factura,
        "Articulo": articulo,
        "Costo %": costo_pct,
        "Costo $": costo_pesos,
        "Bolsillo": bolsillo
    }])
    
    csv = registro.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="💾 Descargar fila para Excel",
        data=csv,
        file_name=f"Venta_{nombre}_{dia_auto}-{mes_auto}.csv",
        mime="text/csv",
    )

else:
    st.info("👈 Abre el menú de la izquierda y carga el 'Total Factura' para comenzar.")
