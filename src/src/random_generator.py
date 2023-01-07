from data_struct import *
from functions import *

import pandas as pd
import random
from faker import Faker
from numpy import NaN

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
                        'name': [fake.first_name() for _ in range(num_people)],
                        'surname': [fake.last_name() for _ in range(num_people)],
                        'address': [strWithoutChar(fake.city,"(\\n|,|'|\")") for _ in range(num_people)],
                        'age': [random.randint(10, 90) for _ in range(num_people)],
                        'occupation': [strWithoutChar(fake.job,"('|,|'|\")") for _ in range(num_people)]}))

#create a dataframe for the queries
queries = Queries(pd.DataFrame({'id': [randomElement(people.getColumnSubset('id'),rndFormattedInt,[num_queries,num_queries*2,"p{}"],alsoNaN=True) for _ in range(num_queries)],
                        'name': [randomElement(people.getColumnSubset('name'),fake.first_name,alsoNaN=True) for _ in range(num_queries)],
                        'surname': [randomElement(people.getColumnSubset('name'),fake.last_name,alsoNaN=True) for _ in range(num_queries)],
                        'address': [randomElement(people.getColumnSubset('address'),strWithoutChar,[fake.city,"(\\n|,)"],alsoNaN=True) for _ in range(num_queries)],
                        'age': [randomElement(people.getColumnSubset('age'),random.randint,[10,90],alsoNaN=True) for _ in range(num_queries)],
                        'occupation': [randomElement(people.getColumnSubset('occupation'),strWithoutChar,[fake.job,","],alsoNaN=True) for _ in range(num_queries)]},
                        ['q{}'.format(i) for i in range(num_queries)]))


#create a dataframe for the utility matrix
utility_matrix = UtilityMatrix(pd.DataFrame([[randomElement(randomSourceFn=random.uniform,args=[0,100],alsoNaN=True) for _ in range(num_queries)] for _ in range(num_users)],users.values,queries.index.values))

baseFilesPath = "."

#save the dataframes to CSV files
people.toCsv(baseFilesPath + "/files/people.csv")

users.toCsv(baseFilesPath + "/files/users.csv")

queries.toCsv(baseFilesPath + "/files/queries.csv")

utility_matrix.toCsv(baseFilesPath + "/files/utility_matrix.csv")