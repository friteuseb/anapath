import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
from pathology_image_analyzer import PathologyImageAnalyzer

class PathologyImageGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Analyseur d'images pathologiques")
        self.master.geometry("1400x800")

        self.analyzer = PathologyImageAnalyzer()
        self.image_path = None
        self.photo = None
        self.annotated_photo = None

        self.create_widgets()

    def create_widgets(self):
        self.load_button = tk.Button(self.master, text="Charger une image", command=self.load_image)
        self.load_button.pack(pady=10)

        self.sample_type_var = tk.StringVar(value='sang')
        self.sample_type_menu = tk.OptionMenu(self.master, self.sample_type_var, 'sang', 'urine')
        self.sample_type_menu.pack(pady=10)

        self.canvas = tk.Canvas(self.master, width=400, height=400)
        self.canvas.pack(pady=10, side=tk.LEFT)

        self.analyze_button = tk.Button(self.master, text="Analyser l'image", command=self.analyze_image)
        self.analyze_button.pack(pady=10)

        self.technical_report_text = tk.Text(self.master, height=20, width=50)
        self.technical_report_text.pack(pady=10, side=tk.LEFT)

        self.clinical_report_text = tk.Text(self.master, height=20, width=50)
        self.clinical_report_text.pack(pady=10, side=tk.LEFT)

        self.annotated_canvas = tk.Canvas(self.master, width=400, height=400)
        self.annotated_canvas.pack(pady=10, side=tk.RIGHT)

    def load_image(self):
        self.image_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp")])
        if self.image_path:
            image = Image.open(self.image_path)
            image.thumbnail((400, 400))
            self.photo = ImageTk.PhotoImage(image)
            self.canvas.create_image(200, 200, image=self.photo)

    def analyze_image(self):
        if self.image_path:
            try:
                self.analyzer.set_sample_type(self.sample_type_var.get())
                results = self.analyzer.analyze(self.image_path)
                technical_report, clinical_report = self.analyzer.generate_report()
                self.technical_report_text.delete(1.0, tk.END)
                self.technical_report_text.insert(tk.END, technical_report)
                self.clinical_report_text.delete(1.0, tk.END)
                self.clinical_report_text.insert(tk.END, clinical_report)
                
                # Save and display the annotated image
                self.analyzer.highlight_anomalies("annotated_image.png")
                annotated_image = Image.open("annotated_image.png")
                annotated_image.thumbnail((400, 400))
                self.annotated_photo = ImageTk.PhotoImage(annotated_image)
                self.annotated_canvas.create_image(200, 200, image=self.annotated_photo)

            except Exception as e:
                messagebox.showerror("Erreur", f"Une erreur est survenue lors de l'analyse : {str(e)}")
        else:
            messagebox.showwarning("Attention", "Veuillez d'abord charger une image.")

if __name__ == "__main__":
    root = tk.Tk()
    app = PathologyImageGUI(root)
    root.mainloop()
