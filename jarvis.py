#!/usr/bin/env python3

# - *- coding: utf - 8 - *-

import os, sys, datetime, glob, http.client, urllib.parse, requests, subprocess, spur, telepot, json

# Ruta desde donde se ejecuta el script
DIR_SCRIPT_PATH = os.path.dirname(os.path.abspath(__file__))


## Web ##

# Servicios Web #
def servicesWeb():
	## Linea/bloque editable ##

	# Url de cada servicio web(paginas)
	urls = ["http://modelos.insmet.cu", "http://modelos.insmet.cu:6175", "http://rcm.insmet.cu"]

	## Linea/bloque editable ##


	line = ''	
	
	with open(DIR_SCRIPT_PATH + "/report.txt", "w") as file:
		file.write("------------------------------\n")
		file.write("Servicios Web:\n\n")
		
		# chequear si cada servicio web esta online
		for url in urls:
			if check_url(url):
				line = url + ": ONLINE"
			else:
				line = url + ": OFFLINE"
				
			file.write(line + "\n")
			
		file.write("------------------------------\n")
		
		
# Espacio disponible Web-PC #
def dataWeb():
	## Linea/bloque editable ##

	# Direccion base de los datos de la pagina web
	base_dir = '/var/www/html/INSMET-webs/models/static/models/'
	
	# Directorios
	file_dirs = ["ARW_POST", "plots"]
	
	# Proyectos
	project_dirs = ["sispi", "spnoa"]

	## Linea/bloque editable ##


	# chequear cada directorio
	for file_ in file_dirs:
		# por cada proyecto
		for project_ in project_dirs:
			
			# rutas de los directorios de los datos
			project_dir = base_dir + file_ + "/" + project_ + "/"
            
			# limpiar los directorios de los datos(si hay mas de 6 plazos)			
			if file_ == "ARW_POST":
				cleanDirectories("", project_dir)
				
			if file_ == "plots" and project_ == "sispi":
				cleanDirectories("wrfout_", project_dir)
				cleanDirectories("wrfout-2_", project_dir)
			
			if file_ == "plots" and project_ == "spnoa":
				cleanDirectories("wrfout_", project_dir)
				cleanDirectories("spnoa_", project_dir)


## Clusters ##

# Clusters online #
def servicesClusters():
	## Linea/bloque editable ##

	# Ips de cada cluster (PCs) con sus nodos (si tienen)
	ips = {
		'10.0.10.120' : {
			'hosts' : ['node01', 'node03']
		},			
		'10.0.10.121' : {
			'host' : ['node01', 'node02', 'node03', 'node04'],
		},
		'10.0.100.219' : {
			'hosts' : []
		},
	}

	## Linea/bloque editable ##


	line = ''
	
	
	with open(DIR_SCRIPT_PATH + "/report.txt", "a") as file:
		file.write("------------------------------\n")
		file.write("Servicios Clusters:\n\n")
		
		# chequear si cada cluster esta online
		for ip, value in list(ips.items()):
			for hosts in list(value.values()):
				
				# chequear la cabecera
				response = subprocess.getstatusoutput("ping " + ip + " -c 1")[0]
			
				if response == 0:
					line = ip + ": ONLINE"
					file.write(line + "\n")
					
					# chequear los nodos
					if len(hosts) > 0:
						nodesCluster(ip, hosts, file)
					
				else:
					line = ip + ": OFFLINE"
					file.write(line + "\n")
				
			file.write("\n")
			
		file.write("------------------------------\n")


# Espacio disponible Clusters #
def dataClusters():
	## Linea/bloque editable ##

	# Ips de cada cluster (PCs) con las rutas de directorios a
	# chequear de una PC determinada, empezando por el directorio raiz
	ips = {
		'10.0.10.120' : {
			'dirs' : [
				'/opt', 
				'/opt/data/CIMO2CLUSTER', 
				'/opt/productos', 
				'/opt/sispi/OUTPUTS_1W/outputs'
			]
		},
		'10.0.10.121' : {
			'dirs' : [
				'/opt', 
				'/opt/data/CIMO2CLUSTER', 
				'/opt/descargas_electricas/rayos', 
				'/opt/insmet.cu', 
				'/opt/insmet.cu/spnoa2ascii', 
				'/opt/sispi/OUTPUTS_1W/outputs', 
				'/opt/spnoa/OUTPUTS_1W/outputs',
				'/opt/spnoa/OUTPUTS_1W/SWAN_Work', 
				'/opt/spnoa/OUTPUTS_1W/WW3_Work'
			]
		},
	}
	
	# Usuario generico
	user = "cluster"

	## Linea/bloque editable ##


	with open(DIR_SCRIPT_PATH + "/report.txt", "a") as file:
		file.write("------------------------------\n")
		file.write("Espacio disponible en disco:\n\n")
		
		for ip, value in list(ips.items()):
			dirs = list(value.values())[0]
			checkDirectories(ip, user, dirs, file)
			
			file.write("------------------------------\n")


# Chequear directorio de datos GFS
def gfsCluster():
	## Linea/bloque editable ##

	# Ips de cada cluster (PCs) con la ruta de los datos GFS
	ips = {
		'10.0.10.120' : {
			'gfs' : '/opt/data/CIMO2CLUSTER'
		},
		'10.0.10.121' : {
			'gfs' : '/opt/data/CIMO2CLUSTER'
		},
	}
	
	# Usuario generico
	user = "cluster"

	## Linea/bloque editable ##


	# fecha actual
	date = dateFormat(datetime.datetime.now())

	gfs_folders = []
	
	with open(DIR_SCRIPT_PATH + "/report.txt", "a") as file:
		file.write("------------------------------\n")	
		file.write("Datos GFS descargados:\n\n")
		
		for ip, value in list(ips.items()):
			for gfs_dir in list(value.values()):
				
				file.write("<" + ip + ">\n\n")
				
				# rutas de los directorios GFS
				cmd = subprocess.Popen("ssh " + user + "@" + ip + " ls -d " + gfs_dir + "/" + date + "*", shell=True, stdin=None, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
				lines = cmd.stdout.readlines()
				
				# directorios GFS
				for line in lines:
					gfs_folders.append(line.decode().split(gfs_dir)[1].rstrip('\n'))
				
				# invertir el orden de manera descendente (por fecha)
				gfs_folders.sort(reverse=True)
				
				# chequear que existan directorios
				if len(gfs_folders) > 0:
					
					for i in range(len(gfs_folders)):				
						# fichero "dataready" indica que los datos del plazo fueron descargados correctamente
						ready = (gfs_dir + gfs_folders[i]) + "/" + "dataready"
						
						# chequear si exite el fichero dataready
						if subprocess.getstatusoutput("ssh " + user + "@" + ip + ' ls -h ' + ready + "*")[0] == 0:
							file.write(" " + gfs_folders[i] + "--listo\n")
						else:
							file.write(" " + gfs_folders[i] + "--incompleto\n")
				else:
					file.write(" --no hay datos\n")
				
				# limpiar array de directorios para la proxma interacion
				gfs_folders = []
				file.write("\n")
				
		file.write("------------------------------\n")


## Funciones auxiliares ##

# Checkear que exista la url a guardar
def check_url(url):
    # Comprobar si la pagina esta online (codigo http 200) o si existe algun error en el servidor (codigo http 400 a 600)
    return get_server_status_code(url) not in list(range(400, 600))


# Obtener respuesta del estatus del servidor web
def get_server_status_code(url):
	# Devolver el codigo de estado de la pagina web.	
	try:		
		r = requests.get(url)
		status = r.status_code
		
		return status
		
	except requests.exceptions.RequestException as e:
		
		raise SystemExit(e)


# Eliminar por etiqueta (PC web)
def cleanDirectories(label, project_dir):
	## Linea/bloque editable ##

	# Ips de la PC web (paginas)
	ip = "10.0.100.219"
	
	# Usuario generico
	user = "webs-pc"

	## Linea/bloque editable ##


	# lista de rutas de los directorios de los datos
	cmd = subprocess.Popen("ssh " + user + "@" + ip + " ls -d " + project_dir + label + "*", shell=True, stdin=None, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	lines = cmd.stdout.readlines()
	
	dirs = []
	
	# directorios de los datos
	for line in lines:
		dirs.append(line.decode().split(project_dir)[1])
		
	# invertir el orden de manera descendente (por fecha)
	dirs.sort(reverse=True)
	
	# chequear si hay mas de 6 directorios
	for i in range(len(dirs)):
		if i > 5:
			os.system("ssh " + user + "@" + ip + " rm -fr " + project_dir + dirs[i])


# Chequear nodos online #
def nodesCluster(ip, hosts, file):
	## Linea/bloque editable ##
	
	# Usuario generico
	user = "cluster"
	
	## Linea/bloque editable ##
	
	
	line = ''
	
	shell = spur.SshShell(hostname=ip, username=user)
	
	for host in hosts:
		try:
			
			response = shell.run(['ping', host, '-c 1'])
			
			if response.return_code == 0:
				line = "\t" + host + ": ONLINE"
				homeNode(shell, host, file)
			else:
				line =  "\t" + host + ": OFFLINE"
				
		except spur.RunProcessError as error:
			
			line =  "\t" + host + ": OFFLINE"
		file.write(line + "\n")


# Chequear home montado en el nodo #
def homeNode(shell, host, file):
	node = shell.run(['ssh', host, 'mountpoint', '-q', '/home'])

	if node.return_code != 0:
		file.write("\t </home> no MONTADO")


# Chequear espacio en disco de directorios
def checkDirectories(ip, user, dirs, file):
	# imprimir ip de la PC
	file.write("<" + ip + ">\n\n")
	
	# reporte general del directorio	
	size = subprocess.Popen("ssh " + user + "@" + ip +" df -m --output=size " + dirs[0], shell=True, stdin=None, stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout.readlines()[1]
	used = subprocess.Popen("ssh " + user + "@" + ip +" df -m --output=used " + dirs[0], shell=True, stdin=None, stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout.readlines()[1]
	avail = subprocess.Popen("ssh " + user + "@" + ip +" df -m --output=avail " + dirs[0], shell=True, stdin=None, stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout.readlines()[1]
	pcent = subprocess.Popen("ssh " + user + "@" + ip + " df --output=pcent " + dirs[0], shell=True, stdin=None, stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout.readlines()[1]
	
	cadena = " Total: {:.1f}G\n Usado: {:.1f}G\n Disponible: {:.1f}G\n Usado%: {}"
	file.write("Directorio Raiz: " + dirs[0] + "\n\n")
	file.write(cadena.format(to_gb(size), to_gb(used), to_gb(avail), pcent.decode()))
	file.write("\n")
	
	# reporte de los subdirectorios mas grandes (criticos)
	file.write("Subdirectorios criticos:\n\n")
	file.write(" total(G) \t<directorio>\t usado(%)\n")
	
	for i in range(len(dirs)):
		if i > 0:
			total_subdir = to_gb((os.popen("ssh " + user + "@" + ip + " du -m --summarize " + dirs[i]).read().split(dirs[i])[0]).rstrip('\t'))
			percent_subdir = ((total_subdir / to_gb(size)) * 100)
			cadena = "{:.1f}G \t{}\t {:.1f} %"
			file.write(" " + cadena.format(total_subdir, dirs[i], percent_subdir))
			file.write("\n")
	
	lines = []
	
	# reporte de todos los subdirectorios
	file.write("Resumen subdirectorios\n\n")
	file.write(" total(G)\t <directorio>\n")
	cmd = subprocess.Popen("ssh " + user + "@" + ip + " du -sh " + "'" + dirs[0] + "/*" + "'", shell=True, stdin=None, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	lines = cmd.stdout.readlines()
	
	for line in lines:
		file.write(" " + line.decode())
	file.write("\n")


# Convertir megabytes a gigabytes
def to_gb(mbytes):
	return float(mbytes) * (1024.0 / 1024.0 ** 2)


# Convertir formato fecha
def dateFormat(date):	
	# formato de fecha YYYYMMDDHH
	year = date.strftime('%Y')
	month = date.strftime('%m')
	day = date.strftime('%d')
	date_format = year + month + day
	
	return date_format


# Configuraciones proxy
def proxyConfig():
	proxyconf=os.getenv("http_proxy")
	proxyconf=open(os.path.expanduser(DIR_SCRIPT_PATH + '/proxy'),'r').read().strip('\n')

	if proxyconf != None:
		proxy_user=proxyconf.split(":")[1].strip("//")
		proxy_pass=proxyconf.split(":")[2].split("@")[0]
		proxy_url="http://"+proxyconf.split("@")[1]


# Enviar reporte sin proxy
def sendReport(report):
	credentials=json.load(open(os.path.expanduser(DIR_SCRIPT_PATH + "/" + "credentials.json"), 'r'))
	bot=telepot.Bot(credentials['Telegram Bot Token'])
	file = open(report,'rb')
	bot.sendDocument(-495336441, file)


def run():
	# Hora de ejecucion del script
	hour = datetime.datetime.now().strftime('%H')

	# Configuraciones proxy para el environment de crontab
	proxyConfig()
	
	# Servicios web onlines
	servicesWeb()
	
	# Limpiar datos de sispy web
	if hour == '06':
		dataWeb()
	
	# Clusters online
	servicesClusters()
	
	# Chequear datos GFS
	if hour == '02' or hour == '08' or hour == '14' or hour == '20':
		gfsCluster()
	
	# Chequear espacio disponible en los clusters
	if hour == '06':
		dataClusters()
	
	# Enviar reporte sin proxy
	report = DIR_SCRIPT_PATH + "/report.txt"
	#sendReport(report)
	
	# Enviar reporte con proxy
	try:
		os.system(DIR_SCRIPT_PATH + "/" + "jodo " + "python3 " + DIR_SCRIPT_PATH + "/" + "sendReport.py")
	except:
		#print ("Fallo al publicar en Telegram")
		with open(report, "a") as file:
			file.write("------------------------------\n")
			file.write("**Fallo al publicar el reporte en Telegram**\n\n")
			file.write("------------------------------\n")



#Ejecutar script
run()
