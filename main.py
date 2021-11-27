import random
import time

from redis_init import rd
from word2vec import model

count = 0


# 모든 사용자 태그 유사도 측정
def get_all_user_similarity():
    user_with_tag = {}  # user with tag dict
    rank = []  # weight 계산된 list
    user_keys = list(rd.keys("tag:user:*"))

    if (len(user_keys) < 2):
        print("매칭 사용자 부족")
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


# 사용자 2명 골라서 유사도 계산
def get_similarity(first_user_tags, second_user_tags):
    weight_sum = 0
    for first_user_tag in first_user_tags:
        for second_user_tag in second_user_tags:
            if first_user_tag in model.wv.vocab and second_user_tag in model.wv.vocab:
                weight_sum += model.wv.similarity(first_user_tag, second_user_tag)

    return weight_sum


# 가장 유사도 높은 사용자 2명 select && redis에 넣기
def get_matching_user(rank):
    matching = max(rank, key=lambda weight: weight[2])  # (user1, user2, weight)
    print(matching)

    first_user = matching[0]
    second_user = matching[1]

    # 사용자 2명의 socket id 찾기
    first_user_socket_id = rd.get(first_user)
    second_user_socket_id = rd.get(second_user)

    # matching set에 socket id 2개 넣기기
    matchig_key = "matching" + str(get_matching_user.count)
    get_matching_user.count += 1
    rd.sadd(matchig_key, first_user_socket_id, second_user_socket_id)  # insert

    # 기존 유저에서 제외
    rd.delete(matching[0], matching[1])
    rd.delete("tag:" + matching[0], "tag:" + matching[1])


if __name__ == "__main__":
    get_matching_user.count = 0 # get_matching_user 내에 static variable
    rd.publish("test", "hello")

    # while True:
    #     all_user = get_all_user_similarity()  # redis에 user 1명 이하면 false 반환
    #     if (all_user):
    #         get_matching_user(all_user)  # matching user 2명
    #     time.sleep(1)
