# -*- coding: utf-8 -*-

# import imageio
# imageio.plugins.ffmpeg.download()

from InstagramAPI import InstagramAPI
import time
import random
import sys
import datetime
import os


api = InstagramAPI("username", "password")
max_following_count = 300
time_delay = (10, 30)


datetime_msk = datetime.datetime.now(datetime.timezone(datetime.timedelta(seconds=10800), 'MSK'))
datetime_str = '{:02d}-{:02d}-{:04d}_{:02d}-{:02d}-{:02d}'.\
    format(datetime_msk.day,datetime_msk.month,datetime_msk.year,datetime_msk.hour,datetime_msk.minute,datetime_msk.second)
current_following_count = 0


def sleep():
    time.sleep(random.randint(*time_delay))


sleep()
if not api.login():
    raise Exception("Can't login!")


def unique(sequence):
    seen = set()
    return [x for x in sequence if not (x in seen or seen.add(x))]

users_to_following_filename = 'users_to_following.txt'
with open(users_to_following_filename, 'r', encoding='utf-8') as f:
    users_to_following = [x.strip() for x in f.read().splitlines()]
    users_to_following = unique(users_to_following)
    users_to_following = list(filter(None, users_to_following))

dict_filename = 'dict.txt'
with open(dict_filename, 'r', encoding='utf-8') as f:
    dict = [x.strip().lower() for x in f.read().splitlines()]
    dict = unique(dict)
    dict = list(filter(None, dict))


def is_correct_for_dict(user):
    lower_fullname = user[2].lower()
    return any([x in lower_fullname for x in dict])


def get_users_with_correct_fullname(users):
    correct = set(filter(is_correct_for_dict,users))
    not_correct = set(users) - correct
    return list(correct), list(not_correct)


write_small_pattern = '{:<20}{:<40}{:<50}\n'
def write_small_userinfo(sourse_userinfo, users_union):

    params = zip(['correct_{}_small.txt'.format(datetime_str), 'not_correct_{}_small.txt'.format(datetime_str)],
                 get_users_with_correct_fullname(users_union))

    for fn, users in params:
        if not os.path.isfile(fn):
            with open(fn, 'w', encoding='utf-8') as f:
                f.write(write_small_pattern.format('ID;', 'username;', 'full_name;'))

        with open(fn, 'a', encoding='utf-8') as f:
            f.write('\n' + sourse_userinfo + '\n')
            for user in users:
                userinfo = [x + ';' for x in list(user)]
                f.write(write_small_pattern.format(*userinfo))
                f.flush()


def append_text_in_file(filename, text):
    with open(filename, 'a', encoding='utf-8') as f:
        f.write(text)
        f.flush()


write_full_pattern = '{:<20}{:<40}{:<50}{:<15}{:<15}\n'
def write_full_userinfo(sourse_userinfo, users):
    global current_following_count
    filenames = ['correct_{}_full.txt'.format(datetime_str), 'not_correct_{}_full.txt'.format(datetime_str)]

    for fn in filenames:
        if not os.path.isfile(fn):
            with open(fn, 'w', encoding='utf-8') as f:
                f.write(write_full_pattern.format('ID;', 'username;', 'full_name;', 'followers;', 'followings;'))

        append_text_in_file(fn, '\n' + sourse_userinfo + '\n')

    size_users = len(users)
    i = 0
    while i < size_users and current_following_count < max_following_count:
        sys.stdout.write('\rProcessing {}/{}... Follow count: {}/{}'.
                         format(i + 1, size_users, current_following_count, max_following_count))
        sys.stdout.flush()

        sleep()
        api.getUsernameInfo(users[i][0])

        follower_count = api.LastJson['user']['follower_count']
        following_count = api.LastJson['user']['following_count']

        userinfo = [x + ';' for x in list(users[i]) + [str(follower_count), str(following_count)]]

        if is_correct_for_dict(users[i]):
            sleep()
            api.follow(users[i][0])
            current_following_count += 1
            append_text_in_file(filenames[0], write_full_pattern.format(*userinfo))
        else:
            append_text_in_file(filenames[1], write_full_pattern.format(*userinfo))
        i += 1
    print()


if __name__ == '__main__':

    try:
        i = 0

        while current_following_count < max_following_count and len(users_to_following) > 0:

            print('User №' + str(i+1) + ' : ' + users_to_following[0])

            sleep()
            if api.searchUsername(users_to_following[0]):

                if api.LastJson['user']['is_private']:
                    print('User "{}" has private profile!\n'.format(users_to_following[0]))
                    i += 1
                    users_to_following.pop(0)
                    continue

                user = [str(api.LastJson['user']['pk']), api.LastJson['user']['username'], api.LastJson['user']['full_name']]

                sleep()
                print('Follow...')
                api.follow(user[0])
                current_following_count += 1

                if not current_following_count < max_following_count:
                    print('\nFollowing count = {}!\nExit!'.format(current_following_count))
                    break

                sleep()
                print('Getting total user followers...')
                user_followers = [(str(x['pk']), x['username'], x['full_name']) for x in api.getTotalFollowers(user[0])]

                sleep()
                print('Getting total user followings...')
                user_followings = [(str(x['pk']), x['username'], x['full_name']) for x in api.getTotalFollowings(user[0])]

                sleep()
                print('Getting total self followings...')
                self_followings = [(str(x['pk']), x['username'], x['full_name']) for x in api.getTotalSelfFollowings()]

                users_union = list(set(user_followers + user_followings) - set(self_followings))
                print('Count all users: {}'.format(len(users_union)))

                write_small_userinfo('User №' + str(i+1) + ' : ' + users_to_following[0], users_union)
                write_full_userinfo('User №' + str(i+1) + ' : ' + users_to_following[0], users_union)

                if not current_following_count < max_following_count:
                    print('\nFollowing count = {}!\nExit!'.format(current_following_count))
                    break

            else:
                print('User "{}" is not found!'.format(users_to_following[0]))

            i += 1
            users_to_following.pop(0)
            print('\n')

    except BaseException as e:
        print(e.with_traceback())
    finally:

        users_to_following = filter(None, users_to_following)
        users_to_following = filter(lambda x: x.replace(' ', ''), users_to_following)

        with open(users_to_following_filename, 'w', encoding='utf-8') as f:
            f.write('\n'.join(users_to_following))

        print('\nCompleted!')
