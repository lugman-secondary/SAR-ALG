import json
from nltk.stem.snowball import SnowballStemmer
import os
import re


class SAR_Project:
    """
    Prototipo de la clase para realizar la indexacion y la recuperacion de noticias

        Preparada para todas las ampliaciones:
          parentesis + multiples indices + posicionales + stemming + permuterm + ranking de resultado

    Se deben completar los metodos que se indica.
    Se pueden añadir nuevas variables y nuevos metodos
    Los metodos que se añadan se deberan documentar en el codigo y explicar en la memoria
    """

    # lista de campos, el booleano indica si se debe tokenizar el campo
    # NECESARIO PARA LA AMPLIACION MULTIFIELD
    fields = [("title", True), ("date", False),
              ("keywords", True), ("article", True),
              ("summary", True)]


    # numero maximo de documento a mostrar cuando self.show_all es False
    SHOW_MAX = 10


    def __init__(self):
        """
        Constructor de la classe SAR_Indexer.
        NECESARIO PARA LA VERSION MINIMA

        Incluye todas las variables necesaria para todas las ampliaciones.
        Puedes añadir más variables si las necesitas

        """
        self.index = {
                'title': {},
                'date': {},
                'keywords': {},
                'summary': {},
                'article': {}
        }
        # hash para el indice invertido de terminos --> clave: termino, valor: posting list.
        self.sindex = {
                'title': {},
                'date': {},
                'keywords': {},
                'summary': {},
                'article': {}
        }
        #hash para el índice de stems
        self.ptindex = {
                'title': {},
                'date': {},
                'keywords': {},
                'summary': {},
                'article': {}
        }
        #hash para el índice permuterm
        self.docs = {} # diccionario de documentos --> clave: entero(docid),  valor: ruta del fichero.
        self.weight = {} # hash de terminos para el pesado, ranking de resultados. puede no utilizarse
        self.news = {} # hash de noticias --> clave entero (newid), valor: la info necesaria para diferenciar la noticia dentro de su fichero (doc_id y posición dentro del documento)
        self.tokenizer = re.compile("\W+") # expresion regular para hacer la tokenizacion
        self.stemmer = SnowballStemmer('spanish') # stemmer en castellano
        self.show_all = False # valor por defecto, se cambia con self.set_showall()
        self.show_snippet = False # valor por defecto, se cambia con self.set_snippet()
        self.use_stemming = False # valor por defecto, se cambia con self.set_stemming()
        self.use_ranking = False  # valor por defecto, se cambia con self.set_ranking()


    ###############################
    ###                         ###
    ###      CONFIGURACION      ###
    ###                         ###
    ###############################
        self.vocab=[]
        self.docid = 0
        self.newid = 0
        self.num_days = {}
        self.term_frequency = {}
        self.searched_terms = []

    def set_showall(self, v):
        """

        Cambia el modo de mostrar los resultados.

        input: "v" booleano.

        UTIL PARA TODAS LAS VERSIONES

        si self.show_all es True se mostraran todos los resultados el lugar de un maximo de self.SHOW_MAX, no aplicable a la opcion -C

        """
        self.show_all = v


    def set_snippet(self, v):
        """

        Cambia el modo de mostrar snippet.

        input: "v" booleano.

        UTIL PARA TODAS LAS VERSIONES

        si self.show_snippet es True se mostrara un snippet de cada noticia, no aplicable a la opcion -C

        """
        self.show_snippet = v


    def set_stemming(self, v):
        """

        Cambia el modo de stemming por defecto.

        input: "v" booleano.

        UTIL PARA LA VERSION CON STEMMING

        si self.use_stemming es True las consultas se resolveran aplicando stemming por defecto.

        """
        self.use_stemming = v


    def set_ranking(self, v):
        """

        Cambia el modo de ranking por defecto.

        input: "v" booleano.

        UTIL PARA LA VERSION CON RANKING DE NOTICIAS

        si self.use_ranking es True las consultas se mostraran ordenadas, no aplicable a la opcion -C

        """
        self.use_ranking = v




    ###############################
    ###                         ###
    ###   PARTE 1: INDEXACION   ###
    ###                         ###
    ###############################


    def index_dir(self, root, **args):
        """
        NECESARIO PARA TODAS LAS VERSIONES

        Recorre recursivamente el directorio "root" e indexa su contenido
        los argumentos adicionales "**args" solo son necesarios para las funcionalidades ampliadas

        """

        self.multifield = args['multifield']
        self.positional = args['positional']
        self.stemming = args['stem']
        self.permuterm = args['permuterm']

        for dir, subdirs, files in os.walk(root):
            for filename in files:
                if filename.endswith('.json'):
                    fullname = os.path.join(dir, filename)
                    self.index_file(fullname)

        ##########################################
        ## COMPLETAR PARA FUNCIONALIDADES EXTRA ##
        ##########################################
        if self.stemming:
            self.make_stemming()
        if self.permuterm:
            self.make_permuterm()


    def index_file(self, filename):
        """
        NECESARIO PARA TODAS LAS VERSIONES

        Indexa el contenido de un fichero.

        Para tokenizar la noticia se debe llamar a "self.tokenize"

        Dependiendo del valor de "self.multifield" y "self.positional" se debe ampliar el indexado.
        En estos casos, se recomienda crear nuevos metodos para hacer mas sencilla la implementacion

        input: "filename" es el nombre de un fichero en formato JSON Arrays (https://www.w3schools.com/js/js_json_arrays.asp).
                Una vez parseado con json.load tendremos una lista de diccionarios, cada diccionario se corresponde a una noticia

        """

        with open(filename) as fh:
            jlist = json.load(fh)

        #
        # "jlist" es una lista con tantos elementos como noticias hay en el fichero,
        # cada noticia es un diccionario con los campos:
        #      "title", "date", "keywords", "article", "summary"
        #
        # En la version basica solo se debe indexar el contenido "article"
        #
        #
        #
      
        self.docs[self.docid] = filename

            # Contador de la posición de una noticia en un fichero
        contador_noticia = 0
        for noticia in jlist:
            # Se añade al diccionario de noticias la noticia con clave -> self.newid, valor -> (filename, contador_noticia)
            self.news[self.newid] = [self.docid, contador_noticia]

            # Si se activa la función de multifield
            if self.multifield:
                multifield = ['title', 'date',
                                'keywords', 'article', 'summary']
            # Si no, se procesa article y date (nos interesa para una métrica posterior)
            else:
                multifield = ['article', 'date']
            # Se tokeniza el cotenido de cada campo (menos el de date)
            for field in multifield:
                if field != 'date':
                    contenido = self.tokenize(noticia[field])
                else:
                    contenido = [noticia[field]]
                # Contador de la posición de un token en una noticia
                posicion_token = 0
                for token in contenido:
                    # Si el token no esta en el diccionario de tokens, se añade
                    if token not in self.index[field]:
                        if not self.positional:
                            self.index[field][token] = {
                                self.newid: 1}
                        else:
                            self.index[field][token] = {
                                self.newid: [posicion_token]}
                    # Si el token esta ya...
                    else:
                        # ...si no existe la noticia en el token, se añade
                        if self.newid not in self.index[field][token]:
                            if not self.positional:
                                self.index[field][token][self.newid] = 1
                            else:
                                self.index[field][token][self.newid] = [
                                    posicion_token]
                        else:
                            # Si no, se añade a la entrada del token-noticia la posición donde se ha encontrado
                            if not self.positional:
                                self.index[field][token][self.newid] += 1
                            else:
                                self.index[field][token][self.newid] += [posicion_token]

                    posicion_token += 1

            self.newid += 1

            contador_noticia += 1

        self.docid += 1



    def tokenize(self, text):
        """
        NECESARIO PARA TODAS LAS VERSIONES

        Tokeniza la cadena "texto" eliminando simbolos no alfanumericos y dividientola por espacios.
        Puedes utilizar la expresion regular 'self.tokenizer'.

        params: 'text': texto a tokenizar

        return: lista de tokens

        """
        return self.tokenizer.sub(' ', text.lower()).split()



    def make_stemming(self):
        """
        NECESARIO PARA LA AMPLIACION DE STEMMING.

        Crea el indice de stemming (self.sindex) para los terminos de todos los indices.

        self.stemmer.stem(token) devuelve el stem del token

        """
        f = []
        for i in self.fields:
            f.append(i[0])

        for field in f:
            for termino in self.index[field].keys():
                term = self.stemmer.stem(termino)
                if self.sindex[field].get(term) == None:
                    self.sindex[field][term] = [termino]
                else:
                    self.sindex[field][term] = self.sindex[field][term] + [termino]

        


    def make_permuterm(self):
        """
        NECESARIO PARA LA AMPLIACION DE PERMUTERM

        Crea el indice permuterm (self.ptindex) para los terminos de todos los indices.

        """
        if self.multifield:
            # Searching for the different fields
            f = []
            for i in self.fields:
                f.append(i[0])

            for field in range(len(f)):
                for termino in self.index[f[field]].keys():
                    t = termino
                    termino += '$'
                    permutations = []

                    for i in range(len(termino)):
                        termino = termino[1:] + termino[0]
                        permutations.append(termino)
                    #self.ptindex[f[field]][t] = len(permutations) if self.ptindex[f[field]].get(t) == None else self.ptindex[f[field]][t] + len(permutations)
                    if self.ptindex[f[field]].get(t) == None:
                        self.ptindex[f[field]][t] = permutations
                    else:
                        self.ptindex[f[field]][t] = self.ptindex[f[field]][t] + permutations
        else:
            for termino in self.index['article'].keys():
                termino += '$'
                permutations = []

                for i in range(len(termino)):
                    termino = termino[1:] + termino[0]
                    permutations = permutations + [termino]

                #self.ptindex['article'][termino] = len(permutations)
                #self.ptindex['article'][termino] = permutations if self.ptindex['article'].get(termino) == None else self.ptindex['article'][termino] + termino 
                if self.ptindex['article'].get(termino) == None:
                    self.ptindex['article'][termino] = permutations
                else:
                    self.ptindex['article'][termino] = self.ptindex['article'][termino] + permutations




    def show_stats(self):
        """
        NECESARIO PARA TODAS LAS VERSIONES

        Muestra estadisticas de los indices

        """
        pass
        ########################################
        ## COMPLETAR PARA TODAS LAS VERSIONES ##
        ########################################
        print("\n")
        print("="*20)
        print("Number of indexed days: "+str(len(self.index['date'].keys())))
        print("-"*20)
        print("Number of indexed news: "+str(len(self.news.keys())))
        print("-"*20)
        
        #comprobación multiterm
        if self.multifield:
            multifield = ['title', 'date', 'keywords', 'article', 'summary']
        else:
            multifield = ['article']
        print("TOKENS:")
        for field in multifield:
            if field:
                print('     # of tokens in \'{}\': {}'.format(
                    field, len(self.index[field])))
        print("-"*20)
        # permuterm activo #
        if self.permuterm:
            for field in multifield:
                if field:
                    print('     # of permuterms in \'{}\': {}'.format(
                        field, len(self.ptindex[field])))
        print("-"*20)
        # stemming activo #
        if self.stemming:
            for field in multifield:
                if field:
                    print('     # of stems in \'{}\': {}'.format(
                        field, len(self.sindex[field])))
        print("-"*20)
        #comprobación positional
        if self.positional: 
            print("Positional queries are alowed.")
        else:
            print("Positional queries are NOT alowed.")
        print("="*20)









    ###################################
    ###                             ###
    ###   PARTE 2.1: RECUPERACION   ###
    ###                             ###
    ###################################


    def solve_query(self, query):
        """
        NECESARIO PARA TODAS LAS VERSIONES
        Resuelve una query.
        Debe realizar el parsing de consulta que sera mas o menos complicado en funcion de la ampliacion que se implementen
        param:  "query": cadena con la query
                "prev": incluido por si se quiere hacer una version recursiva. No es necesario utilizarlo.
        return: posting list con el resultado de la query
        """
        if query is None or len(query) == 0:
            return []

        res = []

        # Preprocesamiento de la consulta
        query = query.replace('"', '')
        query = query.replace('(', ' ( ')
        query = query.replace(')', ' ) ')
        q = query.split()

        # Bucle que realiza, primeramente, las funcionalidades extra
        i = 0
        while i < len(q):
            term = q[i]
            # 1º Subconcultas y subconsultas anidadas (de forma iterativa)
            if term == '(':
                i += 1
                q2 = ''
                aux = 0
                while aux >= 0:
                    if q[i] == '(':
                        aux += 1
                    if q[i] == ')':
                        aux -= 1
                    q2 += q[i] + ' '
                    i += 1
                q2 = q2.strip()
                q2 = q2[0:len(q2) - 1]
                res.append(self.solve_query(q2))
            else:
                # 2º Consultas multifield
                if ':' in term:
                    field = term[0:term.find(':')]
                    term = term[term.find(':') + 1:]
                else:
                    field = 'article'
                # Se codifica los conectores básicos para un posterior tratado
                if term == 'AND':
                    res += [1]
                    i += 1
                elif term == 'OR':
                    res += [0]
                    i += 1
                elif term == 'NOT':
                    res += [-1]
                    i += 1
                else:
                    # 3º Consultas permuterm (wildcard query)
                    term = term.lower()
                    if '*' in term:
                        res.append(self.get_permuterm(term, field))
                        i += 1
                    elif '?' in term:
                        res.append(self.get_permuterm(term, field))
                        i += 1
                    else:
                        # 4º Consultas posicionales
                        aux = 0
                        terms = []
                        while (i + aux) < len(q) and q[i + aux] != 'AND' and q[i + aux] != 'OR' and q[i + aux] != 'NOT':
                            terms.append(q[i + aux])
                            aux += 1
                        if len(terms) == 1:
                            if self.use_stemming:
                                res.append(self.get_stemming(term, field))
                            else:
                                res.append(self.get_posting(term, field))
                            i += 1
                        else:
                            res.append(self.get_positionals(terms, field))
                            i += aux


        # Bucle que realiza, en segundo lugar, las funcionalidades básicas
        ret = []
        i = 0
        while i < len(res):
            # Según la codificación anterior realiza NOT o AND o OR, respectivamente
            r = res[i]
            if r == 1:
                if res[i + 1] == -1:
                    seg = self.reverse_posting(res[i + 2])
                    i += 3
                else:
                    seg = res[i + 1]
                    i += 2
                ret = self.and_posting(ret, seg)
            elif r == 0:
                if res[i + 1] == -1:
                    seg = self.reverse_posting(res[i + 2])
                    i += 3
                else:
                    seg = res[i + 1]
                    i += 2
                ret = self.or_posting(ret, seg)
            elif r == -1:
                ret = self.reverse_posting(res[i + 1])
                i += 2
            else:
                ret = r
                i += 1

        return ret
    



    def get_posting(self, term, field='article',wildcard='False'):
        """
        NECESARIO PARA TODAS LAS VERSIONES

        Devuelve la posting list asociada a un termino.
        Dependiendo de las ampliaciones implementadas "get_posting" puede llamar a:
            - self.get_positionals: para la ampliacion de posicionales
            - self.get_permuterm: para la ampliacion de permuterms
            - self.get_get_stemming: para la amplaicion de stemming


        param:  "term": termino del que se debe recuperar la posting list.
                "field": campo sobre el que se debe recuperar la posting list, solo necesario se se hace la ampliacion de multiples indices

        return: posting list

        """
        pass
        ########################################
        ## COMPLETAR PARA TODAS LAS VERSIONES ##
        ########################################
        res=[]
        if '*' in term or '?' in term:
            res = self.get_permuterm(term, field)
        # Posting list de un stem
        elif self.use_stemming and not wildcard:
            res = self.get_stemming(term, field)
        # Posting list de un termino
        else:
            if term in self.index[field]:
                res = list(self.index[field][term].keys())

        return res



    def get_positionals(self, terms, field='article'):
        """
        NECESARIO PARA LA AMPLIACION DE POSICIONALES

        Devuelve la posting list asociada a una secuencia de terminos consecutivos.

        param:  "terms": lista con los terminos consecutivos para recuperar la posting list.
                "field": campo sobre el que se debe recuperar la posting list, solo necesario se se hace la ampliacion de multiples indices

        return: posting list

        """
        
        ########################################################
        ## COMPLETAR PARA FUNCIONALIDAD EXTRA DE POSICIONALES ##
        ########################################################
        result = []

        actual = terms[0]
        res = self.get_posting(actual)
        
        if(len(terms)<=1):
            return res
        i=1


        while(i < len(terms)):
            resAct= []

            next = terms[i]
            
        
            l2 = self.get_posting(next)
            result = self.and_posting(res, l2)
        
            

            for elem in result:
                for lActual in self.index[field][actual][elem]:
                    if (lActual + 1) in self.index[field][next][elem]:                        
                        res += [elem]
                        resAct += [elem]

            
            returnList=[]
            for el in res:
                if(el in resAct):
                    returnList += [el]
                #print(el)

            res = list(dict.fromkeys(returnList))

            i+=1
            actual = next        
        
        
        return res

                    
                        

    
            
            
    def get_stemming(self, term, field='article'):
        """
        NECESARIO PARA LA AMPLIACION DE STEMMING

        Devuelve la posting list asociada al stem de un termino.

        param:  "term": termino para recuperar la posting list de su stem.
                "field": campo sobre el que se debe recuperar la posting list, solo necesario se se hace la ampliacion de multiples indices

        return: posting list

        """
        # Obtenemos el stem de este termino
        stem = self.stemmer.stem(term)

        res = []

        # Si existe este stem, devolvemos la union de las posting list para todas los terminos asociados a este stem
        if stem in self.sindex[field]:
            for token in self.sindex[field][stem]:
                # Utilizamos el metodo OR para concatenar
                res = self.or_posting(
                    res, list(self.index[field][token].keys()))

        return res



    def get_permuterm(self, term, field='article'):
        """
        NECESARIO PARA LA AMPLIACION DE PERMUTERM

        Devuelve la posting list asociada a un termino utilizando el indice permuterm.

        param:  "term": termino para recuperar la posting list, "term" incluye un comodin (* o ?).
                "field": campo sobre el que se debe recuperar la posting list, solo necesario se se hace la ampliacion de multiples indices

        return: posting list

        """
        
        # Realizamos la wildcard
        query = term + '$'
        
        #Buscamos el símbolo '?' o '*', paramos cuando lo encontremos
        while query[-1] != "*" and query[-1] != '?':
            query = query[1:] + query[0]

        #Aquí almacenaremos la palabra hasta el término
        query = query[:-1]
        # Aquí almacenaremos el termino '?' o '*'
        simb = query[-1]

        res = []

        listTerms = (t for t in list(self.ptindex[field].keys()) if t.startswith(term) and (simb == '*' or len(t) == len(term) + 1))


        for perm in listTerms:
            for token in self.ptindex[field][perm]:
                # Concatenamos los posting_list con el metodo OR
                # Para evitar que haga el stem de cada término establecemos wildcard=True 
                res = self.or_posting(res, self.get_posting(
                    token, field, wildcard=True))

        return res

    def minus_posting(self, p1, p2):
        """
        OPCIONAL PARA TODAS LAS VERSIONES

        Calcula el except de dos posting list de forma EFICIENTE.
        Esta funcion se propone por si os es util, no es necesario utilizarla.

        param:  "p1", "p2": posting lists sobre las que calcular


        return: posting list con los newid incluidos de p1 y no en p2

        """

        if p1 is None or p2 is None or len(p1) == 0 or len(p2) == 0:
            return []

        # return [x for x in p1 if x not in p2]

        res = []
        x = y = 0

        while x < len(p1) and y < len(p2):
            if p1[x] == p2[y]:
                x += 1
                y += 1

            else:
                res.append(p1[x])
                x += 1

        while x < len(p1):
            res.append(p1[x])
            x += 1

        return res


        #pass
        ########################################################
        ## COMPLETAR PARA TODAS LAS VERSIONES SI ES NECESARIO ##
        ########################################################



    def reverse_posting(self, p):
        """
        NECESARIO PARA TODAS LAS VERSIONES

        Devuelve una posting list con todas las noticias excepto las contenidas en p.
        Util para resolver las queries con NOT.


        param:  "p": posting list


        return: posting list con todos los newid exceptos los contenidos en p

        """

        # Obtenemos lista de todas las noticias
        res = list(self.news.keys())
        # Recorremos la posting list
        for post in p:
            # Eliminamos la noticia de la lista de todas las noticias
            res.remove(post)

        return res




        #pass
        ########################################
        ## COMPLETAR PARA TODAS LAS VERSIONES ##
        ########################################



    def and_posting(self, p1, p2):
        """
        NECESARIO PARA TODAS LAS VERSIONES

        Calcula el AND de dos posting list de forma EFICIENTE

        param:  "p1", "p2": posting lists sobre las que calcular


        return: posting list con los newid incluidos en p1 y p2

        """

        #pass
        ########################################
        ## COMPLETAR PARA TODAS LAS VERSIONES ##
        ########################################
        res = []
        i = 0
        j = 0
        # El pseudocodigo de teoria pasado a Python
        while i < len(p1) and j < len(p2):
            if p1[i] == p2[j]:
                res.append(p1[i])
                i += 1
                j += 1
            elif p1[i] <= p2[j]:
                i += 1
            elif p1[i] >= p2[j]:
                j += 1

        return res


    def or_posting(self, p1, p2):
        """
        NECESARIO PARA TODAS LAS VERSIONES

        Calcula el OR de dos posting list de forma EFICIENTE

        param:  "p1", "p2": posting lists sobre las que calcular


        return: posting list con los newid incluidos de p1 o p2

        """
        res = []
        i = 0
        j = 0
        
        
        while i < len(p1) and j < len(p2):
          
            if p1[i] == p2[j]:
                res.append(p1[i])
                i+=1
                j+=1
            elif p1[i] < p2[j]:
                res.append(p1[i])
                i+=1
            else:
                res.append(p2[j])
                j+=1

        for pos in range(i, len(p1)):
            res.append(p1[pos])

        for pos in range(j, len(p2)):
            res.append(p2[pos])

        return res

        #pass
        ########################################
        ## COMPLETAR PARA TODAS LAS VERSIONES ##
        ########################################


    




    #####################################
    ###                               ###
    ### PARTE 2.2: MOSTRAR RESULTADOS ###
    ###                               ###
    #####################################


    def solve_and_count(self, query):
        """
        NECESARIO PARA TODAS LAS VERSIONES

        Resuelve una consulta y la muestra junto al numero de resultados

        param:  "query": query que se debe resolver.

        return: el numero de noticias recuperadas, para la opcion -T

        """
        result = self.solve_query(query)
        print("%s\t%d" % (query, len(result)))
        return len(result)  # para verificar los resultados (op: -T)

        

    def print_snippets(self, new, query):
       
        words = self.tokenize(new['article'])
        # Limpiaremos la palabra de valores que ahora no nos hacen falta
        query = query.replace('"', '')
        query = query.replace('*', '')
        query = query.replace('(', '')
        query = query.replace(')', '')
        query = query.replace('?', '')
        query = query.replace('NOT ', 'NOT')
        # Tendremos en cuenta el campo multifiel, pero no utilizaremos el simbolo ':' más veces
        query = query.replace(':', '|POS|')
        query = self.tokenize(query)
        
        snippet=''
        l_cont = 0
       
        
        for w in query:
            # Buscaremos en article, en caso de que no sea multifiel
            local = words

            # Si es multifield, tokenizaremos los campos posibles para buscar en ellos también
            if '|POS|' in w:
                field, w = w.split('|POS|')
                # No hay que tokenizar la fecha
                if field != 'date':
                    local = self.tokenize(new[field])

            #Buscaremos en los campos oportunos para así mostrar las información que podamos.
            if w in local:
                #Obtenemos la primera ocurrencia del término, en caso de que esté sea encontrado

                pos = local.index(w)
                min_p = pos - 5

                # En caso de que este sea menor que 0, es decir no encontrado optendremos texto desde el principio
                if min_p < 0:
                    min_p = 0
                max_p = pos + 5
                # Tambien tendremos en cuenta el máximo del text
                if max_p > len(local) - 1:
                    max_p = len(local) - 1

                # Si el fragmento no está al principio, indicaremos esto con '...'
                snippet_aux = ''
                if min_p > 0:
                    snippet_aux += '...'

                # Aquí realizaremos la inclusión del texto referente al snippet
                snippet_aux += " ".join(local[min_p:max_p + 1])

                # En caso de no ser el final también podremos '...'
                if max_p < len(local) - 1:
                    snippet_aux += '...'

                l_cont += 1
                
                #Pondremos saltos de linea para separa los diferente tokens
                if l_cont != len(query) - 1 and len(query) > 1 and len(snippet_aux.lstrip()) > 0:
                    snippet_aux += '\n'

                snippet += snippet_aux

        # Finalmente lo imprimimos desde aquí para segmentar mejor el código
        print(snippet)

    def solve_and_show(self, query):
        """
        NECESARIO PARA TODAS LAS VERSIONES

        Resuelve una consulta y la muestra informacion de las noticias recuperadas.
        Consideraciones:

        - En funcion del valor de "self.show_snippet" se mostrara una informacion u otra.
        - Si se implementa la opcion de ranking y en funcion del valor de self.use_ranking debera llamar a self.rank_result

        param:  "query": query que se debe resolver.

        return: el numero de noticias recuperadas, para la opcion -T

        """
        result = self.solve_query(query)


        print("=" * 40) 
        print('Query: \'{}\''.format(query))
        print('Number of results: {}'.format(len(result)))

        i = 1
        for new in result:
            aux = self.news[new]

            with open(self.docs[self.news[new][0]]) as fh:
                jlist = json.load(fh)
                aux = jlist[self.news[new][1]]

            if self.use_ranking:
                puntuacion = self.jaccard(query, aux)
            else:
                puntuacion = 0

            # Si esta activada la función de snippets
            if not self.show_snippet:
                print('#{:<4} ({}) ({}) ({}) {} ({})'.format(
                    i, puntuacion, new, aux['date'], aux['title'], aux['keywords']))
            else:
                print('#{}'.format(i))
                print('Score: {}'.format(puntuacion))
                print(new)
                print('Date: {}'.format(aux['date']))
                print('Title: {}'.format(aux['title']))
                print('Keywords: {}'.format(aux['keywords']))

                self.print_snippets(aux,query)

            i += 1

            if not self.show_all and i > self.SHOW_MAX:
                break
        print("=" * 40)



    def rank_result(self, result, query):
        """
        NECESARIO PARA LA AMPLIACION DE RANKING

        Ordena los resultados de una query.

        param:  "result": lista de resultados sin ordenar
                "query": query, puede ser la query original, la query procesada o una lista de terminos


        return: la lista de resultados ordenada

        """
        pass

        ###################################################
        ## COMPLETAR PARA FUNCIONALIDAD EXTRA DE RANKING ##
        ###################################################
