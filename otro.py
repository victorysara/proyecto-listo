import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime
import json
import os

# Archivos de base de datos
CONFIG_FILE = "config_tech.json"
DATA_FILE = "inventario_data.json"

class TechSystemPro:
    def __init__(self, root):
        self.root = root
        self.root.title("Tech System Pro - Win7 Edition")
        self.root.geometry("600x650")
        
        self.verificar_archivos()
        self.bg_color = self.cargar_config()
        self.inventario = self.cargar_datos() 
        
        self.root.protocol("WM_DELETE_WINDOW", self.cerrar_aplicacion)
        self.setup_login()

    def verificar_archivos(self):
        if not os.path.exists(DATA_FILE):
            with open(DATA_FILE, "w") as f: json.dump({}, f)
        if not os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "w") as f: json.dump({"color": "#f4f4f4"}, f)

    def cargar_config(self):
        try:
            with open(CONFIG_FILE, "r") as f: return json.load(f).get("color", "#f4f4f4")
        except: return "#f4f4f4"

    def cargar_datos(self):
        try:
            with open(DATA_FILE, "r") as f: 
                data = json.load(f)
                return {str(k): v for k, v in data.items()}
        except: return {}

    def guardar_todo(self):
        with open(DATA_FILE, "w") as f:
            json.dump(self.inventario, f, indent=4)

    def cerrar_aplicacion(self):
        self.guardar_todo()
        self.root.destroy()

    def limpiar_ventana(self):
        for widget in self.root.winfo_children(): widget.destroy()

    # --- LOGIN CON FLUJO DE ENTER ---
    def setup_login(self):
        self.limpiar_ventana()
        self.root.configure(bg=self.bg_color)
        frame = tk.Frame(self.root, bg=self.bg_color)
        frame.pack(expand=True)
        tk.Label(frame, text="BIENVENIDO ADMIN", font=("Arial", 22, "bold"), bg=self.bg_color).pack(pady=20)
        
        tk.Label(frame, text="Usuario:", bg=self.bg_color).pack()
        self.ent_user = tk.Entry(frame, font=("Arial", 12), justify="center")
        self.ent_user.pack(pady=5)
        self.ent_user.focus_set()
        # Al dar Enter, pasa al campo de contraseña
        self.ent_user.bind('<Return>', lambda e: self.ent_pass.focus())

        tk.Label(frame, text="Contraseña:", bg=self.bg_color).pack()
        self.ent_pass = tk.Entry(frame, show="*", font=("Arial", 12), justify="center")
        self.ent_pass.pack(pady=5)
        # Al dar Enter, ejecuta la validación (como pulsar el botón)
        self.ent_pass.bind('<Return>', lambda e: self.validar_login())

        tk.Button(frame, text="ENTRAR", command=self.validar_login, bg="#2ecc71", fg="white", width=15, font=("Arial", 10, "bold")).pack(pady=20)

    def validar_login(self):
        if self.ent_user.get() == "admin" and self.ent_pass.get() == "12345": self.menu_principal()
        else: messagebox.showerror("Error", "Credenciales incorrectas")

    # --- MENÚ PRINCIPAL ---
    def menu_principal(self):
        self.limpiar_ventana()
        self.root.geometry("600x650")
        frame = tk.Frame(self.root, bg=self.bg_color)
        frame.pack(expand=True, fill="both")
        tk.Label(frame, text="MENÚ PRINCIPAL", font=("Arial", 22, "bold"), bg=self.bg_color).pack(pady=40)
        btn_s = {"font": ("Arial", 11, "bold"), "width": 35, "height": 2}
        tk.Button(frame, text="📦 GESTIÓN E HISTORIAL", command=self.pantalla_gestion, bg="#3498db", fg="white", **btn_s).pack(pady=10)
        tk.Button(frame, text="🎨 COLOR DE FONDO", command=self.ventana_color, **btn_s).pack(pady=10)
        tk.Button(frame, text="❓ AYUDA", command=self.mostrar_ayuda, bg="#f1c40f", **btn_s).pack(pady=10)
        tk.Button(frame, text="❌ SALIR DEL SISTEMA", command=self.cerrar_aplicacion, bg="#e74c3c", fg="white", **btn_s).pack(pady=10)

    def mostrar_ayuda(self):
        ayuda_texto = (
            "GUÍA RÁPIDA:\n\n"
            "- NUEVO: Registra un producto.\n"
            "- MOVER: Salida a profesor.\n"
            "- REINTEGRO: Devuelve y limpia historial.\n"
            "- ELIMINAR: Borra permanentemente del archivo."
        )
        messagebox.showinfo("Ayuda", ayuda_texto)

    # --- PANTALLA GESTIÓN ---
    def pantalla_gestion(self):
        self.limpiar_ventana()
        self.root.geometry("1150x800")
        toolbar = tk.Frame(self.root, bg="#2c3e50", pady=10)
        toolbar.pack(side="top", fill="x")
        
        btn_t = {"font": ("Arial", 8, "bold"), "width": 14}
        tk.Button(toolbar, text="NUEVO", command=self.pop_nuevo, **btn_t).pack(side="left", padx=5)
        tk.Button(toolbar, text="BUSCAR", command=self.pop_buscar, bg="#9b59b6", fg="white", **btn_t).pack(side="left", padx=5)
        tk.Button(toolbar, text="MOVER", command=self.pop_mover, bg="#f1c40f", **btn_t).pack(side="left", padx=5)
        tk.Button(toolbar, text="REINTEGRO", command=self.pop_reintegro, **btn_t).pack(side="left", padx=5)
        tk.Button(toolbar, text="ELIMINAR", command=self.eliminar_seleccion, bg="#e74c3c", fg="white", **btn_t).pack(side="left", padx=5)
        tk.Button(toolbar, text="VOLVER", command=self.menu_principal, **btn_t).pack(side="right", padx=5)

        f1 = tk.LabelFrame(self.root, text=" REGISTRO DE PRODUCTOS ", bg=self.bg_color, font=("Arial", 10, "bold"))
        f1.pack(fill="both", expand=True, padx=15, pady=5)
        self.tree_reg = ttk.Treeview(f1, columns=("C", "N", "S", "NS", "T"), show='headings', selectmode="browse")
        for c, h in zip(("C", "N", "S", "NS", "T"), ("Código", "Nombre", "Sirve", "No Sirve", "Total")):
            self.tree_reg.heading(c, text=h); self.tree_reg.column(c, anchor="center")
        self.tree_reg.pack(fill="both", expand=True, padx=5, pady=5)

        f2 = tk.LabelFrame(self.root, text=" HISTORIAL DE MOVIMIENTOS ", bg=self.bg_color, font=("Arial", 10, "bold"))
        f2.pack(fill="both", expand=True, padx=15, pady=5)
        self.tree_his = ttk.Treeview(f2, columns=("F", "C", "Q", "E", "P"), show='headings', selectmode="browse")
        for c, h in zip(("F", "C", "Q", "E", "P"), ("Fecha", "Código", "Cant.", "Estado", "Profesor")):
            self.tree_his.heading(c, text=h); self.tree_his.column(c, anchor="center")
        self.tree_his.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.actualizar_tablas()

    def actualizar_tablas(self):
        for i in self.tree_reg.get_children(): self.tree_reg.delete(i)
        for i in self.tree_his.get_children(): self.tree_his.delete(i)
        for cod, d in self.inventario.items():
            self.tree_reg.insert("", "end", values=(cod, d[0], d[1], d[2], d[1]+d[2]))
            for h in d[3]: self.tree_his.insert("", "end", values=h)

    def eliminar_seleccion(self):
        sel_reg = self.tree_reg.selection()
        sel_his = self.tree_his.selection()
        
        if sel_reg:
            item = sel_reg[0]
            cod = str(self.tree_reg.item(item)['values'][0]).strip()
            if messagebox.askyesno("ELIMINAR", f"¿Borrar {cod} del sistema permanentemente?"):
                if cod in self.inventario:
                    del self.inventario[cod]
                    self.guardar_todo()
                    self.actualizar_tablas()
        elif sel_his:
            item = sel_his[0]
            vals = self.tree_his.item(item)['values']
            fecha, cod = str(vals[0]), str(vals[1]).strip()
            if messagebox.askyesno("ELIMINAR", "¿Borrar registro del historial?"):
                if cod in self.inventario:
                    self.inventario[cod][3] = [h for h in self.inventario[cod][3] if str(h[0]) != fecha]
                    self.guardar_todo()
                    self.actualizar_tablas()
        else:
            messagebox.showwarning("!", "Selecciona una fila para eliminar.")

    def pop_reintegro(self):
        pop = tk.Toplevel(self.root); pop.geometry("350x400")
        tk.Label(pop, text="CÓDIGO:").pack(); e_c = tk.Entry(pop); e_c.pack()
        tk.Label(pop, text="CANTIDAD:").pack(); e_q = tk.Entry(pop); e_q.pack()
        v_r = tk.StringVar(value="Sirve")
        tk.Radiobutton(pop, text="Sirve", variable=v_r, value="Sirve").pack()
        tk.Radiobutton(pop, text="No Sirve", variable=v_r, value="No Sirve").pack()
        def ok():
            c, q = e_c.get().strip(), int(e_q.get() or 0)
            if c in self.inventario:
                idx = 1 if v_r.get() == "Sirve" else 2
                self.inventario[c][idx] += q
                self.inventario[c][3] = [] # Limpia historial
                self.guardar_todo(); self.actualizar_tablas(); pop.destroy()
        tk.Button(pop, text="REINTEGRAR", command=ok, bg="#3498db", fg="white").pack(pady=20)

    # --- RESTO DE FUNCIONES MANTENIDAS ---
    def pop_buscar(self):
        pop = tk.Toplevel(self.root); pop.geometry("300x150")
        tk.Label(pop, text="Código:").pack(); eb = tk.Entry(pop); eb.pack(); eb.focus_set()
        def buscar():
            q = eb.get().strip()
            if q in self.inventario:
                d = self.inventario[q]
                messagebox.showinfo("OK", f"Nombre: {d[0]}\nTotal: {d[1]+d[2]}")
                pop.destroy()
            else: messagebox.showerror("Error", "No existe")
        tk.Button(pop, text="BUSCAR", command=buscar, bg="#9b59b6", fg="white").pack(pady=10)

    def pop_nuevo(self):
        pop = tk.Toplevel(self.root); pop.geometry("350x380")
        tk.Label(pop, text="COD:").pack(); e1 = tk.Entry(pop); e1.pack(); e1.focus_set()
        tk.Label(pop, text="NOM:").pack(); e2 = tk.Entry(pop); e2.pack()
        tk.Label(pop, text="SIRVE:").pack(); e3 = tk.Entry(pop); e3.pack(); e3.insert(0,"0")
        tk.Label(pop, text="NO SIRVE:").pack(); e4 = tk.Entry(pop); e4.pack(); e4.insert(0,"0")
        def ok():
            c = str(e1.get()).strip()
            if c:
                self.inventario[c] = [e2.get().upper(), int(e3.get() or 0), int(e4.get() or 0), []]
                self.guardar_todo(); self.actualizar_tablas(); pop.destroy()
        tk.Button(pop, text="GUARDAR", command=ok, bg="#27ae60", fg="white").pack(pady=20)

    def pop_mover(self):
        pop = tk.Toplevel(self.root); pop.geometry("400x450")
        tk.Label(pop, text="COD:").pack(); e_c = tk.Entry(pop); e_c.pack()
        tk.Label(pop, text="CANT:").pack(); e_q = tk.Entry(pop); e_q.pack()
        v_t = tk.StringVar(value="Sirve")
        tk.Radiobutton(pop, text="Sirve", variable=v_t, value="Sirve").pack()
        tk.Radiobutton(pop, text="No Sirve", variable=v_t, value="No Sirve").pack()
        tk.Label(pop, text="PROFE:").pack(); e_p = tk.Entry(pop); e_p.pack()
        def mover():
            c, q = e_c.get().strip(), int(e_q.get() or 0)
            if c in self.inventario:
                idx = 1 if v_t.get() == "Sirve" else 2
                if self.inventario[c][idx] >= q:
                    self.inventario[c][idx] -= q
                    f = datetime.now().strftime("%d/%m %H:%M")
                    self.inventario[c][3].append([f, c, q, v_t.get(), e_p.get().upper()])
                    self.guardar_todo(); self.actualizar_tablas(); pop.destroy()
        tk.Button(pop, text="REGISTRAR", command=mover, bg="#f1c40f").pack(pady=20)

    def ventana_color(self):
        win = tk.Toplevel(self.root); win.geometry("250x350")
        colores = ["#ffffff", "#add8e6", "#98fb98", "#ffebcd", "#d3d3d3", "#f4f4f4"]
        for c in colores:
            tk.Button(win, bg=c, text=f"Color {c}", command=lambda col=c: self.aplicar_color(col)).pack(fill="x", pady=2)
    
    def aplicar_color(self, col):
        self.bg_color = col
        with open(CONFIG_FILE, "w") as f: json.dump({"color": col}, f)
        self.root.configure(bg=col)

if __name__ == "__main__":
    root = tk.Tk()
    app = TechSystemPro(root)
    root.mainloop()
    
