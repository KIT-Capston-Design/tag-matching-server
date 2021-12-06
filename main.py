import json
import random
import time

from redis_init import rd
from word2vec import model


# Estimate Tag Similarity of All Users
def get_all_user_similarity():
    user_with_tag = {}  # user with tag dict
    rank = []  # weighted list
    user_keys = list(rd.keys("tag:user:*"))

    if (len(user_keys) < 2):
        print("Not Enough Users", flush = True)
        return False

    for key in user_keys:
        user_with_tag[key] = rd.smembers(key)

    for i in range(0, len(user_keys)):
        for j in range(i, len(user_keys)):
            if (i != j):
                first_user_tags = user_with_tag[user_keys[i]]
                second_user_tags = user_with_tag[user_keys[j]]
                rank.append((user_keys[i][4:], user_keys[j][4:], get_similarity(first_user_tags, second_user_tags)))

    return rank


# Select Two Users and Calculate Tag Similarity
def get_similarity(first_user_tags, second_user_tags):
    weight_sum = 0
    for first_user_tag in first_user_tags:
        for second_user_tag in second_user_tags:
            if first_user_tag in model.wv.vocab and second_user_tag in model.wv.vocab:
                weight_sum += model.wv.similarity(first_user_tag, second_user_tag)

    return weight_sum


# Select Most Similarity Two User And Insert in Redis
def get_matching_user(rank):
    matching = max(rank, key=lambda weight: weight[2])  # (user1, user2, weight)
    print(matching, flush = True)

    first_user = matching[0]
    second_user = matching[1]

    # Find Sokcet ID of Two User
    first_user_socket_id = rd.get(first_user)
    second_user_socket_id = rd.get(second_user)

    # Notify Socket ID of Two User to Node Server
    rd.publish("random_matching", json.dumps([first_user_socket_id, second_user_socket_id]))

    # Exclude Existing User in Redis
    rd.delete(matching[0], matching[1])
    rd.delete("tag:" + matching[0], "tag:" + matching[1])


if __name__ == "__main__":
    get_matching_user.count = 0  # static variable in get_matching_user

    while True:
        all_user = get_all_user_similarity()  # if user in redis is less than two, return false
        if all_user:
            get_matching_user(all_user)  # matching two user
        time.sleep(1)
