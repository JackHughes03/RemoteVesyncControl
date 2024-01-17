from pyvesync import VeSync
import PySimpleGUI as sg
import keyring

manager = VeSync('', '')
window = sg.Window('Purifier', [])
autologgedin = False


def save_credentials(username, password):
    keyring.set_password('VeSync', 'username', username)
    keyring.set_password('VeSync', username, password)


def get_credentials():
    username = keyring.get_password('VeSync', 'username')
    password = keyring.get_password('VeSync', username)
    return username, password


def loginauto():
    global manager

    username, password = get_credentials()

    if username and password:
        manager = VeSync(username, password)
        manager.login()
        manager.update()
        global autologgedin
        autologgedin = True


def loginfunc(username, password):
    global manager

    manager = VeSync(username, password)
    manager.login()
    manager.update()
    save_credentials(username, password)

    update_headers()

    return


def log_out():
    print("Logging out")

    save_credentials('', '')

    global autologgedin
    autologgedin = False

    window['-LOGIN-'].update("Logged out")
    window['-NAME-'].update('')
    window['-STATUS-'].update('')
    window['-MODE-'].update('')
    window['-FILTER-'].update('')

    update_headers()

    return


def update_headers():
    window['-NAME-'].update(manager.fans[0].device_name)
    window['-LOGIN-'].update("Logged in")
    window['-STATUS-'].update(manager.fans[0].device_status)

    if manager.fans[0].mode == 'sleep':
        window['-MODE-'].update('Sleep')
    else:
        window['-MODE-'].update(manager.fans[0].fan_level)

    window['-FILTER-'].update(manager.fans[0].filter_life)


def setgui():
    sg.theme('DarkBlue14')

    layout = [
        [sg.Text('Username', size=(15, 1)), sg.InputText(size=(20, 1))],
        [sg.Text('Password', size=(15, 1)), sg.InputText(size=(20, 1))],
        [sg.Button('Login', size=(10, 1), border_width=0), sg.Text('', key='-LOGIN-', size=(20, 1))],

        [sg.Text('Name:', size=(15, 1)), sg.Text('', key='-NAME-', size=(20, 1))],
        [sg.Text('Status:', size=(15, 1)), sg.Text('', key='-STATUS-', size=(20, 1))],
        [sg.Text('Mode:', size=(15, 1)), sg.Text('', key='-MODE-', size=(20, 1))],
        [sg.Text('Filter life:', size=(15, 1)), sg.Text('', key='-FILTER-', size=(20, 1))],

        [sg.Button('Turn on', size=(10, 2), button_color=('white', '#111111'), pad=((5, 5), (10, 10)), border_width=0),
         sg.Button('Turn off', size=(10, 2), button_color=('white', '#111111'), pad=((5, 5), (10, 10)),
                   border_width=0)],

        [sg.Button('High', button_color=('white', '#111111'), border_width=0),
         sg.Button('Medium', button_color=('white', '#111111'), border_width=0),
         sg.Button('Low', button_color=('white', '#111111'), border_width=0),
         sg.Button('Sleep', button_color=('white', '#111111'), border_width=0)],

        [sg.Button('Light 0', button_color=('white', '#111111'), border_width=0),
         sg.Button('Light 1', button_color=('white', '#111111'), border_width=0),
         sg.Button('Light 2', button_color=('white', '#111111'), border_width=0)],

        [sg.Button('Quit', button_color=('white', '#111111'), border_width=0)],
        [sg.Button('Log out', size=(10, 1), border_width=0)],
    ]

    global window
    window = sg.Window('Purifier', layout)

    auto_login_done = False

    while True:
        if not auto_login_done:
            loginauto()
            auto_login_done = True

        event, values = window.read(timeout=100)
        if autologgedin:
            update_headers()

        if event == sg.WIN_CLOSED or event == 'Quit':
            break

        actions = {
            'Turn on': lambda: manager.fans[0].turn_on(),
            'Turn off': lambda: manager.fans[0].turn_off(),
            'High': lambda: manager.fans[0].change_fan_speed(3),
            'Medium': lambda: manager.fans[0].change_fan_speed(2),
            'Low': lambda: manager.fans[0].change_fan_speed(1),
            'Sleep': lambda: manager.fans[0].sleep_mode(),
            'Username': lambda: manager.username,
            'Password': lambda: manager.password,
            'Login': lambda: loginfunc(values[0], values[1]),
            'Light 0': lambda: manager.fans[0].set_night_light('off'),
            'Light 1': lambda: manager.fans[0].set_night_light('dim'),
            'Light 2': lambda: manager.fans[0].set_night_light('on'),
            'Log out': lambda: log_out(),
        }

        if event in actions:
            actions[event]()
            update_headers()

    window.close()


setgui()
