import pandas as pd
import random
from faker import Faker

#initialize Faker
fake = Faker(['it_IT', 'en_US'])

#set the number of users and people
num_users = 10
num_people = 10
num_queries = 10

#create a dataframe for the users
users = pd.DataFrame(index= ['u{}'.format(i) for i in range(num_users)])


#create a dataframe for the people
people = pd.DataFrame({'name': [fake.first_name() for i in range(num_people)],
                       'surname': [fake.last_name() for i in range(num_people)],
                       'address': [fake.address() for i in range(num_people)],
                       'age': [random.randint(10, 90) for i in range(num_users)]})

people = people.replace('\n', ' ', regex=True)


#create a dataframe for the queries
attr = ['people_id', 'name', 'address', 'age']

queries = pd.DataFrame({'people_id': ['people_id={}'.format(i) for i in range(num_queries)],
                        'name': ['name={}'.format(i) for i in range(num_queries)], 
                        'address': ['address={}'.format(i) for i in range(num_queries)],
                        'age': ['age={}'.format(i) for i in range(num_queries)]},
                        index= ['q{}'.format(i) for i in range(num_queries)])


#create a dataframe for the user_people_scores
user_people_scores = pd.DataFrame({'user_id': [random.randint(1, num_users) for i in range(num_users * num_people)],
                               'people_id': [random.randint(1, num_people) for i in range(num_users * num_people)],
                               'rating': [random.randint(1, 5) for i in range(num_users * num_people)]})



#create a dataframe for the utility matrix
data = {}

#add the scores
for i in range(num_queries):
    data.update({'q{}'.format(i): [random.randint(1, 100) for i in range(num_users)]})

utility_matrix = pd.DataFrame(data, index=['u{}'.format(i) for i in range(num_users)])


#save the dataframes to CSV files
users.to_csv('users.csv', header=False)
people.to_csv('people.csv')
queries.to_csv('queries.csv')
utility_matrix.to_csv('utility_matrix.csv')

#preview the dataframes
#print(users)
#print(people)
#print(utility_matrix)