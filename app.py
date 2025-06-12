# Importamos streamlit, la herramienta para crear la web app
import streamlit as st
from datetime import datetime

# ====================================================================
# TODA LA LÓGICA DE CÁLCULO QUE YA CREAMOS.
# ¡ESTA PARTE NO CAMBIA EN ABSOLUTO! LA COPIAMOS Y PEGAMOS TAL CUAL.
# ====================================================================
FRANJAS = [(15, 0.22, 0.33), (45, 0.20, 0.26), (90, 0.18, 0.24), (150, 0.16, 0.22), (450, 0.14, 0.20), (750, 0.12, 0.17), (float('inf'), 0.10, 0.15)]
MIN_HONORARY_PROCESO_CONOCIMIENTO = 10.0

def generate_report_string(amount_in_uma):
    report_lines = []
    # --- Encabezado General ---
    report_lines.append("--------------------------------------------------------------------")
    report_lines.append("      CÁLCULO DE HONORARIOS SUGERIDOS - LEY 27.423")
    report_lines.append("--------------------------------------------------------------------")
    report_lines.append(f"Fecha del Cálculo: {datetime.now().strftime('%d/%m/%Y')}")
    report_lines.append(f"Monto del Proceso Analizado: {amount_in_uma:.2f} UMA")

    honorary_max = 0.0
    honorary_min_hybrid = 0.0
    previous_upper_limit = 0.0
    
    for i, (upper_limit, min_perc, max_perc) in enumerate(FRANJAS):
        if amount_in_uma <= previous_upper_limit: break
        amount_in_tranche = min(amount_in_uma, upper_limit) - previous_upper_limit
        honorary_max += amount_in_tranche * max_perc
        if amount_in_uma > upper_limit:
            honorary_min_hybrid += amount_in_tranche * max_perc
        else:
            honorary_min_hybrid += amount_in_tranche * min_perc
        previous_upper_limit = upper_limit

    report_lines.append("\n====================================================================")
    report_lines.append("  CÁLCULO DEL HONORARIO MÁXIMO SUGERIDO")
    report_lines.append("====================================================================")
    report_lines.append("Se calcula sumando el resultado de aplicar el % MÁXIMO a cada tramo.\n")
    temp_previous_upper_limit = 0
    for i, (upper_limit, _, max_perc) in enumerate(FRANJAS):
        if amount_in_uma <= temp_previous_upper_limit: break
        amount_in_tranche = min(amount_in_uma, upper_limit) - temp_previous_upper_limit
        label = f"Tramo {i+1}" if amount_in_uma > upper_limit else "Excedente"
        report_lines.append(f"  - {label} (al {max_perc:.2%}): {(amount_in_tranche * max_perc):.2f} UMA")
        temp_previous_upper_limit = upper_limit
    report_lines.append("  ------------------------------------------------------------------")
    report_lines.append(f"  > TOTAL MÁXIMO SUGERIDO: {honorary_max:.2f} UMA")

    report_lines.append("\n====================================================================")
    report_lines.append("  CÁLCULO DEL HONORARIO MÍNIMO SUGERIDO")
    report_lines.append("====================================================================")
    report_lines.append("Se usan los % MÁXIMOS para tramos completos y solo el % MÍNIMO para el excedente.\n")
    temp_previous_upper_limit = 0
    for i, (upper_limit, min_perc, max_perc) in enumerate(FRANJAS):
        if amount_in_uma <= temp_previous_upper_limit: break
        amount_in_tranche = min(amount_in_uma, upper_limit) - temp_previous_upper_limit
        if amount_in_uma > upper_limit:
            report_lines.append(f"  - Tramo {i+1} (al {max_perc:.2%}): {(amount_in_tranche * max_perc):.2f} UMA")
        else:
            report_lines.append(f"  - Excedente (al {min_perc:.2%}): {(amount_in_tranche * min_perc):.2f} UMA")
        temp_previous_upper_limit = upper_limit
    report_lines.append("  ------------------------------------------------------------------")
    report_lines.append(f"  > TOTAL MÍNIMO SUGERIDO: {honorary_min_hybrid:.2f} UMA")

    final_min_honorary = max(honorary_min_hybrid, MIN_HONORARY_PROCESO_CONOCIMIENTO)
    
    report_lines.append("\n====================================================================")
    report_lines.append("              RANGO FINAL DE HONORARIOS SUGERIDOS")
    report_lines.append("====================================================================")
    report_lines.append(f"Considerando el piso legal de {MIN_HONORARY_PROCESO_CONOCIMIENTO:.2f} UMA (Art. 58) para el mínimo.\n")
    report_lines.append(f"  HONORARIO MÍNIMO: {final_min_honorary:.2f} UMA")
    report_lines.append(f"  HONORARIO MÁXIMO: {honorary_max:.2f} UMA")
    report_lines.append("--------------------------------------------------------------------")

    return "\n".join(report_lines)

# ====================================================================
# INTERFAZ DE LA APLICACIÓN WEB CON STREAMLIT
# Esta parte reemplaza todo el código de tkinter.
# ====================================================================

# Configuración de la página (título en la pestaña del navegador, ícono, etc.)
st.set_page_config(page_title="Calculadora de Honorarios | By Sebastián Careaga Quiroga", page_icon="⚖️", layout="centered")

# Título principal de la aplicación
st.title("Calculadora de Honorarios Profesionales")
st.markdown("Ley 27.423 - Creada por **Sebastián Careaga Quiroga**")

st.divider() # Una línea divisoria

# Campo para que el usuario ingrese el monto en UMA
# 'value=None' para que empiece vacío, 'placeholder' es el texto gris de guía
amount_uma_input = st.number_input(
    label="Ingrese el Monto del Proceso en UMA:",
    min_value=0.0,
    value=None,
    step=10.0,
    format="%.2f",
    placeholder="Ej: 707.12"
)

# Botón para iniciar el cálculo
calculate_button = st.button("Calcular Honorarios", type="primary", use_container_width=True)


# Lógica de la aplicación
if calculate_button:
    if amount_uma_input is not None and amount_uma_input > 0:
        # Si el usuario ingresó un valor y presionó el botón, generamos el reporte
        final_report = generate_report_string(amount_uma_input)
        
        st.divider()
        st.subheader("Reporte de Cálculo Detallado")
        
        # Mostramos el reporte en un área de texto con fondo gris claro
        # st.code() es ideal para texto pre-formateado como nuestro reporte
        st.code(final_report, language=None)
        
    else:
        # Si el usuario no ingresó un valor, mostramos una advertencia
        st.warning("Por favor, ingrese un monto en UMA para poder calcular.")

# Pie de página
st.divider()
st.caption("Esta herramienta es una guía de referencia basada en la Ley 27.423. La regulación final puede variar según el criterio judicial.")