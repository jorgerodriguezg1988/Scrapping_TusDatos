from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import time
import csv

def buscar_proceso(identificacion, input_id):
    driver = webdriver.Chrome()

    try:
        driver.get("https://procesosjudiciales.funcionjudicial.gob.ec/busqueda-filtros")
        WebDriverWait(driver, 8).until(
            EC.presence_of_element_located((By.ID, input_id))
        )

        # encuentra el mat-input
        input_field = driver.find_element(By.ID, input_id)
        
        # ingresa el proceso
        input_field.send_keys(identificacion)
        input_field.send_keys(Keys.RETURN)
        time.sleep(3)

        datos = []

        while True:
            # parse
            html = driver.page_source
            soup = BeautifulSoup(html, 'html.parser')

            # encuentra los elementos 'causa-individual'
            resultados = soup.find_all('div', class_='causa-individual')

            for resultado in resultados:
                id = resultado.find(class_='id').text.strip()
                fecha = resultado.find(class_='fecha').text.strip()
                identificacion = resultado.find(class_='numero-proceso').text.strip()
                accion_infraccion = resultado.find(class_='accion-infraccion').text.strip()
                detalle = resultado.find(class_='detalle').text.strip()

                datos.append([id, fecha, identificacion, accion_infraccion, detalle])

                print(f"{id}, {fecha, identificacion, accion_infraccion, detalle}")

            # verificar boton de pagina siguiente
            try:
                next_button = driver.find_element(By.CSS_SELECTOR, 'button.mat-mdc-paginator-navigation-next')
                if not next_button.is_enabled(): # habilitado?
                    break
                
                next_button.click()
                time.sleep(3)
            except:
                break

        return datos

    except Exception as e:
        print(f"Error: {e}")
        return []
    finally:
        driver.quit()
        
        
        
def buscar_detalle_proceso(numero_proceso, input_id, driver=None):
    datos = []

    try:
        if driver is None:
            driver = webdriver.Chrome()
       
        driver.get("https://procesosjudiciales.funcionjudicial.gob.ec/busqueda-filtros")
        
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.ID, input_id))
        )
        
        input_field = driver.find_element(By.ID, input_id)
        input_field.send_keys(numero_proceso)
        input_field.send_keys(Keys.RETURN) #enter
        time.sleep(2)        
        
        # clic en el icono del folder
        try:
            link_folder = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, f'//a[contains(@aria-label, "Vínculo para ingresar a los movimientos del proceso {numero_proceso}")]'))
            )
            link_folder.click()

            #print(f"clic en el folder {numero_proceso}")

        except Exception as e:
            print(f"No se pudo hacer clic en el folder: {e}")

        try:
            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CLASS_NAME, "lista-movimiento-individual"))
            )

            html = driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
            
            #print(f"numero de proceso: {numero_proceso}")
            #print("detalles del proceso:")
            
            movimientos = soup.find_all('div', class_='lista-movimiento-individual')
            for movimiento in movimientos:
                numero_incidente = movimiento.find(class_='numero-incidente').text.strip()
                fecha_ingreso = movimiento.find(class_='fecha-ingreso').text.strip()
                actores = movimiento.find(class_='lista-actores').text.strip()
                demandados = movimiento.find(class_='lista-demandados').text.strip()
               
                print(f"Numero de incidente: {numero_incidente}")
                print(f"Fecha de ingreso: {fecha_ingreso}")
                print(f"Actores: {actores}")
                print(f"Demandados: {demandados}")
                print("")
                
                datos.append([numero_proceso, numero_incidente, fecha_ingreso, actores, demandados])

            # pag principal
            driver.get("https://procesosjudiciales.funcionjudicial.gob.ec/busqueda-filtros")
            
            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.ID, input_id))
            )

            #print(f"regresa pag principal")
            
            time.sleep(3)

        except Exception as e:
            print(f"error al procesar detalles del proceso: {e}")

    except Exception as e:
        print(f"Ocurrio un error: {e}")

    return datos, driver  # navegador abierto continuamente

        
def exportar_a_csv(datos, nombre_archivo):
    with open(nombre_archivo, mode='w', newline='', encoding='utf-8') as archivo_csv:
        writer = csv.writer(archivo_csv)
        # titulos
        writer.writerow(['ID', 'Fecha', 'Numero de Proceso', 'Accion/Infraccion', 'Detalle'])
        # escribe los datos obtenidos en el .csv
        if datos:
            writer.writerows(datos)
            
def main():
    identificacion = "1791251237001"

    # buscar usando en el ofendido/mat-input-1
    datos_ofendido = buscar_proceso(identificacion, "mat-input-1")
    exportar_a_csv(datos_ofendido, f'ofendido_{identificacion}.csv')
    print(f"Datos exportados correctamente a ofendido_{identificacion}.csv")
    csv_ofendido = f"ofendido_{identificacion}.csv"
    #print(csv_ofendido)

    # buscar usando en el demandado/mat-input-3
    datos_demandado = buscar_proceso(identificacion, "mat-input-3")
    exportar_a_csv(datos_demandado, f'demandado_{identificacion}.csv')
    print(f"Datos exportados correctamente a demandado_{identificacion}.csv")
    csv_demandado = f"demandado_{identificacion}.csv"
    #print(csv_demandado)
    
    datos_detalle_ofendido = []  # Definir variable fuera del bucle
    datos_detalle_demandado = []  # Definir variable fuera del bucle
    
    with open(csv_ofendido, mode='r', newline='', encoding='utf-8') as archivo_csv:
        reader = csv.reader(archivo_csv)
        next(reader)  # omite la cabecera
        
        for row in reader:
            numero_proceso = row[2]  # columna 3 del csv
            print(numero_proceso)
            detalle_ofendido, driver = buscar_detalle_proceso(numero_proceso, "mat-input-0")
            datos_detalle_ofendido.extend(detalle_ofendido)  # Acumular los datos en la lista
            print(detalle_ofendido)
        exportar_a_csv(datos_detalle_ofendido, f'detalle_ofendido_{identificacion}.csv')
        print(f"Datos exportados correctamente")
            
    print("\n")        
    with open(csv_demandado, mode='r', newline='', encoding='utf-8') as archivo_csv:
        reader = csv.reader(archivo_csv)
        next(reader) # omite la cabecera
        
        for row in reader:
            numero_proceso = row[2]  # columna 3 del csv
            print(numero_proceso)
            detalle_demandado, driver = buscar_detalle_proceso(numero_proceso, "mat-input-0", driver)
            datos_detalle_demandado.extend(detalle_demandado)  # Acumular los datos en la lista
            print(detalle_demandado)
        exportar_a_csv(datos_detalle_demandado, f'detalle_demandado_{identificacion}.csv')
        print(f"Datos exportados correctamente")


if __name__ == "__main__":
    main()
