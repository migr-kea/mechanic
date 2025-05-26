import os
import shutil
from datetime import datetime

#Skift disse stier til dine egne:
kilde_fil = 'noter.csv'           #Din datafil (fx CSV eller SQLite DB)
backupmappe = 'backup'                 #Mappen hvor backupfiler skal ligge

#Lav backupnavn med dato og tid
dato = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
backup_filnavn = f"{dato}_{kilde_fil}"
backup_sti = os.path.join(backupmappe, backup_filnavn)

# 🗂 Opret backupmappen hvis den ikke findes
os.makedirs(backupmappe, exist_ok=True)

#Kopiér filen til backupmappen
shutil.copy2(kilde_fil, backup_sti)

print(f"Backup gemt som: {backup_sti}")
