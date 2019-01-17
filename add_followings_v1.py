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


time_delay = (10, 30)
def sleep():
    time.sleep(random.randint(*time_delay))


sleep()
if not api.login():
    raise Exception("Can't login!")


users_to_following_filename = 'users_to_following.txt'
with open(users_to_following_filename, 'r', encoding='utf-8') as f:
    users_to_following = [x.strip() for x in f.read().splitlines()]


with open('dict.txt','r', encoding='utf-8') as f:
    dict = [x.strip().lower() for x in f.read().splitlines()]


def is_correct_for_dict(user):
    lower_fullname = user[2].lower()
    return any([x in lower_fullname for x in dict])


def get_correct_fullname_users(users):
    correct = set(filter(is_correct_for_dict,users))
    not_correct = users - correct
    return list(correct), list(not_correct)


write_pattern = '{:<20}{:<40}{:<50}{:<15}{:<15}\n'
def write_txt_users(filename, users, do_follow=False):
    if not os.path.isfile(filename):
        with open(filename,'w', encoding='utf-8') as f:
            f.write(write_pattern.format('ID;', 'username;', 'full_name;', 'followers;', 'followings;'))

    with open(filename,'a', encoding='utf-8') as f:

        size_users = len(users)
        for i in range(size_users):

            sys.stdout.write('\r{} : {}/{}'.format(filename, i+1, size_users))
            sys.stdout.flush()

            if do_follow:
                sleep()
                api.follow(users[i][0])

            sleep()
            api.getUsernameInfo(users[i][0])

            follower_count = api.LastJson['user']['follower_count']
            following_count = api.LastJson['user']['following_count']

            userinfo = [x + ';' for x in list(users[i])+[str(follower_count), str(following_count)]]

            f.write(write_pattern.format(*userinfo))
            f.flush()
        print()


if __name__ == '__main__':

    try:
        max_followings = 100
        size_users_to_following = len(users_to_following)
        max_followings = max_followings if size_users_to_following >= max_followings else size_users_to_following

        datetime_msk = datetime.datetime.now(datetime.timezone(datetime.timedelta(seconds=10800), 'MSK'))
        datetime_str = '{:02d}-{:02d}-{:04d}_{:02d}-{:02d}-{:02d}'.\
            format(datetime_msk.day,datetime_msk.month,datetime_msk.year,datetime_msk.hour,datetime_msk.minute,datetime_msk.second)

        i = 0
        while i < max_followings and len(users_to_following) > 0:

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

                sleep()
                print('Getting total followers...')
                followers_of_user = [(str(x['pk']), x['username'], x['full_name']) for x in api.getTotalFollowers(user[0])]

                sleep()
                print('Getting total followings...')
                followings_of_user = [(str(x['pk']), x['username'], x['full_name']) for x in api.getTotalFollowings(user[0])]

                union_of_users = set(followers_of_user + followings_of_user)
                print('Count all users (followers+followings): {}'.format(len(union_of_users)))

                correct, not_correct = get_correct_fullname_users(union_of_users)

                write_txt_users('correct_{}.txt'.format(datetime_str), correct, True)
                write_txt_users('not_correct_{}.txt'.format(datetime_str), not_correct)

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
