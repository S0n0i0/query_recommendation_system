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
        res = existingSource[random.randint(0,existingSource.size)-1]
    elif choice == 1:
        res = randomSourceFn(*args)
    else:
        return None
    
    return res if template == None else template.format(res)

#initialize Faker
fake = Faker(['it_IT', 'en_US'])
Faker.seed(12345)

#set the number of users and people
num_users = 10
num_people = 10
num_queries = 10

#create a dataframe for the users
users = pd.DataFrame(['u{}'.format(i) for i in range(num_users)])


#create a dataframe for the people
people = pd.DataFrame({'name': [fake.name() for _ in range(num_people)],
                       'address': [rndNoChar(fake.address,"(\\n|,)") for _ in range(num_people)],
                       'age': [random.randint(10, 90) for _ in range(num_people)],
                       'occupation': [rndNoChar(fake.job,",") for _ in range(num_people)]},
                       pd.Index(['p{}'.format(i) for i in range(num_people)],name="id"))


#create a dataframe for the queries
queries = pd.DataFrame({'id': [randomElement(people.index,random.randint,[num_queries,num_queries*2],'id={}',True) for _ in range(num_queries)],
                        'name': [randomElement(people['name'],fake.name,[],'name={}',True) for _ in range(num_queries)], 
                        'address': [randomElement(people['address'],rndNoChar,[fake.address,"(\\n|,)"],'address={}',True) for _ in range(num_queries)],
                        'age': [randomElement(people['age'],random.randint,[10,90],'age={}',True) for _ in range(num_queries)],
                        'occupation': [randomElement(people['occupation'],rndNoChar,[fake.job,","],'occupation={}',True) for _ in range(num_queries)]},
                        ['q{}'.format(i) for i in range(num_queries)])


#create a dataframe for the utility matrix
utility_matrix = pd.DataFrame([[randomElement(randomSourceFn=random.uniform,args=[0,100],alsoNaN=True) for _ in range(num_queries)] for _ in range(num_users)],users[0].values,queries.index.values)

baseFilesPath = "."

#save the dataframes to CSV files
people.to_csv(baseFilesPath + "/files/people.csv")

users.to_csv(baseFilesPath + "/files/users.csv", header=False, index=False)

with open(baseFilesPath + "/files/queries.csv", "w") as f:
    queryDict = queries.to_dict("index")
    for i in queryDict:
        f.write(i)
        for param in queryDict[i]:
            if queryDict[i][param] != None:
                f.write("," + str(queryDict[i][param]))
        f.write("\n")

with open(baseFilesPath + "/files/utility_matrix.csv","w",newline='') as f:
    f.write(utility_matrix.to_csv()[1:])