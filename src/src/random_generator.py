from data_struct import *

import pandas as pd
import random
from faker import Faker
from numpy import NaN
import re

pdSeries = pd.core.series.Series
pdDataFrame = pd.core.frame.DataFrame

def rndNoChar(fnSource,toReplace: str,value: str = " "):
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

#initialize Faker
fake = Faker(['it_IT', 'en_US'])
Faker.seed(12345)
random.seed(12345)

#set the number of users and people
num_users = 10
num_people = 10
num_queries = 10

#create a dataframe for the users
users = Users(pd.Series(['u{}'.format(i) for i in range(num_users)]))


#create a dataframe for the people
people = People(pd.DataFrame({'id': ['p{}'.format(i) for i in range(num_people)], #Rimettere 'id' come index in caso si voglia tornare in quel modo
                        'name': [fake.name() for _ in range(num_people)],
                       'address': [rndNoChar(fake.address,"(\\n|,)") for _ in range(num_people)],
                       'age': [random.randint(10, 90) for _ in range(num_people)],
                       'occupation': [rndNoChar(fake.job,",") for _ in range(num_people)]}))

#create a dataframe for the queries
queries = Queries(pd.DataFrame({'id': [randomElement(people.getColumnSubset('id'),random.randint,[num_queries,num_queries*2],'id={}',True) for _ in range(num_queries)],
                        'name': [randomElement(people.getColumnSubset('name'),fake.name,[],'name={}',True) for _ in range(num_queries)], 
                        'address': [randomElement(people.getColumnSubset('address'),rndNoChar,[fake.address,"(\\n|,)"],'address={}',True) for _ in range(num_queries)],
                        'age': [randomElement(people.getColumnSubset('age'),random.randint,[10,90],'age={}',True) for _ in range(num_queries)],
                        'occupation': [randomElement(people.getColumnSubset('occupation'),rndNoChar,[fake.job,","],'occupation={}',True) for _ in range(num_queries)]},
                        ['q{}'.format(i) for i in range(num_queries)]))


#create a dataframe for the utility matrix
utility_matrix = UtilityMatrix(pd.DataFrame([[randomElement(randomSourceFn=random.uniform,args=[0,100],alsoNaN=True) for _ in range(num_queries)] for _ in range(num_users)],users.values,queries.index.values))

baseFilesPath = "."

#save the dataframes to CSV files
people.toCsv(baseFilesPath + "/files/people.csv")

users.toCsv(baseFilesPath + "/files/users.csv")

queries.toCsv(baseFilesPath + "/files/queries.csv")

utility_matrix.toCsv(baseFilesPath + "/files/utility_matrix.csv")