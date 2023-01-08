import random
import re
from data_struct import *
from math import sqrt

def strWithoutChar(fnSource,toReplace: str,value: str = " "):
    """Generation of a string from fnSource where value is put in place of substring found by regex toReplace"""

    return re.sub(toReplace,value,fnSource())

def randomElement(existingSource = None, randomSourceFn = None, args: list = [], template: str = None, alsoNaN: bool = False, weights: list = None) -> any:
    possibilities = []
    if existingSource is not None: possibilities.append(0)
    if randomSourceFn != None: possibilities.append(1)
    if alsoNaN: possibilities.append(2)
    
    choice = random.choices(possibilities, weights=weights, k=1) #None ha una possibilità 10 volte più alta di uscire del primo

    if not choice[0]:
        res = existingSource[random.randint(0,existingSource.size-1)]
    elif choice[0] == 1:
        res = randomSourceFn(*args)
    else:
        return None
    
    return res if template == None else template.format(res)

def rndFormattedInt(min: int = 0, max: int = 10, template: str = None):
    return template.format(random.randint(min,max))

def populateUtilityMatrix(utility_matrix: UtilityMatrix, people: People, queries: Queries, persona_rating: pDataFrame, min: float = 0, max: float = 100):

    nNaN = {
        "cells": 0, #Da togliere e mettere furoi per tagliare prod_cart
        "columns": 0,
        "rows": 0
    }

    cellsCoordinates = [["",""]]*utility_matrix.size
    coordinatesCount = 0
    NaNInRows = [0]*queries.index.size
    for q in queries.index.values:
        result = people.poseQuery(queries.getQuery(q))

        if result.empty:
            for u in utility_matrix.index.values:
                utility_matrix[q][u] = 0 #Nobody likes an empty query
                cellsCoordinates[coordinatesCount] = [q,u]
                coordinatesCount += 1
        else:
            i = 0
            NaNInCol = 0
            for u in utility_matrix.index.values:
                sum = 0
                count = 0
                dist = 0
                gradeNormal = Normal(NaN,NaN)

                #Get mean
                for p in result.index.values:
                    tmp = persona_rating[p][u]
                    if not isnan(tmp):
                        sum += tmp
                        count += 1

                if count > 0:
                    gradeNormal.mu = sum / count

                #Get std
                if not isnan(gradeNormal.mu):
                    for p in result.index.values:
                        tmp = persona_rating[p][u] 
                        if not isnan(tmp):
                            dist += (tmp - gradeNormal.mu)**2

                    if count > 0:
                        gradeNormal.sd = sqrt(dist/count) 

                if not isnan(gradeNormal.mu):
                    utility_matrix[q][u] = gradeNormal.getGrade(min, max)
                    cellsCoordinates[coordinatesCount] = [q,u]
                    coordinatesCount += 1
                else:
                    nNaN["cells"] += 1
                    NaNInCol += 1
                    NaNInRows[i] += 1
                i += 1

            if NaNInCol == utility_matrix.index.size: nNaN["columns"] += 1

    nNaN["rows"] = NaNInRows.count(utility_matrix.columns.size)
    return cellsCoordinates

def removeValuesUtilityMatrix(utiliy_matrix: UtilityMatrix, cellsCoordinates: list[list[str]], sparsity: float):

    #shuffle cartesian product and prepare elements to delete and lists to prevent empty rows or columns
    random.shuffle(cellsCoordinates)
    toDelete = len(cellsCoordinates)*sparsity
    elementsPerColumns = {q: utiliy_matrix.index.size for q in utiliy_matrix.columns}
    elementsPerRows = {u: utiliy_matrix.columns.size for u in utiliy_matrix.index}

    #Set the values to Nan
    count = 0
    while toDelete and count < len(cellsCoordinates):
        queryId = cellsCoordinates[count][0]
        userId = cellsCoordinates[count][1]
        if elementsPerColumns[queryId]-1 and elementsPerRows[userId]-1:
            utiliy_matrix[queryId][userId] = NaN
            toDelete -= 1
            elementsPerColumns[queryId] -= 1
            elementsPerRows[userId] -= 1
        count += 1