import csv

userdata = dict()
books = list()
userperbook = dict()
comunBook = set()
#PROCESAR ARCHIVOS
# @profile
def ProcessFiles():
	global books
	with open('db/BX-Book-Ratings.csv', 'rb') as f:
		reader = csv.reader(f,delimiter=';')
		book_ratings = list(reader)
	del book_ratings[0]
	for user_id,isbn,rating in book_ratings:
		if(user_id in userdata):
			userdata[user_id][isbn] = rating
		else:
			userdata[user_id] = dict()
			userdata[user_id][isbn] = rating
		if(isbn in userperbook):
			userperbook[isbn].append(user_id)
		else:
			userperbook[isbn] = list()
			userperbook[isbn].append(user_id)
	print 'userdata en RAM'

	with open('db/BX-Books.csv', 'rb') as f:
		reader = csv.reader(f,delimiter=';')
		books = list(reader)
	del books[0]
	#['ISBN', 'Book-Title', 'Book-Author', 'Year-Of-Publication', 'Publisher', 'Image-URL-S', 'Image-URL-M', 'Image-URL-L']
	print 'Libros en RAM'

def PromedioRating(diccionario):
	prom = 0
	cantidad = 0
	for isbn,rating in diccionario.items():
		prom+=int(rating)
		cantidad+=1
	return float(prom/cantidad)

# @profile
def Similares(iduser):
	global userdata,comunBook
	comun = list() # ['234274982', '2323X233',...]
	ratingsMedia = dict() # {'user': 5.3, 'user2': 4.2...}
	correlacion = dict() # {'user': 0.4443, 'user2': .323...} Solo guarda sobre 0
	def comun(u1,u2):
		u1 = set(userdata[u1])
		u2 = set(userdata[u2])
		return  u1 & u2
	def r(uid,libro):
		return float(userdata[uid][libro])
	for user,data in userdata.items():
		# print data
		ratingsMedia[user] = PromedioRating(data)
	print "ratingsMedia obtenida\n"
	def corr(iduser,u2):
		iduser = str(iduser)
		u2 = str(u2)
		dominio = comun(iduser,u2)
		s1 = 0
		s2 = 0
		s3 = 0
		if(dominio):
			for libro in dominio:
				s1+=(r(iduser,libro)-ratingsMedia[iduser])**2
				s2+=(r(u2,libro)-ratingsMedia[u2])**2
				s3+=(r(iduser,libro)-ratingsMedia[iduser])*(r(u2,libro)-ratingsMedia[u2])
			if(s2 == 0.0 or s1 == 0.0):
				calculo = 0
			else:
				calculo = s3/( ( (s1)**.5 )*( (s2)**.5 ) )
			return calculo
		else:
			return 0
	for uid in userdata:
		corre = corr(iduser,uid)
		if(corre != 0):
			correlacion[uid] = corr(iduser,uid)
			comunBook= comunBook.union(userdata[uid].keys())
	return correlacion

def AllRatingLibros(uid):
	uid = str(uid)
	global books,comunBook
	if uid not in userdata.keys():
		return []
	correlaciones = Similares(uid)
	print "Correlaciones Determinadas"
	ratings = list()
	def RatingL(libro):
		libro = str(libro)
		sumaT = 0
		sumaI = 0
		veces = 0
		for id2 in userperbook[libro]:
			if(id2 in correlaciones.keys()):
				veces+=1
				sumaT += correlaciones[id2]*int(userdata[id2][libro])
				sumaI += abs(correlaciones[id2])
		if(veces > 0):
			return float(float(sumaT)/sumaI)
		else:
			return 0
	for book in comunBook:
		if book not in userdata[uid].keys():
			if(RatingL(book) != 0):
				ratings.append((RatingL(book),book))
	ratings = sorted(ratings)[::-1]
	print "Rating por libros determinados"
	return ratings
	#[(7.0, '1881320189')...]
ProcessFiles()
def creartop(k,lista):
	print "Creando lista TOP"
	if(len(lista) == 0):
		print "No se han podido obtener recomendaciones para el usuario"
		return
	userdata = dict()
	comunBook = set()
	html=open("top.html","w")
	html.write('<!DOCTYPE html>\n')
	html.write('<html lang="es">\n')
	html.write('<head>\n')
	html.write('	<meta charset="UTF-8">\n')
	html.write('	<title>Tabla de Datos</title>\n')
	html.write('<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/font-awesome/4.4.0/css/font-awesome.min.css">')
	html.write('<link rel="stylesheet" type="text/css" href="animate.css">')
	html.write('<link rel="stylesheet" type="text/css" href="style.css">')
	html.write("<link href='https://fonts.googleapis.com/css?family=Open+Sans:400,700' rel='stylesheet' type='text/css'>")
	html.write('</head>\n')
	html.write('<body>\n')
	html.write('<h1>Libros recomendados</h1>')
	i=0
	html.write("<ol>\n")
	toplibro=dict()
	for x in books:
		toplibro[x[0]]=[x[1],x[2],x[3],x[-1]]
	print "Procesando informacion de libros"
	while i<k:
		libro=str(lista[i][1])
		stars=int(lista[i][0])
		if libro in toplibro.keys():
			nombre=toplibro[libro][0]
			autor=toplibro[libro][1]
			aniopubli=toplibro[libro][2]
			imagen=toplibro[libro][3]
		else:
			nombre="ISBN:"
			autor=libro	
			imagen="no.png"
			aniopubli=""
		html.write("<li class=\"wow bounceInUp\">\n")
		html.write("<img src=\""+imagen+"\">\n")
		html.write("<h2>"+nombre+"</h2>\n")
		html.write("<p>"+autor+"</p>\n")
		html.write("<p>"+aniopubli+"</p>\n")
		html.write("<div class=""\"stars\">")
		for x in range(stars):
			html.write("<i class=""\"fa fa-star\"></i>\n")
		html.write('<strong>Estrellas: '+str(stars)+'</strong>')
		html.write("</div>\n")
		html.write("</li>\n")
		i+=1
	html.write("</ol>\n")
	html.write('<script src="wow.min.js"></script>')
	html.write('<script src="main.js"></script>')
	html.write('</body>')
	html.write('</html>')
	html.close()
	print "Archivo top.html generado correctamente"
creartop(50,AllRatingLibros(8))	
