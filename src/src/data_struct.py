from enum import Enum
import pandas as pd
import json
import io
from numpy import NaN

Id = str
Score = float
pSeries = pd.core.series.Series
pDataFrame = pd.core.frame.DataFrame

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
    def __init__(self, data = None, index = None, columns = None) -> None:
        self.people = pd.DataFrame(data,index,columns)

    @staticmethod
    def fromCsv(csvName: str = "", sep: str = ","):
        people = People()
        if csvName != "": people.people = pd.read_csv(csvName, sep=sep, index_col=0)
        return people

    def __str__(self) -> str:
        return str(self.people)

    def __getattr__(self, attr):
        return getattr(self.people, attr)

    def getFields(self) -> tuple:
        ref = self.people
        return tuple(ref.keys().insert(0,ref.index.name))

    def getPerson(self,id) -> pSeries:
        return self.people.loc[id]

    def getColumnSubset(self, columns: list = []) -> pDataFrame:
        return self.people[columns]

    def poseQuery(self, query: Query | str) -> pDataFrame:
        """Consider the table structure indexes=people, columns=fields"""

        return self.people.query(query if isinstance(query,str) else str(query))

class Users:
    def __init__(self, data = None, index = None, name = None) -> None:
        self.users = pd.Series(data,index,"object",name)

    @staticmethod
    def fromCsv(csvName: str = "", sep: str = ","):
        users = Users()
        if csvName != "": users.users = pd.read_csv(csvName, sep=sep, header=None).squeeze()
        return users

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
    def __init__(self, data = None, index = None, columns = None) -> None:
        self.queries = pd.DataFrame(data,index,columns)

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
    def __init__(self, data = None, index = None, columns = None) -> None:
        self.utility_matrix = pd.DataFrame(data,index,columns)

    @staticmethod
    def fromCsv(csvName: str = "", sep: str = ","):
        utility_matrix = UtilityMatrix()
        if csvName != "": utility_matrix.utility_matrix = pd.read_csv(csvName, sep=sep)
        return utility_matrix

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