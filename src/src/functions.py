import random
import re
from data_struct import *
from math import sqrt

def strWithoutChar(fnSource,toReplace: str,value: str = " "):
    """Generation of a string from fnSource where value is put in place of substring found by regex toReplace"""

    return re.sub(toReplace,value,fnSource())

def randomElement(existingSource = None, randomSourceFn = None, args: list = [], template: str = None, alsoNaN: bool = False) -> any:
    possibilities = []
    if existingSource is not None: possibilities.append(0)
    if randomSourceFn != None: possibilities.append(1)
    if alsoNaN: possibilities.append(2)
    
    choice = random.choice(possibilities)
    if not choice:
        res = existingSource[random.randint(0,existingSource.size-1)]
    elif choice == 1:
        res = randomSourceFn(*args)
    else:
        return None
    
    return res if template == None else template.format(res)

def rndFormattedInt(min: int = 0, max: int = 10, template: str = None):
    return template.format(random.randint(min,max))

def populateUtilityMatrix(people: People, queries: Queries, users: Users, persona_rating: pDataFrame, utility_matrix: UtilityMatrix, min: float = 0, max: float = 100):

    for i in queries.index.values:
        q = queries.getQuery(i)
        result = people.poseQuery(q)
        for u in users.index.values:
            sum = 0
            count = 0
            dist = 0

            #Get mean
            for p in result.index.values:
                tmp = persona_rating[p][u] 
                if tmp is not NaN:
                    sum += tmp
                    count += 1
                print(p)
                #persona_rating[p][u] 
            mu = sum / count

            #Get std
            for p in result.index.values:
                tmp = persona_rating[p][u] 
                if tmp is not NaN:
                    dist += (tmp - mu)**2
                print(p)

            sd = sqrt(dist/count)            
            utility_matrix[i][u] = Normal(mu, sd).getGrade(max, min)
    