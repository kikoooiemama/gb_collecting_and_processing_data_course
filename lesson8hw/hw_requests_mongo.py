from pymongo import MongoClient

client = MongoClient('192.168.1.76', 27017)
db = client['instagram']
users = db.users


# Вывести всех юзеров на экран
def print_users(collection):
    print("Users in base:")
    for i in collection.find({}, {'user_name': 1, 'user_id': 1, '_id': 0}):
        print(f"    {i}")
    print()


# 5) Написать запрос к базе, который вернет список подписчиков только указанного пользователя
def followers_list_request(collection, user_id):
    followers_dict = collection.find({'user_id': user_id}, {"followers": 1, "_id": 0})[0]
    return followers_dict.get('followers')


# 6) Написать запрос к базе, который вернет список профилей, на кого подписан указанный пользователь
def followings_list_request(collection, user_id):
    followings_dict = collection.find({'user_id': user_id}, {"followings": 1, "_id": 0})[0]
    return followings_dict.get('followings')


# Проверить все ли данные(подписки, подписчики) попали в базу
def check_amount_follows(collection):
    for i in collection.find({},
                             {'user_name': 1, 'user_id': 1, 'user_followings_n': 1, 'user_followers_n': 1, '_id': 0}):
        n_followers = len(followers_list_request(collection, i['user_id']))
        n_followings = len(followings_list_request(collection, i['user_id']))
        print(f"User: {i['user_name']}, Id:{i['user_id']}")
        print(f"    N_followers: {i['user_followers_n']}, Followers in base: {n_followers}")
        print(f"    N_followings: {i['user_followings_n']}, Followings in base: {n_followings}")
        print()


user_id = 45214393367

print_users(users)

# followers_list = followers_list_request(users, user_id)
# pprint(followers_list)

# followings_list = followings_list_request(users, user_id)
# pprint(followings_list)

check_amount_follows(users)
