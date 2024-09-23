import os
import pysrt 
import google.generativeai as genai
import logging
import tkinter as tk
from tkinter import filedialog
from config import key,prompt
from math import ceil
import shutil
from time import sleep
import threading
from vertexai.preview import tokenization
# Limiti versione FREE
'''
Senza costi:
2 rpm
32.000 T/M
50 RPD
di Gemini Advanced.

RPM: richieste al minuto
TPM: token al minuto
RPD: richieste al giorno
TPD: token al giorno

'''


# TODO
# 1 Importare la chiave,il prompt , cosa tradurre e google-gemini V
# 2 Dividere il file in sotto file V
# 3 mandare il prompt più la parte da tradurre V
# 4 unire le parti e scriverle in un nuovo file V
# 5 creare una classe V
# 5.1 crea un file requisiti V
# 6 creare un file unico per chiave,propmt V
# 7 creare una UI V

TIME_OUT: int = 60
MAX_REQUEST: int = 50 
MAX_ROWS: int = 150
MODEL_NAME : str = "gemini-1.5-pro"


def formated_final_path(directory,name):
    new_name =  name.split('.')[0] + '_translated.' + name.split('.')[1]
    return f"{directory}/{new_name}"

def formated_initial_path(directory,name):
    return f"{directory}/{name}"

def select_rows_per_part(rows):
    max_rows_per_part = MAX_ROWS
    total_parts = ceil (rows  / max_rows_per_part)
    return max_rows_per_part,total_parts
   
    
class PySrtTrans:
    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(
            filename='app.log',
            filemode='a',
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            level=logging.INFO,
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        self.main_path = os.getcwd()
        self.directory_names = ["srt_raw","srt_trans"]
        self.directory_path = []
        for  dir in self.directory_names:
            self.create_directory(dir)
            
        self.root = tk.Tk()
        self.root.withdraw()
        self.file_path = None
        
        # variabili per la UI
        self.timer=""
        self.err_message=""
        self.proced_file=""
        
        # contatore per raggiungere il massimo di richiste giornaliere 
        self.g_rpd=0
        self.path_srt=None

        self.update_event = threading.Event()
        
    
    def reset_timer(self):
        self.timer=""
        self.update_event.clear()
    
    def reset_err_message(self):
        self.err_message=""
        self.update_event.clear()
    
    def token_counter(self,file):
        tokenizer = tokenization.get_tokenizer_for_model(MODEL_NAME)
        result = tokenizer.count_tokens(file)
        return int(result.total_tokens)
     

        
    def create_directory(self,directory_name):
        try:
            if os.path.exists(directory_name):
                dir_path = os.path.abspath(os.path.join(self.main_path, directory_name))
                self.logger.info(f"Cartella  {directory_name} esistente path='{dir_path}")
                self.directory_path.append({"id":directory_name,"path":dir_path})
            else:
                os.makedirs(directory_name)
                dir_path = os.path.abspath(os.path.join(self.main_path, directory_name))
                self.logger.info(f"Cartella {directory_name} creata path='{dir_path}")
                self.directory_path.append({"id":directory_name,"path":dir_path})
            
        except Exception as e:
            self.logger.info(f"Errore cartelle: {str(e)}")
            self.err_message=f"Errore cartelle: {str(e)}"
            self.update_event.set()
   
    

    def translate_text(self,text,index,file):
        genai.configure(api_key=key)
        try:
            message=f"{text}\n{prompt}"
            
            # Create the model
            generation_config = {
            "temperature": 1,
            "top_p": 0.95,
            "top_k": 64,
            "max_output_tokens": 8192,
            "response_mime_type": "text/plain",
            }
            
            safety_settings : list[str] = [{"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}]

            model = genai.GenerativeModel(
            model_name="gemini-1.5-pro",
            generation_config=generation_config,
            safety_settings=safety_settings
            # See https://ai.google.dev/gemini-api/docs/safety-settings
            )

            chat_session = model.start_chat(
            history=[
            ]
            )
            
            self.logger.info(f"Parte srt {index+1} file {file} Inzio Traduzione ")
            self.logger.info(f"Parte srt {index+1} file {file} numero token {self.token_counter(message)}")
            response = chat_session.send_message(f"{message}")
            self.logger.info(f"Parte srt {index+1} file {file}  Tradotta ")
            self.logger.info(f"Parte srt {index+1} file {file} numero token {self.token_counter(response.text)}")
            return response.text

            
        except Exception as e:
            self.logger.info(f"Errore traduzione file  : {str(e)}")
            self.err_message=f"Errore traduzione file  : {str(e)}"
            self.update_event.set()

    def scrivi_file(self,file_path,data):
        try:
            with open(file_path,"w",encoding='utf-8') as file:
                for index,srt in enumerate(data):
                    file.write(srt)
                    self.logger.info(f"Scritta parte {index+1} file {file_path}")  
        except Exception as e:
            self.logger.info(f"Errore scrittura file: {str(e)}")
            self.err_message=f"Errore scrittura file: {str(e)}"
            self.update_event.set()

    def select_srt_files(self):
        # Apri una finestra di dialogo per selezionare i file .srt
        file_paths = filedialog.askopenfilenames(filetypes=[("SRT Files", "*.srt")])
        
        if not file_paths:
            self.logger.info("Nessun file srt selezionato.")
            self.err_message="Nessun file srt selezionato."
        else:
            try:
                for file in file_paths:
                    self.file_path = file    
                    self.logger.info(f"SRT selezionato: {self.file_path}")
                    shutil.copy2(self.file_path, self.directory_names[0])
                    self.logger.info(f"File copiato nella cartella: {self.directory_names[0]}")
            except Exception as e:
                self.logger.error(f"copia Fallita: {str(e)}")
                self.err_message=f"copia Fallita: {str(e)}"
                self.update_event.set()
    
    
    
    def split_srt_file(self,input_file):
        try:
            # Leggi il file SRT
            subs = pysrt.open(input_file)
            self.path_srt=input_file
            
            # Calcola il numero di righe per parte
            rows_per_part,num_parts = select_rows_per_part(len(subs))
            
            # Inizializza una lista per le parti
            parts = []
            
            # Dividi il file in parti uguali
            for i in range(num_parts):
                start_index = i * rows_per_part
                end_index = min((i + 1) * rows_per_part, len(subs))
                
                part = subs[start_index:end_index]
                part_str = '\n'.join(str(sub) for sub in part)
                
                parts.append(part_str)
            for index,part in enumerate(parts):
                self.logger.info(f"Parte srt {index+1} file {input_file} numero token {self.token_counter(part)}")
            return parts
            
        except Exception as e:
            self.logger.info(f"Errore divisione file : {str(e)}")
            self.err_message=f"Errore divisione file : {str(e)}"
            self.update_event.set()
    
    def get_file_names(self,directory):
        return [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
    
    def translates_srt_files(Self):
        try:
            Self.reset_err_message()
            Self.reset_timer()
            file_names_l = Self.get_file_names(Self.directory_path[0]['path'])
            next_request=0
            if next_request<=(MAX_REQUEST-Self.g_rpd):
                for file in file_names_l:
                    translated_file = []
                    parts =  Self.split_srt_file(formated_initial_path(Self.directory_path[0]['path'],file))
                    next_request= len(parts)
                    for  index, part in enumerate(parts):
                        translated_part = Self.translate_text(part,index,file)
                        Self.g_rpd+=1
                        translated_file.append(translated_part)
                        sleep(TIME_OUT)
                    final_file_name = formated_final_path(Self.directory_path[1]['path'],file)
                    Self.scrivi_file(final_file_name,translated_file)
                    Self.proced_file=f"File tradotto e salvato {final_file_name}"
            else:
                Self.logger.info(f"Massimo rpd({MAX_REQUEST}) giornaliero raggiunto")
                Self.err_message=f"Massimo rpd({MAX_REQUEST}) giornaliero raggiunto"
            Self.update_event.set()
                    
        except Exception as e:
            Self.logger.info(f"Errore processo di traduzione: {str(e)}")
            Self.err_message=f"Errore processo di traduzione: {str(e)}"
            Self.update_event.set()



