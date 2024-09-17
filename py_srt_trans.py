import os
import pysrt 
import google.generativeai as genai
import logging
from config import key,prompt
from math import ceil
from time import sleep
from google.generativeai.types import HarmCategory, HarmBlockThreshold

# TODO
# 1 Importare la chiave,il prompt , cosa tradurre e google-gemini V
# 2 Dividere il file in sotto file V
# 3 mandare il prompt più la parte da tradurre V
# 4 unire le parti e scriverle in un nuovo file V
# 5 creare una classe V
# 5.1 crea un file requisiti V
# 6 creare un file unico per chiave,propmt V
# 7 creare una UI

TIME_OUT: int = 120
def get_file_names(directory):
    return [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]

def formated_final_path(directory,name):
    new_name =  name.split('.')[0] + '_translated.' + name.split('.')[1]
    return f"{directory}/{new_name}"

def formated_initial_path(directory,name):
    return f"{directory}/{name}"

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
   
    

    def translate_text(self,text,index,file):
        genai.configure(api_key=key)
        try:
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
            response = chat_session.send_message(f"{prompt}\n{text}")
            self.logger.info(f"Parte srt {index+1} file {file}  Tradotta ")
            return response.text

            
        except Exception as e:
            self.logger.info(f"Errore traduzione file  : {str(e)}")

    def scrivi_file(self,file_path,data):
        try:
            with open(file_path,"w",encoding='utf-8') as file:
                for index,srt in enumerate(data):
                    file.write(srt)
                    self.logger.info(f"Scritta parte {index+1} file {file_path}")
                     
        except Exception as e:
            self.logger.info(f"Errore scrittura file: {str(e)}")

    def split_srt_file(self,input_file, num_parts=3):
        try:
            # Leggi il file SRT
            subs = pysrt.open(input_file)
            
            # Calcola il numero di righe per parte
            rows_per_part = ceil(len(subs) / num_parts)
            
            # Inizializza una lista per le parti
            parts = []
            
            # Dividi il file in parti uguali
            for i in range(num_parts):
                start_index = i * rows_per_part
                end_index = min((i + 1) * rows_per_part, len(subs))
                
                part = subs[start_index:end_index]
                part_str = '\n'.join(str(sub) for sub in part)
                
                parts.append(part_str)
            
            return parts
        except Exception as e:
            self.logger.info(f"Errore divisione file : {str(e)}")
    
    def translates_srt_files(Self):
        try:
            file_names_l = get_file_names(Self.directory_path[0]['path'])
            for file in file_names_l:
                translated_file = []
                parts =  Self.split_srt_file(formated_initial_path(Self.directory_path[0]['path'],file))
                for  index, part in enumerate(parts):
                    translated_part = Self.translate_text(part,index,file)
                    translated_file.append(translated_part)
                final_file_name = formated_final_path(Self.directory_path[1]['path'],file)
                Self.scrivi_file(final_file_name,translated_file)
                Self.logger.info(f"Time Out : {TIME_OUT}s")
                sleep(TIME_OUT)
                    
        except Exception as e:
            Self.logger.info(f"Errore processo di traduzione: {str(e)}")



