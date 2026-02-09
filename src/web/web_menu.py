from termcolor import colored


def select_urls(visited_list):
    if not visited_list:
        return []

    selected = [True for _ in visited_list]

    def print_menu():
        print(colored('\nDiscovered URLs:', 'cyan', attrs=['bold']))
        for i, u in enumerate(visited_list, 1):
            mark = 'X' if selected[i - 1] else ' '
            print(colored(f" [{mark}] {i}. {u}", 'white'))
        print(colored("\nCommands: 'all' (select all), 'none' (deselect all), numbers to toggle (e.g. 1 3 5), 'done' to continue", 'cyan'))

    try:
        while True:
            print_menu()
            cmd = input(colored('\nSelect URLs to test > ', 'blue')).strip().lower()
            if cmd in ('all', 'a'):
                selected = [True for _ in visited_list]
            elif cmd in ('none', 'n'):
                selected = [False for _ in visited_list]
            elif cmd in ('done', 'd'):
                break
            elif cmd == '':
                continue
            else:
                parts = [p for p in cmd.replace(',', ' ').split() if p]
                toggled = False
                for p in parts:
                    if p.isdigit():
                        idx = int(p) - 1
                        if 0 <= idx < len(selected):
                            selected[idx] = not selected[idx]
                            toggled = True
                if not toggled:
                    print(colored('Invalid input. Use numbers, all, none, or done.', 'red'))
    except (KeyboardInterrupt, EOFError):
        print(colored('\nSelection aborted, proceeding with defaults.', 'yellow'))

    chosen = [u for i, u in enumerate(visited_list) if selected[i]]
    return chosen
