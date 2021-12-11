#!/usr/bin/env python3

def splitMatrixID(matrix_id):
    if matrix_id[0] != '@' or matrix_id.count(':') != 1:
        print('The user\'s matrix ID should be something like @user:domain')
        return None, None
    [username, server] = matrix_id.split(':')
    username = username[1:]
    return username, server

def getAccessToken(base_url, server, username, password):
    print('Logging in...')
    login = requests.post('{}/login'.format(base_url),
                        json = { 'type': 'm.login.password',
                                   'user': username,
                                   'password': password })
    if login.status_code != 200:
        print('Login on matrix server {} failed!'.format(server))
        print(login.text)
        return None
    print('Successfully logged in !')
    return login.json()['access_token']

def changeDisplayName(base_url, access_token, room_id, matrix_id, display_name):
    params = { 'access_token': access_token }
    print('Changing display name...')
    room_member = requests.put('{}/rooms/{}/state/m.room.member/{}'
                               .format(base_url, room_id, matrix_id),
                               params = params,
                               json = { 'membership': 'join',
                                        'displayname': display_name})
    if room_member.status_code != 200:
        print('Failed to update displayname in room {}!'.format(room_id))
        print(room_member.text)
    else:
        print('Succesfully changed display name in room {}'.format(room_id))

def logOut(base_url, access_token):
    params = { 'access_token': access_token }
    print('Logging out...')
    logout = requests.post('{}/logout'.format(base_url), params = params)
    if logout.status_code != 200:
        print('Failed to logout...')

if __name__ == '__main__':
    import argparse, json, requests
    from getpass import getpass
    from sys import exit

    parser = argparse.ArgumentParser(description='Set the displayname in a matrix room.')
    parser.add_argument('-s', '--server', help='The server name');
    parser.add_argument('-p', '--password', help='The user\'s password (not recommended)');
    parser.add_argument('matrix_id', help='The user\'s matrix ID (e.g @user:domain)');
    parser.add_argument('display_name', help='The new display name to use');
    parser.add_argument('room_id', help='The room ID where to change the display name');
    args = parser.parse_args()

    [username, server] = splitMatrixID(args.matrix_id)
    if not username or not server:
        exit(1)
    if not args.password:
        args.password = getpass()
    if args.server:
        server = args.server
    base_url = 'https://{}/_matrix/client/r0'.format(server)

    access_token = getAccessToken(base_url, server, username, args.password)
    if not access_token:
        exit(1)

    changeDisplayName(base_url, access_token, args.room_id, args.matrix_id, args.display_name)
    logOut(base_url, access_token)
    print('Bye !')
