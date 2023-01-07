import random
import re
from data_struct import *
from math import sqrt
import itertools

def strWithoutChar(fnSource,toReplace: str,value: str = " "):
    """Generation of a string from fnSource where value is put in place of substring found by regex toReplace"""

    return re.sub(toReplace,value,fnSource())

def randomElement(existingSource = None, randomSourceFn = None, args: list = [], template: str = None, alsoNaN: bool = False) -> any:
    possibilities = []
    if existingSource is not None: possibilities.append(0)
    if randomSourceFn != None: possibilities.append(1)
    if alsoNaN: possibilities.append(2)
    
    choice = random.choices(possibilities, weights=[1, 0, 5], k=1) #None ha una possibilità 10 volte più alta di uscire del primo

    if not choice[0]:
        res = existingSource[random.randint(0,existingSource.size-1)]
    elif choice[0] == 1:
        res = randomSourceFn(*args)
    else:
        return None
    
    return res if template == None else template.format(res)

def rndFormattedInt(min: int = 0, max: int = 10, template: str = None):
    return template.format(random.randint(min,max))

def populateUtilityMatrix(people: People, queries: Queries, users: Users, persona_rating: pDataFrame, utility_matrix: UtilityMatrix, min: float = 0, max: float = 100):

    countc = 0

    for i in queries.index.values:
        q = queries.getQuery(i)
        result = people.poseQuery(q)

        #TEST QUERY -----------------------------------------------------------

        #print(result.empty())
        if len(result.index.values) > 0:
            countc +=1
        
        #-------------------------------------------------------------------

        for u in users.index.values:
            sum = 0
            count = 0
            dist = 0
            mu = NaN
            sd = NaN

            #Get mean
            for p in result.index.values:
                tmp = persona_rating[p][u] 
                if tmp is not NaN:
                    sum += tmp
                    count += 1

            if count > 0:
                mu = sum / count

            #Get std
            for p in result.index.values:
                tmp = persona_rating[p][u] 
                if tmp is not NaN:
                    dist += (tmp - mu)**2

            if count > 0:
                sd = sqrt(dist/count) 

            if mu is not NaN and sd is not NaN:           
                utility_matrix[i][u] = Normal(mu, sd).getGrade(min, max)
            else:
                utility_matrix[i][u] = NaN

    print(countc)

def removeValuesUtilityMatrix(utiliy_matrix: UtilityMatrix, queries: Queries, users: Users, num_users: int, num_queries:int, percentToDelete: int):

    users_list = users.index.values.copy()
    queries_list = queries.index.values.copy()

    deletedRows = False
    deletedColumns = False
    
    #Get how many elements to delete and how many to keep
    tot = num_users * num_queries
    nDelete =  int((percentToDelete * tot) / 100) #nDelete=10 

    #Get the number of columns to set to Nan
    nRowsDelete =  int((20 * num_users) / 100) #=2
    if nDelete > nRowsDelete * num_queries:
        nDelete -= nRowsDelete * num_queries   #-1 
        deletedRows = True

    #Get the number of rows to set to Nan
    nColDelete = int((20 * num_queries) / 100) #=2
    if nDelete > nColDelete * num_users  :
        nDelete -= nColDelete * num_users          #nDelete = 70 - (2*10) = 50
        deletedColumns =True

    if deletedColumns and deletedRows:
        nDelete += nRowsDelete * nColDelete #Crossing cells

    nKeep = tot - nDelete   

    #Get cartesian product of users and queries
    lists= [users_list, queries_list]
    cart_product = list()
    for element in itertools.product(*lists):
        cart_product.append(element)

    #Set random rows to Nan
    if deletedRows:
        random.shuffle(users_list)

        userIds = set() 

        for i in range(nRowsDelete):
            userIds.add(users_list[i])
            for queryId in queries_list:
                userId = "u{}".format(users_list[i])            
                utiliy_matrix[queryId][userId] = NaN

        for i in userIds:
            for j in queries_list:
                cart_product.remove((i, j))

    #Set random columns to Nan
    if deletedColumns:
        random.shuffle(queries_list)

        queryIds = set()

        for i in range(nColDelete):
            for userId in range(num_users):
                queryId = queries_list[i]
                queryIds.add(queryId)
                utiliy_matrix[queryId][userId] = NaN

        for i in queryIds:
            for j in users_list:
                if j not in userIds:
                    cart_product.remove((j, i))   

    #shuffle cartesian product and delete as many elements as the cells i want to keep
    random.shuffle(cart_product)
    cart_product = cart_product[nKeep:] #contains the coordinates of the values to set to NaN


    #Set the values to Nan
    for i in range(len(cart_product)):
        userId = "u{}".format(cart_product[i][0])
        queryId = cart_product[i][1]
        utiliy_matrix[queryId][userId] = NaN
