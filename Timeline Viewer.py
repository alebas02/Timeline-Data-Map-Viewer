import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import webview
import webview.menu as wm
import json
import folium
import folium.plugins as plugins
import os

risultati = []  # Lista che conterrà elementi del file .json letto 

# Funzione per trovare tutti i valori associati a una ad una determinata chiave specifica nel file .json
def trova_tutti_i_valori(data):
    global risultati 
    risultati.clear()  # Svuoto la lista prima di caricarla
    
    #print("\nstampo risultati alla chiamata di trova_tutti...: ", risultati)
    #print("\n\n")

    # Itero su 'semanticSegments' e verifica la presenza di 'timelinePath'
    if "semanticSegments" in data:
        i = 0
        for segment in data["semanticSegments"]:
            #start_time = segment["startTime"]
            if "visit" in segment:
                lat, lon = data["semanticSegments"][i]["visit"]["topCandidate"]["placeLocation"]["latLng"].replace('Â°', '').split(", ")
                risultati.append([segment["startTime"],float(lat), float(lon)]) 
            elif "timelinePath" in segment:  # Controlla se 'timelinePath' è presente
                    #print("vero")
                    for entry in segment["timelinePath"]:
                        #print("valori trovati nel file:", entry)
                        lat, lon = entry["point"].replace('Â°', '').split(", ")
                        risultati.append([entry["time"],float(lat), float(lon)]) 
                #valori.append(segment)      
            i = i + 1
        return 1            # Ritorno 1 se è stato letto un file JSON con formato corretto
            
    else:
        messagebox.showerror("Errore apertura del file", "Il file aperto non possiede un formato corretto")
        return 0    # Ritorno 1 se è stato letto un file JSON con formato non corretto

# Carica il file JSON
def apri_file():
    #print("Ciao")
    global combobox
    global risultati
    global pulsante_ApriMappa
    global label2
    date = []   # Lista che conterrà le date estratte dai timestamp

    file_path = filedialog.askopenfilename(
        title="Seleziona un file JSON",
        filetypes=[("File JSON", "*.json")]
    )

    #print("\npercorso del file: "+ file_path+ "\n")

    if file_path:  # Se un file è stato selezionato
        with open(file_path, 'r') as file:          # Apro e leggo il file JSON
            try:
                data = json.load(file)
                #print("file aperto\n\n")
                #label.configure(text=f"File selezionato dal percorso: {file_path}")  # Aggiorna l'etichetta

                if trova_tutti_i_valori(data) == 1:     # Se è stato aperto un file sintatticamente corretto allora procedo
                    date.clear()
                    valore_precedente = ""  # Definisco il valore precedente come una stringa vuota
                    for i, valore in enumerate(risultati):
                        #print("iterazione: ",i, "valore precedente: ", valore_precedente)
                        if valore[0].split('T')[0] != valore_precedente:    # Estraggo solo la data dal primo elemento (timestamp) di ogni tupla di risultati 
                            date.append(valore[0].split('T')[0])            # Inserisco valore nella lista date solo se il valore attuale è diverso dal precedente
                        valore_precedente = valore [0].split('T')[0]        # Assegno al valore precedente il valore attuale 

                    # Nascondo la label
                    label.pack_forget()

                    label2 = ttk.Label(app, text="Seleziona una data per visualizzarne gli spostamenti")
                    label2.pack(pady=20)  # Aggiungi padding verticale per centrare meglio la label

                    # Creazione del ComboBox con scrollbar
                    combobox = ttk.Combobox(app, values=date)
                    combobox.set(date[0])  # Imposto nella ComboBox il valore iniziale

                    # Aggiungo il ComboBox alla finestra con un layout manager
                    combobox.pack(pady=10, padx=20)

                    # Aggiungo un pulsante per selezionare il file
                    pulsante_ApriMappa = ttk.Button(app, text="Apri mappa", state="normal", command=apri_mappa)
                    pulsante_ApriMappa.pack(pady=20)
                    
                    
                    file_menu.entryconfig("Apri", state="disabled")         # Una volta che il file è aperto disabilito l'opzione di apertare di un file
                    file_menu.add_separator()                               # Aggiungo una linea di separazione
                    file_menu.add_command(label="Chiudi", command=chiudi)   # Aggiungo una voce per chiudere il file attualmente aperto    


            except json.JSONDecodeError:
                #print("Errore nella lettura del file JSON.")
                messagebox.showerror("Errore apertura del file", "Il file aperto non possiede un formato corretto")

    
     

# Funzione per avviare la finestra di pywebview
def apri_mappa():
    
    global mappa
    global risultati    

    lista_timestamp_filtrata = []                           # Lista che conterrà solo i timestamp che equivalgono alla data selezionata dall'utente nella ComboBox  
    lista_coordinate_filtrata = []                          # Lista che conterrà solo le coordinae che appartengono alla data selezionata dall'utente nella ComboBox  
    
    #print("la lista delle coordinate è:", lista_coordinate)
    #print("la lista dei timestamp è: " , lista_timestamp)
    opzione_combobox = combobox.get()  # Salvo il valore selezionato dall'utente sulla ComboBox
    #print(f"Opzione selezionata: {opzione_combobox}")

    # Carico le liste filtrare 
    i = 0
    while (i < len(risultati)):
        if opzione_combobox == risultati[i][0].split('T')[0] : 
            lista_timestamp_filtrata.append(risultati[i][0])
            lista_coordinate_filtrata.append([risultati[i][1],risultati[i][2]])
        i = i+1
    
    #print("la lista delle coordinate filtrata è:", lista_coordinate_filtrata)
    #print("la lista dei timestamp filtrata è: " , lista_timestamp_filtrata)

    data_string = lista_timestamp_filtrata[0]      # Assegno il primo timestamp presente nella lista dei timestamp 

    #print("data del primo timestamp", data_string)

    # Crea la mappa centrata su una posizione specifica
    mappa = folium.Map(location= lista_coordinate_filtrata[0], zoom_start=25) # Creo la mappa con zoom sulla prima coordinate individuata
    
    # Aggiungo il primo marker di colore verde prendendo la coordinata dalla lista
    folium.Marker(
        location = lista_coordinate_filtrata[0],
        icon=plugins.BeautifyIcon(          # https://github.com/masajid390/BeautifyMarker
            icon="arrow-down", icon_shape="marker", 
            icon_size=(40,40),
            number= 1,
            inner_icon_style="font-size:20px;",
            #text_color= "green",
            border_color= "black",
            borderWidth = 2,
            background_color="green", 
        ),
        tooltip='Punto n. 1<br>Ora: ' + data_string[11:16] + '<br>Latitudine: '+ str(lista_coordinate_filtrata[0][0]) +'<br>Longitudine: '+ str(lista_coordinate_filtrata[0][1]),  # Estrazione dell'orario "HH:mm" dal timestamp della prima coordinata
    ).add_to(mappa)
   
    # Aggiungi i marker successivi di colore arancione alla mappa
    i = 1 
    while i < len(lista_coordinate_filtrata):
        data_string = lista_timestamp_filtrata[i]
        folium.Marker(
            location = lista_coordinate_filtrata[i],
            icon=plugins.BeautifyIcon(          # https://github.com/masajid390/BeautifyMarker
            icon="arrow-down", icon_shape="marker", 
            icon_size=(30,30),
            number= i+1,
            inner_icon_style="font-size:15px;",
            #text_color= "green",
            border_color= "black",
            borderWidth = 2,
            background_color="orange", 
        ),
            tooltip='Punto n. ' +str(i+1) +'<br>Ora: ' + data_string[11:16] + '<br>Latitudine: '+ str(lista_coordinate_filtrata[i][0]) +'<br>Longitudine: '+ str(lista_coordinate_filtrata[i][1]),
            ).add_to(mappa)
        i = i+1  
        
    # Aggiungi ultimo marker di colore rosso alla mappa
    folium.Marker(
            location = lista_coordinate_filtrata[i-1],
            icon=plugins.BeautifyIcon(          
            icon="arrow-down", icon_shape="marker", 
            icon_size=(40,40),
            number= i,
            inner_icon_style="font-size:20px;",
            #text_color= "green",
            border_color= "black",
            borderWidth = 2,
            background_color="red", 
        ),
            tooltip='Punto n. ' +str(i) +'<br>Ora: ' + data_string[11:16] + '<br>Latitudine: '+ str(lista_coordinate_filtrata[i-1][0]) +'<br>Longitudine: '+ str(lista_coordinate_filtrata[i-1][1]),
            #tooltip='Ora: '+lista_timestamp[i-1],  #str(i) perchè non posso concatenare intero ma solo stringhe quindi faccio cast
        ).add_to(mappa)
    folium.PolyLine(lista_coordinate_filtrata, color='red').add_to(mappa)   # Crea un tracciato degli spostamenti dell'utente
    
    # Salve la mappa nella cartella di questo codice sorgente
    mappa.save(os.path.join(os.path.dirname(__file__), "mappa_con_marker.html"))

    # Definisco un Menu di nome File che conterrà la voce salva per salvare la mappa attualmente aperta dall'utente
    menu_items = [
        wm.Menu('File ', [wm.MenuAction('Salva', salva_html)]),
    ]
     
    # Creo una finestra che mi apre la mappa
    webview.create_window("Visualizzatore di Mappe", os.path.join(os.path.dirname(__file__), "mappa_con_marker.html"))
    webview.start(menu=menu_items)  # Passo il menù alla finestra contenente la mappa
    os.remove(os.path.join(os.path.dirname(__file__), "mappa_con_marker.html"))  # Rimuovo la mappa dalla cartella

def salva_html():    # Funzione richiamata nel momento in cui l'utente seleziona la voce Salva 
    mappa.save(os.path.join(os.path.dirname(__file__), combobox.get() + ".html"))   # Salvo la mappa con nome della data selezionata dall'utente sulla ComboBox nella cartella di questo codice sorgente
        
def chiudi():
    label2.pack_forget()                                                # Rimuovo label 2
    label.pack(pady = 80)                                               # Visualizzato label 
    pulsante_ApriMappa.pack_forget()                                    # Rimuovo pulsante per aprire la mappa
    combobox.pack_forget()                                              # Rimuovo ComboBox
    file_menu.delete("Chiudi")                                          # Rimuovo voce "Chiudi" dal menu "File"
    file_menu.delete(1)                 
    file_menu.entryconfig("Apri", state="normal")   # Mostro voce "Apri" del menu "File"

def esci():
    if messagebox.askokcancel("Esci", "Confermi di uscire dal programma?"):
        app.destroy()
# Inizializza la finestra principale
app = tk.Tk()
app.title("Seleziona un file JSON")
app.geometry("500x250")
app.protocol("WM_DELETE_WINDOW", esci)

# Crea una label e aggiungila alla schermata
label = ttk.Label(app, text="Apri un file JSON da analizzare")
label.pack(pady=80)  # Aggiungi padding verticale per centrare meglio la label


menubar = tk.Menu(app)

#sottomenu
file_menu = tk.Menu(menubar, tearoff = False)
file_menu.add_command(label ='Apri', command = apri_file)

# Aggiungi il menu "File" alla barra dei menu
menubar.add_cascade(label="File", menu=file_menu)

# Configura la barra dei menu nella finestra principale
app.config(menu=menubar)

# Avvia l'applicazione
app.mainloop()


