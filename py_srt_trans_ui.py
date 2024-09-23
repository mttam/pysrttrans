import customtkinter as ctk
from py_srt_trans import PySrtTrans
import threading

class UiPySrtTrans(ctk.CTk):
    
    def __init__(self) -> None:
        super().__init__()
        self.title("Python Srt Translator")
        self.geometry("600x400")
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("green")
        # Initialize PySrtTrans
        self.translator = PySrtTrans()
        self.icon_path = "logo.ico"
        self.iconbitmap(self.icon_path)
        
        self.non_stop=True
        
        # Create a button to select SRT files
        self.select_button = ctk.CTkButton(self, text="Select SRT Files", command=self.select_files)
        self.select_button.pack(pady=20)

        # Create a label to display the selected file path
        self.file_label = ctk.CTkLabel(self, text="", wraplength=300)
        self.file_label.pack(pady=10)
        
        self.timer_label = ctk.CTkLabel(self,text="",font=("Arial",14),text_color='red')
        self.timer_label.pack(pady=10)

        # Create a button to start translation
        self.translate_button = ctk.CTkButton(self, text="Comincia Traduzione", state="disabled", command=threading.Thread(target=self.start_translation).start)
        self.translate_button.pack(pady=20)
        
        self.progress_label = ctk.CTkLabel(self, text="", wraplength=300)
        self.progress_label.pack(pady=10)
        
        self.result_label = ctk.CTkLabel(self,text="",wraplength=300)
        self.result_label.pack(pady=10)
        
        
        # Create a label to display the selected file path
        self.err_label = ctk.CTkLabel(self, text="", wraplength=300,text_color="red")
        self.err_label.pack(pady=10)
        
        self.update_thread = threading.Thread(target=self.update_labels)
        self.update_thread.start()

        self.protocol("WM_DELETE_WINDOW", self.on_closing)
      
        
    def update_labels(self):
        while self.non_stop:
            if self.translator.update_event.is_set():
                self.after(0, self.update_gui)
                self.translator.update_event.clear()
            self.after(1000, lambda: None)

    def update_gui(self):
        self.timer_label.configure(text=self.translator.timer)
        self.progress_label.configure(text=self.translator.proced_file)
        self.err_label.configure(text=self.translator.err_message)

    def on_closing(self):
        
        if hasattr(self,'update_thread') and self.update_thread.is_alive():
            self.update_thread.join(timeout=5)
            
        
        if hasattr(self.translator, 'translation_thread') and self.translator.translation_thread.is_alive():
            self.translator.translation_thread.join(timeout=5)
            self.non_stop=False# Give it 5 seconds to stop
        
        # Close the window
        self.destroy()
    
    
    def update_gui(self):
        self.timer_label.configure(text=self.translator.timer)
        self.progress_label.configure(text=self.translator.proced_file)
        self.err_label.configure(text=self.translator.err_message)
        
    
    def start_translation(self):
        try:
            self.translate_button.configure(state="disabled")
            self.translator.translation_thread = threading.Thread(target=self.translator.translates_srt_files)
            self.translator.translation_thread.start()
            
            
            self.translator.translation_thread.join()
            
            self.show_result()
        except Exception as e:
            self.err_label.configure(text=str(e))
            self.translate_button.configure(state="normal")
            
    
    def select_files(self):
        try:
            self.result_label.configure(text="")
            self.translator.select_srt_files()
            if self.translator.file_path:
                self.file_label.configure(text=f"Files selezionati {len(self.translator.get_file_names(self.translator.directory_path[0]['path']))}")
                self.translate_button.configure(state="normal")
        except Exception as e:
            self.err_label.configure(text=str(e))
            self.translate_button.configure(state="normal")

    def show_result(self):
        result_label = ctk.CTkLabel(self, text=f"Traduzione completata! File tradotti {len(self.translator.get_file_names(self.translator.directory_path[0]['path']))}", font=("Arial", 16))
        result_label.pack(pady=20)
        self.translate_button.configure(state="disabled")  # Disable the button after translation
    
