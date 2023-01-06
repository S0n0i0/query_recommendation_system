from enum import Enum
import pandas as pd
import json
import io
import random
from numpy import NaN
from math import ceil

Id = str
Score = float
pSeries = pd.core.series.Series
pDataFrame = pd.core.frame.DataFrame

def maxLenSample(sequence, maxLen: int | None = None, isRandom: bool = True):
    l = maxLen if maxLen is not None and type(maxLen) == int else len(sequence)
    return random.sample(sequence,random.randint(0,l) if isRandom else l)

def isIn0_1(n: float) -> bool:
    return n >= 0 and n <= 1

class ReferenceType(Enum):
    USER = 0
    QUERY = 1

class Query(pSeries): #Trovare alternativa al subclassing, dato che non dovrebbe essere il massimo per pandas

    def __init__(self, query) -> None:
        super().__init__(query)

    def __str__(self) -> str:
        query = ""
        fields = self[self.notna()]
        for i in fields.index:
            query += str(i) + " == '" +  str(fields[i]) + "' & "
        return query[:-3]

class People:
    def __init__(self, people: pDataFrame = pd.DataFrame()) -> None:
        self.people = people

    @staticmethod
    def fromCsv(csvName: str = "", sep: str = ","):
        people = People()
        if csvName != "": people.people = pd.read_csv(csvName, sep=sep, index_col=False) #Mettere index_col=0 se si vuole tornare con prima riga come index
        return people
    
    def toCsv(self, csvName: str = "", sep: str = ","):
        if csvName != "": self.people.to_csv(csvName, index=False) #Togliere index=False se si vuole tornare con id come index

    def __str__(self) -> str:
        return str(self.people)

    def __getattr__(self, attr):
        return getattr(self.people, attr)

    def getFields(self) -> tuple:
        ref = self.people
        return tuple(ref.columns)#.insert(0,ref.index.name))

    '''def getPerson(self,id) -> pSeries:
        return self.people.loc[id]'''

    def getColumnSubset(self, columns: str | list = "") -> pDataFrame:
        return self.people[columns]

    def poseQuery(self, query: Query | str) -> pDataFrame:
        """Consider the table structure indexes=people, columns=fields"""

        return self.people.query(query if isinstance(query,str) else str(query))

class Users:
    def __init__(self, users: pSeries = pd.Series(dtype="object")) -> None:
        self.users = users

    @staticmethod
    def fromCsv(csvName: str = "", sep: str = ","):
        users = Users()
        if csvName != "": users.users = pd.read_csv(csvName, sep=sep, header=None).squeeze()
        return users

    def toCsv(self, csvName: str = "", sep: str = ","):
        if csvName != "": self.users.to_csv(csvName, header=False, index=False)

    def __str__(self) -> str:
        return str(self.users)

    def __getattr__(self, attr):
        return getattr(self.users, attr)

    def getUser(self, index: int) -> Id:
        return self.users[index]

    def concatUser(self, ids: pSeries) -> None:
        """If you have to append elements in a for loop, use a list and then use this concat method"""

        self.users = pd.concat([self.users,ids],ignore_index=True)
    
    def contains(self, id: Id):
        return id in self.users.values

class Queries:
    def __init__(self, queries: pDataFrame = pd.DataFrame()) -> None:
        self.queries = queries

    @staticmethod
    def fromCsv(csvName: str = "", csvSep: str = ",", keyValueSep: str = "="): #Controllare se con file grandi questa procedura è troppo lenta
        queries = Queries()
        if csvName != "":
            records = {}
            with open(csvName, "r") as file:
                for line in file:
                    record = {}
                    splittedLine = (line[:-1] if line[-1] == "\n" else line).split(csvSep)
                    for field in splittedLine[1:]:
                        key, value = field.split(keyValueSep)
                        record[key] = value
                    records[splittedLine[0]] = record

            queries.queries = pd.read_json(io.StringIO(json.dumps(records)),orient="index")
        
        return queries

    def toCsv(self, csvName: str = "", sep: str = ","):
        if csvName != "":
            with open(csvName, "w") as f:
                queryDict = self.queries.to_dict("index")
                for i in queryDict:
                    f.write(i)
                    for param in queryDict[i]:
                        if queryDict[i][param] != None:
                            f.write("," + str(queryDict[i][param]))
                    f.write("\n")
    
    def __str__(self) -> str:
        return str(self.queries)

    def __getattr__(self, attr):
        return getattr(self.queries, attr)

    def getQuery(self, id: Id) -> Query:
        return Query(self.queries.loc[id])

    def getColumnSubset(self, columns: list = []) -> pDataFrame:
        return self.queries[columns]

    def concatQueries(self, queries: pDataFrame) -> None:
        """If you have to append elements in a for loop, use a list and then use this concat method"""

        self.queries = pd.concat([self.queries,pDataFrame])

    def filterQueries(self, query: Query | str):
        """Consider the table structure indexes=queries, columns=fields"""

        return self.queries.query(query if isinstance(query,str) else str(query))

class UtilityMatrix:
    def __init__(self, utility_matrix: pDataFrame = pd.DataFrame()) -> None:
        self.utility_matrix = utility_matrix

    @staticmethod
    def fromCsv(csvName: str = "", sep: str = ","):
        utility_matrix = UtilityMatrix()
        if csvName != "": utility_matrix.utility_matrix = pd.read_csv(csvName, sep=sep)
        return utility_matrix

    def toCsv(self, csvName: str = "", sep: str = ","):
        if csvName != "":
            with open(csvName,"w",newline='') as f:
                f.write(self.utility_matrix.to_csv()[1:])

    def __str__(self) -> str:
        return str(self.utility_matrix)

    def __getattr__(self, attr):
        return getattr(self.utility_matrix, attr)

    def getScore(self, queryId: Id, userId: Id) -> Score:
        return self.utility_matrix[queryId][userId]
        
    def getQueryScores(self, id: Id) -> pSeries:
        return self.utility_matrix[id]
    
    def getUserScores(self, id: Id) -> pSeries:
        return self.utility_matrix.loc[id]

    def setScore(self, userId: Id, queryId: Id, score: Score) -> None:
        self.utility_matrix[queryId][userId] = score

    def addEmptyQuery(self, id: Id) -> bool:
        self.utility_matrix[id] = [NaN for i in range(self.utility_matrix.shape[0])]

    def addEmptyUser(self, id: Id) -> bool:
        self.utility_matrix.loc[id] = [NaN for i in range(self.utility_matrix.shape[1])]

    def filterUm(self, query: Query | str):
        """Consider the table structure indexes=queries, columns=fields"""

        return self.utility_matrix.query(query if isinstance(query,str) else str(query))

    def getScoresGe(self, n: float): #Trovare un modo migliore per eliminare righe e colonne e per passare operatore (unendo gli altri 3 metodi)
        scores = self.utility_matrix[self.utility_matrix.iloc[:] >= n].dropna(0,"all")
        return scores.dropna(1,"all")
    
    def getScoresLe(self, n: float): #Trovare un modo migliore per eliminare righe e colonne
        scores = self.utility_matrix[self.utility_matrix.iloc[:] <= n].dropna(0,"all")
        return scores.dropna(1,"all")
    
    def getScoresEq(self, n: float): #Trovare un modo migliore per eliminare righe e colonne
        scores = self.utility_matrix[self.utility_matrix.iloc[:] == n].dropna(0,"all")
        return scores.dropna(1,"all")

class Normal:
    def __init__(self, mu: float = 0, sd: float = 1) -> None:
        self.mu = mu
        self.sd = sd

    def getGrade(self, min: float | None = None, max: float | None = None) -> float:
        
        grade = random.gauss(self.mu,self.sd)
        if min is not None:
            if grade < min: grade = min
        if max is not None:
            if grade > max: grade = max

        return grade

class Conditions: #Trovare nome migliore
    def __init__(self, normal: Normal = Normal(), fields: set[str] | None = None, elementsProp: float = 1, randomLen: bool = True, specialCases: dict[str,set] = {}) -> None:
        self.normal = normal
        self.fields = fields
        self.elementsProp = elementsProp if isIn0_1(elementsProp) else 1 #Trovare nome migliore
        self.randomLen = randomLen
        self.specialCases = specialCases

class UserProfile:
    def __init__(self, people: People = People(), preferences: Conditions = Conditions(), disinterests: Conditions = Conditions(), avgGradesNormals: list[Normal] = []) -> None:

        toSample = {}
        tmpPref = {}
        tmpBlackList = {}

        self.preferencesGrades = preferences.normal
        self.disinterestsGrades = disinterests.normal
        
        if not people.empty:
            if preferences.fields == None: preferences.fields = set(maxLenSample(people.getFields()))
            if disinterests.fields == None: disinterests.fields = set(maxLenSample(people.getFields()))

            for i in preferences.fields|disinterests.fields: #remove special cases for coerence with random
                toSample[i] = set(people.getColumnSubset(i).unique())
                if i in preferences.specialCases: toSample[i] = toSample[i]-preferences.specialCases[i]
                if i in disinterests.specialCases: toSample[i] = toSample[i]-disinterests.specialCases[i]

            for i in preferences.fields: #preferences creation
                tmpPref[i] = set(maxLenSample(toSample[i],ceil(len(toSample[i])*preferences.elementsProp),preferences.randomLen))
                if i in disinterests.fields: toSample[i] = toSample[i]-tmpPref[i]
            for i in disinterests.fields: #disinterests creation
                tmpBlackList[i] = set(maxLenSample(toSample[i],ceil(len(toSample[i])*disinterests.elementsProp),disinterests.randomLen))

            for i in preferences.specialCases: #preferences special cases
                if i in tmpPref:
                    tmpPref[i] = tmpPref[i] | preferences.specialCases[i]
                else:
                    tmpPref[i] = preferences.specialCases[i]
            for i in disinterests.specialCases: #disinterests special cases
                if i in tmpBlackList:
                    tmpBlackList[i] = tmpBlackList[i] | disinterests.specialCases[i]
                else:
                    tmpBlackList[i] = disinterests.specialCases[i]
                    
        self.preferences = tmpPref
        self.disinterests = tmpBlackList
        self.avgGradesNormals = avgGradesNormals

    def getGrade(self, person: pSeries, min: float | None = None, max: float | None = None) -> float:
        
        liking = 0
        for i in self.preferences:
            if person[i] in self.preferences[i]: liking += 2
            elif i not in self.disinterests or person[i] not in self.disinterests[i]: liking += 1
        
        totalGradeTypes = (2+len(self.avgGradesNormals))
        gradeType = round(liking*totalGradeTypes/(len(self.preferences[i])*2)) #liking:maxLiking=gradeType:totalGradesType
        print(liking,":",(len(self.preferences[i])*2),"=",gradeType,":",totalGradeTypes)
        if gradeType == 0:
            return self.disinterestsGrades.getGrade(min,max)
        elif gradeType == totalGradeTypes:
            return self.preferencesGrades.getGrade(min,max)
        else:
            return self.avgGradesNormals[gradeType-1].getGrade(min,max)
        
'''
#["name","age","occupation"]
#{
    "name": ["Eros","Simone"]
    "age": [10]
    "occupation": ["fireman","employee","Sailor"]
}#
#Parametri casi particolari (piace,non piace a tutti)

p1,Eros,17,Sailor,Via di là
liking = 2
liking:totLiking=x:typesGrades.length
2:5=x:4
x=liking*tyepsGrades/totLiking
random.norm(typesGrades[x])

persona-rating
    u0 u1
p1 5  n
p2 10 n
p3 n  3

for all query -> poseQuery -> compute mu,sd of all p -> random.norm(mu,sd) for all u
randomElement(randomSourceFn=random.normalvariate,args=[0,1],alsoNaN=alsoNan)
'''