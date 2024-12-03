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
        
        # Create a label to truck progress of translation
        self.progress_label = ctk.CTkLabel(self, text="", wraplength=300)
        self.progress_label.pack(pady=10)
        
        # Create a label to truck progress of the result
        self.result_label = ctk.CTkLabel(self,text="",wraplength=300)
        self.result_label.pack(pady=10)
        
        
        # Create a label to display the selected file path
        self.err_label = ctk.CTkLabel(self, text="", wraplength=300,text_color="red")
        self.err_label.pack(pady=10)
        
        # Create a threadi to update the UI
        self.update_thread = threading.Thread(target=self.update_labels)
        self.update_thread.start()

        self.protocol("WM_DELETE_WINDOW", self.on_closing)
      
      
    def update_labels(self):
        """
        Aggiorna periodicamente le etichette dell'interfaccia utente in base agli eventi del traduttore.
        
        Note:
            - Esegue un loop continuo finché self.non_stop è True.
            - Verifica se un evento di aggiornamento è stato impostato dal traduttore.
            - Se un evento è presente, aggiorna l'interfaccia utente chiamando self.update_gui.
            - Pulisce l'evento di aggiornamento dopo averlo elaborato.
            - Introduce una breve pausa di 1 secondo tra gli aggiornamenti.
        
        Raises:
            Exception: Se si verifica un errore durante l'aggiornamento dell'interfaccia.
        """
        while self.non_stop:
            if self.translator.update_event.is_set():
                self.after(0, self.update_gui)
                self.translator.update_event.clear()
            self.after(1000, lambda: None)

    
    def update_gui(self):
        """
        Aggiorna l'interfaccia utente con le informazioni più recenti dal traduttore.
        
        Note:
            - Aggiorna l'etichetta del timer con il valore corrente.
            - Aggiorna l'etichetta di progresso con le informazioni sul file in corso.
            - Aggiorna l'etichetta di errore con eventuali messaggi di errore.
        
        Raises:
            Exception: Se si verifica un errore durante l'aggiornamento dell'interfaccia.
        """
        self.timer_label.configure(text=self.translator.timer)
        self.progress_label.configure(text=self.translator.proced_file)
        self.err_label.configure(text=self.translator.err_message)

    
    def on_closing(self):
        """
        Gestisce la chiusura dell'applicazione, assicurandosi che tutti i thread in esecuzione vengano terminati correttamente.
        
        Note:
            - Verifica se il thread di aggiornamento è attivo e lo fa terminare con un timeout di 5 secondi.
            - Verifica se il thread di traduzione è attivo e lo fa terminare con un timeout di 5 secondi.
            - Imposta self.non_stop a False per fermare il loop principale.
            - Chiude la finestra dell'applicazione.
        
        Raises:
            Exception: Se si verifica un errore durante la chiusura dell'applicazione.
        """
        
        if hasattr(self, 'update_thread') and self.update_thread.is_alive():
            self.update_thread.join(timeout=5)
            
        if hasattr(self.translator, 'translation_thread') and self.translator.translation_thread.is_alive():
            self.translator.translation_thread.join(timeout=5)
            self.non_stop = False  # Give it 5 seconds to stop
        
        # Close the window
        self.destroy()
    
    
    def start_translation(self):
        """
        Avvia il processo di traduzione dei file SRT selezionati.
        
        Note:
            - Disabilita il pulsante di traduzione per prevenire azioni multiple.
            - Crea e avvia un thread separato per eseguire la traduzione.
            - Attende la conclusione del thread di traduzione.
            - Mostra il risultato della traduzione una volta completata.
            - Gestisce eventuali eccezioni durante il processo di traduzione.
        
        Raises:
            Exception: Se si verifica un errore durante il processo di traduzione.
        """
        try:
            self.translate_button.configure(state="disabled")
            self.translator.translation_thread = threading.Thread(target=self.translator.translates_srt_files)
            self.translator.translation_thread.start()
            
            # Attendi la conclusione del thread di traduzione
            self.translator.translation_thread.join()
            
            # Mostra il risultato della traduzione
            self.show_result()
        except Exception as e:
            # Visualizza il messaggio di errore e riabilita il pulsante di traduzione
            self.err_label.configure(text=str(e))
            self.translate_button.configure(state="normal")
            
  
    def select_files(self):
        """
        Seleziona i file SRT da tradurre e aggiorna l'interfaccia utente di conseguenza.
        
        Note:
            - Apre una finestra di dialogo per permettere all'utente di selezionare i file SRT.
            - Se i file vengono selezionati con successo:
              - Aggiorna l'etichetta dei file selezionati con il numero di file.
              - Abilita il pulsante di traduzione.
            - Se si verifica un errore durante la selezione:
              - Visualizza il messaggio di errore nell'etichetta di errore.
              - Abilita il pulsante di traduzione.
        
        Raises:
            Exception: Se si verifica un errore durante il processo di selezione dei file.
        """
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
        """
        Mostra il risultato della traduzione una volta completata.
        
        Note:
            - Crea un'etichetta con il messaggio di completamento e il numero di file tradotti.
            - Imposta la dimensione del font e lo stile dell'etichetta.
            - Aggiunge l'etichetta all'interfaccia utente con un padding verticale.
            - Disabilita il pulsante di traduzione dopo il completamento.
        
        Raises:
            Exception: Se si verifica un errore durante la creazione o l'aggiunta dell'etichetta.
        """
        result_label = ctk.CTkLabel(self, text=f"Traduzione completata! File tradotti {len(self.translator.get_file_names(self.translator.directory_path[0]['path']))}", font=("Arial", 16))
        result_label.pack(pady=20)
        self.translate_button.configure(state="disabled")  # Disable the button after translation
    
