# nhentai downloader
# Date modified: May 13, 2022

from src import *

# Do not edit
default_config = r"""
#Keys and values are to be provided in a [<key> = "<value>"] format.
#   The spaces, = and the quotes are a must. The line is read and is stored into a config dict as <key>:<value> pairs where both the key and value are strings.
#   Keys may contain only upper/lower english alphabets. Any double quote inside the value must preceded by a \(backslash).
#   If a line starts with a non alphabetic character then that line is considered commented, but preferably use # to indicate comments
#   Very Important Note: The first line should always be a newline if you manually create a config file.

#Set file name structure
#   Possible identifiers are {Id}, {Name}. Example: *name = "{Id}-{Name}"* will name the file as its id followed by its name with a "-" in between
name = "" 

#Set Path for output folder, defaults to %cwd%\hentai if left blank. Example: *path = ".\hentai"* means a hentai folder 
#   where this file exists or you can just use the absolute path
path = "" 

#Set Location of text file containing Ids/webpage URLs. Ids must be separated by any delimiter. URLs need nothing
#   It will read the largest consecutive group of numbers as 1 Id hence why Ids must be separated
batch = ""

#Set how many pages are downloaded at once, defaults to 1 if empty. Recommended max threads is 4.
threads = ""

#Sets the file type of the final output. Available types are pdf, cbz, cbt, cbz, img. Case-Sensitive. 
#   img will loosely save the files, i.e save the png files as-is in a folder named after the naming scheme.
#   Defaults to pdf for empty/any other value.
type = "pdf"

#Set the name of the log file. Defaults to history
log = ""

#Set to True to minimal printing which can reduces clutter. Any other value is considered False
minimal = "False"

#Parameters below are manually created
"""

P = re.compile(r'\d+|set\s\w+\s".+"|help|open|done|exit')
P_set = re.compile(r'set\s(\w+)\s"(.+)"')

def show_help(): print(open('help.txt').read())

def open_folder(folder_path: str):
    # Check to see if path exist
    if not os.path.exists(folder_path):
        os.mkdir(folder_path)
    if platform == "darwin":
        os.system(f'open {folder_path}/')
    elif platform == "win32":
        os.system(f'start {folder_path}\\')

# Process current queue
def process_queue(dl_queue, output_folder, temp_folder):
    global path_handler, dl_handler, history_log
    for currPos, id_num in enumerate(dl_queue, 1):
        # Create log statement
        log_statement = f'{datetime.datetime.now()} | ID: {id_num} '

        # Get doujin info
        print(f'[ Fetching {id_num} ({currPos} / {len(dl_queue)}) ]')
        dl_handler = DownloadHandler(id_num, config['type'])
        if not dl_handler.valid:
            print('ERROR - Doujin not found. Skipped\n')
            log_statement += '[ERROR] Doujin not found.\n'
            history_log.write(log_statement)
            continue
        print(f'Title: {dl_handler.title}')
        print(f'Pages: {dl_handler.pages}')

        path_handler = PathHandler(output_folder, temp_folder, dl_handler.title, id_num, config)
        if valid_path(temp_folder): continue #returns True if file alr exists so skip iter

        images = {}
        history_log.write("\n[ DOWNLOADING ] [START]")
        download_start(images) #Starts downloading
        history_log.write("\n[ DOWNLOADING ] [END]\n[ CONVERSION ] [START]")
        
        save_file(images) #Converts the downloaded files
        history_log.write(f"\n[ CONVERSION ] [SUCCESS] {path_handler.final_path}")
        
        m_print(f"Completed conversion!\nSaved at {path_handler.final_path}")

        # Remove temp images
        m_print("[ Removing Temp Data ]")
        shutil.rmtree(temp_folder)
        if platform == "win32":
            print("Done!\n")
            sleep(2)
            os.system('cls')
        else:
            print("Done ✅\n")

        try:
            history_log.write(f'\n{log_statement}[SUCCESS] {dl_handler.title}.\n')
        except:
            # In case a unicode character cannot be written to history log.
            history_log.write(f'\n{log_statement}[SUCCESS] [LOG ERROR] Title could not be recorded due to bad character.\n')
        history_log.flush()


def download_start(images):
        """
        Threading stuff below
        - The working_on variable is used to store a dict and update the screen to show which thread
          is downloading which file at a given time, basically what a thread is working on atm
        - Images was changed into a dict(was a list before) so that the order of pages is maintained
        - The threads list stores the threads created
        - The Count list variable stores the number of pages downloaded
        """
        history_log.write('\n[ THREADING ] [ START ]')

        # Queue to feed downloader
        page_queue = Queue()
        history_log.write(f'\n[THREADING] [TASK] Adding {dl_handler.pages} to queue.')
        for i in range(1, dl_handler.pages + 1): page_queue.put(i)

        working_on, Count = {i: None for i in range(config["threads"])}, [0]

        def helper(images, thread_num, working_on, Count):
            while not page_queue.empty():
                p = page_queue.get()
                history_log.write(f'\n[THREADING] [Thread {thread_num}] working on page {p}')
                working_on[thread_num] = p  # Set which page thread is working on
                # Fetch each image link of the gallery
                img_path = dl_handler.save_image(p, path_handler.temp_path)
                # Add to list of images for conversion later
                images[p], Count[0] = img_path, Count[0] + 1
                if exit_event.is_set(): break
            
            history_log.write(f'\n[THREADING] [Thread {thread_num}] exiting')
            working_on[thread_num] = "Done"

        history_log.write(f"\n[THREADING] [TASK] Creating {config['threads']} threads")

        global threads  # Made a global variable so as to make it gracefully terminate on KeyboardInterrupt
        threads = []
        for i in range(config['threads']):
            threads += [threading.Thread(target=helper, daemon=True, args=(images, i, working_on, Count), name = str(i))]

        for i in threads: i.start()

        # Prints current download status
        borders = '+------------+' + '-----+' * config["threads"] + '-----+-----+----------+'
        print(borders, "\n|Thread ID : |" + '|'.join(
            "{:>5}".format(i) for i in range(config["threads"])) + '|Dwnl.|Total|Completed%|', '\n' + borders)
        template = "|On Page Num:|" + '{:>5}|' * (config["threads"] + 2) + '{:>10}' + '|\r'
        old_working_on = {i: working_on[i] for i in working_on}
        print(template.format(*[working_on[i] for i in range(config["threads"])] + [0, dl_handler.pages, 0]), end='')

        while any((i.is_alive() for i in threads)):  # Check if threads have terminated
            if working_on != old_working_on:  # Updates the screen only if a thread moves on to the next page
                print(template.format(*[working_on[i] for i in range(config["threads"])]
                                       + [Count[0], dl_handler.pages,
                                          '{:.2f}'.format(100 * Count[0] / dl_handler.pages)]), end='')
                old_working_on.update(working_on)
        print(template.format(*(['Done' for _ in range(config["threads"])] + [Count[0], dl_handler.pages, '100.00'])),
              '\n' + borders)
        
        history_log.write('\n[ THREADING ] [ END ]')
        history_log.flush()

def valid_path(temp_folder):
        # Check to see if file exist
        if not path_handler.unique:
            print("ERROR - File already exist. Skipped.\n")
            history_log.write('[PATH] [ERROR] File already exist.\n')
            return True
        # Check to see if path is too long
        while not path_handler.valid or not path_handler.unique:
            while not path_handler.valid:
                title = input(
                    "⚠️   WARNING - File path is too long! Please enter new file name: ")
                path_handler.rename_path(title)
            while not path_handler.unique:
                title = input(
                    "⚠️   WARNING - File name already exist! Please enter another name: ")
                path_handler.rename_path(title)

        # Begin download images
        print("[ Downloading ]")
        if not os.path.exists(output_folder):
            os.mkdir(output_folder)
        if not os.path.exists(temp_folder):
            os.mkdir(temp_folder)
        if os.path.exists(path_handler.temp_path):
            shutil.rmtree(path_handler.temp_path)
        os.mkdir(path_handler.temp_path)

def save_file(images):
    if config["type"] == 'pdf':
        # Convert to PDF
        m_print("[ Converting to PDF ]")
        images = [Image.open(images[it_img + 1]) for it_img in range(dl_handler.pages)]
        pdf_handler = PDFHandler()
        pdf_handler.save_to_pdf(images, path_handler.final_path)

    elif config['type'] == 'img':  # Unpacked handling
        os.rename(path_handler.temp_path, path_handler.file_name)
        shutil.move(path_handler.file_name, path_handler.path_dir)

    else:  # CBx handling
        print(f'[ Converting to {config["type"].upper()} ]')
        file = ZipFile(path_handler.final_path, 'w')
        cwd = os.getcwd()
        os.chdir(path_handler.temp_path)
        for i in images:
            new_name = f"{images[i]}".zfill(8)
            os.rename(f"{images[i]}", new_name)
            file.write(new_name)
        os.chdir(cwd)
        file.close()

def get_command(output_folder, temp_folder, batch=""):
    input_prompt = "Enter ID(s)/webpage URL(s)/Command: "
    #Fn used to get input, defaults to ['retry'] if no input is provided
    get_input = lambda : [i for i in P.findall(input(input_prompt)) if i] or ['retry']
    num_input = batch if batch else get_input()
    while num_input[0] not in ("done", "exit"):
        if P_set.match(num_input[0]): 
            update_config(num_input[0])
        elif num_input[0] == 'retry': 
            num_input = get_input()
            continue
        elif num_input[0] == "open":
            open_folder(output_folder)
            print()
        elif num_input[0] == "help":
            show_help()
        else:
            process_queue(num_input, output_folder, temp_folder)
        # Ask for more input
        num_input = get_input()

def update_config(cmd): #Update existing/add new parameters in config from console using set command
    cmd = P_set.findall(cmd)[0]
    history_log.write("\n[ CONFIG ] [ UPDATE ] Command: '{cmd}'")

    f = open('config.txt').read()

    if re.findall(rf'{cmd[0]} = ".*"', f): #If parameter exists in config.txt, update existing
        content = re.sub(rf'{cmd[0]} = ".*"', rf'{cmd[0]} = "{cmd[1]}"', f)
    else: #Otherwise add new parameter
        content = f + f'\n{cmd[0]} = "{cmd[1]}"'

    open('config.txt', 'w').write(content)

    config[cmd[0]] = cmd[1] #Updates value in the already read config variable
    print('Done Successfully')
    history_log.write("\n[ CONFIG ] [ UPDATE ] [ SUCCESS ]")
    history_log.flush()

def parse_config(): #Parse and check parameters in config.txt into a dict called config
    f = open('config.txt').read()

    # Read into a dict
    config = defaultdict(lambda: None, {i: (j or None) for i, j in re.findall(r'\n([A-Za-z]+) = "(.*)"', f)})

    global minimal
    minimal = config["minimal"]

    m_print('To enable minimal printing which can reduces clutter, set \'minimal = "True"\' in config \n')

    # Name and output folder check
    if config["path"] is None:
        m_print("No output path has been set, defaulting to cwd")
        config["path"] = os.path.join(os.getcwd(), 'hentai')
    if config["name"] is None:
        m_print("No naming structure has been provided, defaulting to id")
        config["name"] = "{Id}"
    m_print()
    m_print("Output folder is", config["path"])
    m_print("File structure is", config["name"], "\n")

    # File format
    if config['type'] is None or config['type'].lower() not in ('pdf', 'cbt', 'cbz', 'cbr', 'img'):
        config['type'] = 'pdf'
    m_print("Doujin will be saved as a", config['type'].upper(), 'file.\n')

    # Threads
    if config["threads"] is None:
        config["threads"] = 1
    else:
        config["threads"] = int(config["threads"])
    m_print("Threads for downloading:", config["threads"], '\n')

    # Batch downloading parse + check
    batch = None
    if config["batch"] is None:
        m_print("Batch downloading has been turned off")
    else:
        m_print("Batch downloading has been turned on")
        m_print("Downloading from inputs provided in file at:", config["batch"])
        if os.path.exists(config['batch']):
            batch = re.findall(r"\d+", open(config['batch']).read())
            print("\nDownloading the following ids:", *batch, sep="\n")
            os.system("pause")
            # Cleanup
            open('config.txt', 'w').write(re.sub(r'batch = ".*"', r'batch = ""', f))
        else:
            m_print('Such a file {} does not exist, skipping batch download'.format(config['batch']))
    m_print()
    config["batch"] = batch

    if config["log"] is None: 
        m_print('No log file path has been set, defaulting to "history"')
        config["log"] = 'history'
    m_print(f"Logging file has been set to {config['log']}.log\n")

    #Add manual config parameters checks here

    return dict(config)

def m_print(*args, **kwargs): #Minimal Print = Used to print only the minimum amount of text to console
    if minimal != 'True':
        print(*args, **kwargs)

#Program Start
print("[ nhentai downloader pdf ]\n")

if os.path.exists('config.txt'): #Read Config
    config = parse_config()
else:
    open('config.txt', 'w').write(default_config)
    config = parse_config()

history_log = open(f'{config["log"]}.log', 'a+') #Logger start
history_log.write(f'[ START ]\n{datetime.datetime.now()} || Script Started')
history_log.write(f'\n{datetime.datetime.now()} || Config: {config}')

# Made a global variable so as to gracefully terminate on KeyboardInterrupt.
threads = []
exit_event = threading.Event()
exit_event.clear()

output_folder = config['path']
all_temp = os.path.join(output_folder, 'temp')

try:
    if config['batch']:
        get_command(output_folder, all_temp, config['batch'])
        config['batch'] = None
    else:
        print("Enter 'help' to see usage and commands\n")
        get_command(output_folder, all_temp)
except KeyboardInterrupt:
    exit_event.set()
    history_log.write(f'\n[ FATAL ] [ KeyboardInterrupt ] {datetime.datetime.now()}')
    print("\n\nWaiting for threads to terminate")
    for i in threads: 
        history_log.write(f'\n[ THREADING ] [ TERMINATION ] [ KeyboardInterrupt ] Waiting for thread num: {i.name} ...')
        i.join()
        history_log.write(f'| [SUCCESS]')
    print("Terminated successfully")
    history_log.write('\n[ THREADING ] [ TERMINATION ] [ SUCCESS ]')

if os.path.exists(all_temp):
    shutil.rmtree(all_temp)
    history_log.write('\n[ CLEANUP ] Temporary folders deleted')

history_log.write("\n[ END ]")
history_log.close()
print("\n---Program End---")
