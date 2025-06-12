# Importamos las librerías necesarias
import tkinter as tk
#from tkinter import ttk  <-- Ya no usamos ttk directamente
import ttkbootstrap as tb # <-- Importamos la nueva librería de estilos
from tkinter import scrolledtext, filedialog, messagebox
from datetime import datetime
from fpdf import FPDF

# --- CLASE PERSONALIZADA PARA CREAR EL PDF CON SELLO DE AGUA ---
class PDF_con_Sello_de_Agua(FPDF):
    def header(self):
        self.set_font('Helvetica', 'B', 50)
        self.set_text_color(220, 220, 220)
        self.rotate(45, x=self.w / 2 - 60, y=self.h / 2 + 10)
        self.text(x=self.w / 2 - 60, y=self.h / 2 + 10, txt="Sebastián Careaga Quiroga")
        self.rotate(0)
        self.set_text_color(0, 0, 0)
        self.set_font('Courier', '', 10)
    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(128)
        self.cell(0, 10, f'Página {self.page_no()}', 0, 0, 'C')

# --- DATOS Y LÓGICA DE CÁLCULO (sin cambios) ---
FRANJAS = [(15, 0.22, 0.33), (45, 0.20, 0.26), (90, 0.18, 0.24), (150, 0.16, 0.22), (450, 0.14, 0.20), (750, 0.12, 0.17), (float('inf'), 0.10, 0.15)]
MIN_HONORARY_PROCESO_CONOCIMIENTO = 10.0

def generate_report_string(amount_in_uma):
    # El reporte es el mismo que en la versión anterior
    report_lines = []
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

# --- INTERFAZ GRÁFICA (GUI) - CON ESTÉTICA MEJORADA ---
def on_calculate_button_click():
    try:
        user_input_uma = float(entry_uma.get())
        if user_input_uma < 0:
            messagebox.showerror("Error", "El monto no puede ser negativo.")
            return
        report_string = generate_report_string(user_input_uma)
        result_text.config(state="normal")
        result_text.delete(1.0, tk.END)
        result_text.insert(tk.END, report_string)
        result_text.config(state="disabled")
        copy_button.config(state="normal")
        pdf_button.config(state="normal")
    except ValueError:
        messagebox.showerror("Error", "Por favor, introduce un número válido.")
        copy_button.config(state="disabled")
        pdf_button.config(state="disabled")
def copy_results_to_clipboard():
    text_to_copy = result_text.get(1.0, tk.END)
    root.clipboard_clear()
    root.clipboard_append(text_to_copy)
    messagebox.showinfo("Copiado", "El resultado ha sido copiado al portapapeles.")
def save_report_as_pdf():
    report_string = result_text.get(1.0, tk.END)
    if not report_string.strip():
        messagebox.showwarning("Vacío", "No hay nada que guardar. Primero realiza un cálculo.")
        return
    filepath = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("Archivos PDF", "*.pdf"), ("Todos los archivos", "*.*")], title="Guardar reporte como PDF", initialfile=f"Honorarios - {datetime.now().strftime('%Y-%m-%d')}.pdf")
    if not filepath: return
    try:
        pdf = PDF_con_Sello_de_Agua('P', 'mm', 'A4')
        pdf.add_page()
        pdf.set_font('Courier', '', 10)
        pdf.multi_cell(0, 5, txt=report_string)
        pdf.output(filepath)
        messagebox.showinfo("Éxito", f"El PDF ha sido guardado correctamente en:\n{filepath}")
    except Exception as e: messagebox.showerror("Error al guardar PDF", f"Ocurrió un error:\n{e}")

# --- Configuración de la Ventana ---
# root = tk.Tk() <-- La línea antigua
root = tb.Window(themename="litera") # <-- La nueva línea, con el tema "litera"
root.title("Calculadora de Honorarios (Ley 27.423)")
root.geometry("800x750")

# --- Contenedor Principal con Padding ---
main_frame = tb.Frame(root, padding=15)
main_frame.pack(expand=True, fill="both")

# --- Frame para los Controles de Entrada ---
input_frame = tb.Frame(main_frame)
input_frame.pack(fill="x", pady=(0, 15)) # pady añade espacio vertical

label_uma = tb.Label(input_frame, text="Monto del Proceso en UMA:", font=("Helvetica", 11))
label_uma.pack(side="left", padx=(0, 10))

entry_uma = tb.Entry(input_frame, width=20)
entry_uma.pack(side="left", padx=(0, 10), fill="x", expand=True)

# --- Frame para los Botones ---
button_frame = tb.Frame(main_frame)
button_frame.pack(fill="x", pady=(0, 20))

# bootstyle da los colores y estilos a los botones
calculate_button = tb.Button(button_frame, text="Calcular", command=on_calculate_button_click, bootstyle="primary")
calculate_button.pack(side="left", fill="x", expand=True, padx=(0, 5))

copy_button = tb.Button(button_frame, text="Copiar Resultado", command=copy_results_to_clipboard, state="disabled", bootstyle="info")
copy_button.pack(side="left", fill="x", expand=True, padx=5)

pdf_button = tb.Button(button_frame, text="Guardar como PDF", command=save_report_as_pdf, state="disabled", bootstyle="success")
pdf_button.pack(side="left", fill="x", expand=True, padx=(5, 0))

# --- Área de texto para mostrar los resultados ---
result_text = scrolledtext.ScrolledText(main_frame, wrap=tk.WORD, font=("Consolas", 10), state="disabled", relief="solid", borderwidth=1)
result_text.pack(expand=True, fill="both")

root.mainloop()