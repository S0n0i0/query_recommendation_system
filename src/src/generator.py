from data_struct import *
from functions import *

import pandas as pd
import random
from faker import Faker
from numpy import NaN
from math import sqrt

#initialize Faker
fake = Faker(['it_IT', 'en_US'])
#Faker.seed(12345)
#random.seed(12345)

#Configuration
#number of users, people and queries
num_users = 10
num_people = 50
num_queries = 10
#user profiles informations
high_grades = {
    "minMu": 80,
    "maxMu": 100,
    "minSd": 1,
    "maxSd": 10,
    "lenProp": random.uniform(0,1),
    "randomLen": True,
    "everyone": {}
}
low_grades = {
    "minMu": 20,
    "maxMu": 40,
    "minSd": 1,
    "maxSd": 10,
    "lenProp": random.uniform(0,1),
    "randomLen": True,
    "everyone": {}
}
average_grades = [Normal(50,5)]
#
alsoNan = True

#create a dataframe for the users
users = Users(pd.Series(['u{}'.format(i) for i in range(num_users)]))


#create a dataframe for the people
people = People(pd.DataFrame({'id': ['p{}'.format(i) for i in range(num_people)], #Rimettere 'id' come index in caso si voglia tornare in quel modo
                        'name': [fake.first_name() for _ in range(num_people)],
                        'surname': [fake.last_name() for _ in range(num_people)],
                        'address': [strWithoutChar(fake.city,"(\\n|,|'|\")") for _ in range(num_people)],
                        'age': [random.randint(10, 90) for _ in range(num_people)],
                        'occupation': [strWithoutChar(fake.job,"('|,|'|\")") for _ in range(num_people)]}))

usersProfile: dict[str,UserProfile] = {}
for i in users.users[0]:
    usersProfile[i] = UserProfile(people,
                                    Conditions(Normal(random.uniform(high_grades['minMu'],high_grades['maxMu']),random.uniform(high_grades['minSd'],high_grades['maxSd'])),
                                                elementsProp=high_grades['lenProp'],randomLen=high_grades['randomLen'],specialCases=high_grades['everyone']),
                                    Conditions(Normal(random.uniform(low_grades['minMu'],low_grades['maxMu']),random.uniform(low_grades['minSd'],low_grades['maxSd'])),
                                                elementsProp=low_grades['lenProp'],randomLen=low_grades['randomLen'],specialCases=low_grades['everyone']),
                                    average_grades)

persona_rating = pd.DataFrame([[randomElement(randomSourceFn=random.uniform,args=[0,100],alsoNaN=False) for _ in range(num_people)] for _ in range(num_users)],
                                users.users,people.people.index)
'''
   u0   u1
p1 50    nan
p2 100   nan
p3 nan  30
'''

#create a dataframe for the queries
queries = Queries(pd.DataFrame({'id': [randomElement(people.getColumnSubset('id'),rndFormattedInt,[num_queries,num_queries*2,"p{}"],alsoNaN=True) for _ in range(num_queries)],
                        'name': [None for _ in range(num_queries)],
                        'surname': [None for _ in range(num_queries)],
                        'address': [None for _ in range(num_queries)],
                        'age': [None for _ in range(num_queries)],
                        'occupation': [None for _ in range(num_queries)]},
                        ['q{}'.format(i) for i in range(num_queries)]))

#create a dataframe for the utility matrix
utility_matrix = UtilityMatrix(pd.DataFrame([[None for _ in range(num_queries)] for _ in range(num_users)],users.values,queries.index.values))

 
        
populateUtilityMatrix(people, queries, users, persona_rating, utility_matrix, 0, 100)
print(utility_matrix)

baseFilesPath = "."

#save the dataframes to CSV files
people.toCsv(baseFilesPath + "/files/people.csv")

users.toCsv(baseFilesPath + "/files/users.csv")

queries.toCsv(baseFilesPath + "/files/queries.csv")

utility_matrix.toCsv(baseFilesPath + "/files/utility_matrix.csv")