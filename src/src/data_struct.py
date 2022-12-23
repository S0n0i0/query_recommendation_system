from enum import Enum
import pandas
import json
import io
from numpy import NaN

Id = str
Score = float

class ReferenceType(Enum):
    USER = 0
    QUERY = 1

class Query(pandas.core.series.Series):

    def __init__(self, query) -> None:
        super().__init__(query)

    def __str__(self) -> str:
        query = ""
        fields = self[self.notna()]
        for i in fields.index:
            query += str(i) + " == '" +  str(fields[i]) + "' & "
        return query[:-3]

class People:
    def __init__(self, csvName: str, sep: str = ",") -> None:
        self.people = pandas.read_csv(csvName, sep=sep, index_col="id")

    def __str__(self) -> str:
        return str(self.people)

    def getFields(self) -> tuple:
        ref = self.people
        return tuple(ref.keys().insert(0,ref.index.name))

    def getPerson(self,id) -> pandas.core.series.Series:
        return self.people.loc[id]

    def poseQuery(self, query: Query) -> pandas.core.frame.DataFrame:
        return self.people.query(str(query))

class Users:
    def __init__(self, csvName: str, sep: str = ",") -> None:
        self.users = pandas.read_csv(csvName, sep=sep, header=None).squeeze()

    def __str__(self) -> str:
        return str(self.users)

    def getUser(self, index: int) -> Id:
        return self.users[index]

    def addUser(self, id: Id) -> None:
        self.users = pandas.concat([self.users,pandas.Series(id)],ignore_index=True)

class Queries:
    def __init__(self, csvName: str, csvSep: str = ",", keyValueSep: str = "=") -> None: #Controllare se con file grandi questa procedura è troppo lenta
        records = {}
        with open(csvName, "r") as file:
            for line in file:
                record = {}
                splittedLine = (line[:-1] if line[-1] == "\n" else line).split(csvSep)
                for field in splittedLine[1:]:
                    key, value = field.split(keyValueSep)
                    record[key] = value
                records[splittedLine[0]] = record

        self.queries = pandas.read_json(io.StringIO(json.dumps(records)))
    
    def __str__(self) -> str:
        return str(self.queries)

    def getQuery(self, id: Id) -> Query:
        return Query(self.queries[id])

    def addQuery(self, query: Query) -> None:
        self.queries[query.name] = query.values

class UtilityMatrix:
    def __init__(self, csvName: str, sep: str = ",") -> None:
        self.um = pandas.read_csv(csvName, sep=sep)

    def __str__(self) -> str:
        return str(self.um)

    def getScore(self, queryId: Id, userId: Id) -> Score:
        return self.um[queryId][userId]
        
    def getQueryScores(self, id: Id) -> pandas.core.series.Series:
        return self.um[id]
    
    def getUserScores(self, id: Id) -> pandas.core.series.Series:
        return self.um.loc[id]

    def setScore(self, userId: Id, queryId: Id, score: Score) -> None:
        self.um[queryId][userId] = score

    def addEmptyQuery(self, id: Id) -> bool:
        self.um[id] = [NaN for i in range(self.um.shape[0])]

    def addEmptySeries(self, id: Id) -> bool:
        self.um.loc[id] = [NaN for i in range(self.um.shape[1])]