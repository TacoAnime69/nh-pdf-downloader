# nhentai downloader
# Date modified: June 20, 2021

from io import TextIOWrapper
from re import findall, sub
from PIL import Image
from sys import platform
from zipfile import ZipFile
from collections import defaultdict
import os, shutil, datetime, threading

from src.DownloadHandler import DownloadHandler
from src.PathHandler import PathHandler
from src.PDFHandler import PDFHandler

# Do not edit
default_config = r"""
#Keys and values are to be provided in a [<key> = "<value>"] format.
#   The spaces, = and the quotes are a must. The line is read and is stored into a config dict as <key>:<value> pairs where both the key and value are strings.
#   Keys may contain only upper/lower english alphabets. Any double quote inside the value must preceded by a \(backslash).
#   If a line starts with a non alphabetic character then that line is considered commented, but preferably use # to indicate comments
#Very Important Note: The first line should always be a newline if you manually create a config file.
#Set file name structure
#   Possible identifiers are {Id}, {Name}. Example: *name = "{Id}-{Name}"* will name the file as its id followed by its name with a "-" in between
name = "" 
#Set Path for output folder, defaults to %cwd%\hentai if left blank. Example: *path = ".\hentai"* means a hentai folder 
#   where this file exists or you can just use the absolute path
path = "" 
#Set Location of text file containing Ids/webpage URLs. Ids must be separated by any delimiter. URLs need nothing
#It will read the largest consecutive group of numbers as 1 Id hence why Ids must be separated
batch = ""
#Set how many pages are downloaded at once, defaults to 1 if empty. Strongly do not recommend going above 6 threads
threads = ""
#Sets the file type of the final output. Available types are pdf, cbz, cbt, cbz, img. Case-Sensitive. 
#img will loosely save the files, i.e save the png files as-is in a folder named after the naming scheme.
#Defaults to pdf for empty/any other value.
type = "pdf"
"""

def open_folder(folder_path: str):
    if platform == "darwin":
        os.system(f'open {folder_path}/')
    elif platform == "win32":
        os.system(f'start {folder_path}\\')


def show_help():
    message = r"""
            nhentai downloader pdf - help
            [ Prompt Usage ]
            [ To Download ]
            - Enter in the ID number(s)/webpage URL(s) of the doujin you wish to download.
            Note: Doujins must come from nhentai website. 
                  This script will not work with any other site.
            Hint: ID numbers can be found in the URL. 
                  https://nhentai.net/g/[id number]/
            - To create a queue (multiple downloads) enter all the ID numbers
            Note: -The order of the ID's does not matter.
                  -ID(s) need any non numeric delimiter whether it be whitespace or hyphen or mixed, whereas URL(s) 
                   do not need any as each consecutive group of numbers is considered as one Id
            - Hit enter to begin downloading
            Note: If a doujin has the same name as an already downloaded item,
                  then it will skip that download.
                  If a doujin has a name that is too long, a warning will
                  appear and prompt to enter a new name.
            Usage:
            Enter ID(s)/webpage URL(s)/Command: [ID number(s)/webpage URL(s) ... ]
            Example:
            Enter ID(s)/webpage URL(s)/Command: 111111 222222,333333https://nhentai.net/g/444444https://nhentai.net/g/555555
            
            [ Batch Downloading from text file]
            -You can copy paste all the links of the doujins you want to download into a text file and set
             the value of batch in the config.txt to the path of this text file.
            Example: 
                Assume the text file "test.txt" in the same folder as the script has the following contents:
                    111111 222222https://nhentai.net/g/444444https://nhentai.net/g/555555
                    nhentai.net/g/666666
                Then all you have to do is set the value of the batch line to 
                    batch = ".\test.txt"
                and all the doujins posted will be downloaded when the script is run
            Note: The batch line in the config.txt will be reset every time the script is executed.
                
            [ Other Options ]
            When prompted, you may enter one of the other commands:
            - done : this will end execution of the program
            - help : this will display this text
            - open : this will open finder/files/file explorer to the
                     default download folder
            [ Threads ]
            - Set this option in the config file to specify how many pages of the same doujin are to be downloaded at once
            [ Type ]
            - Set this option in the config file to specify the file type that the doujins to be saved as(pdf, cbt, cbz, cbt, img i.e unpacked).
            """
    print(message)


# Process current queue
def process_queue(dl_queue, output_folder, temp_folder, log):
    for currPos, id_num in enumerate(dl_queue, 1):
        # Create log statement
        date = datetime.datetime.now()
        log_statement = f'{date} | ID: {id_num} '

        # Get doujin info
        print(f'[ Fetching {id_num} ({currPos} / {len(dl_queue)}) ]')
        dl_handler = DownloadHandler(id_num, config['type'])
        if not dl_handler.valid:
            print('ERROR - Doujin not found. Skipped\n')
            log_statement += '[ERROR] Doujin not found.\n'
            log.write(log_statement)
            continue
        print(f'Title: {dl_handler.title}')
        print(f'Pages: {dl_handler.pages}')

        # Check to see if file exist
        path_handler = PathHandler(output_folder, temp_folder, dl_handler.title, id_num, config)
        if not path_handler.unique:
            print("ERROR - File already exist. Skipped.\n")
            log_statement += '[ERROR] File already exist.\n'
            log.write(log_statement)
            continue
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

        """
        Threading stuff below
        - The working_on variable is used to store a dict and update the screen to show which thread
          is downloading which file at a given time, basically what a thread is working on atm
        - Images was changed into a dict(was a list before) so that the order of pages is maintained
        - The threads list stores the threads created
        - The Count list variable stores the number of pages downloaded
        - page_queue is a iterator used to feed page numbers to the threads so that once a thread finishes 
          its current page it can immediately move onto the next page that has not yet been completed.
        """

        # Queue to feed downloader
        page_queue = iter(range(1, dl_handler.pages + 1))

        images, working_on, Count = {}, {i: None for i in range(config["threads"])}, [0]

        def helper(pages, images, dl_handler, path_handler, thread_num, working_on, Count):
            for p in pages:
                working_on[thread_num] = p  # Set which page thread is working on
                # Fetch each image link of the gallery
                img_path = dl_handler.save_image(p, path_handler.temp_path)
                # Add to list of images for conversion later
                images[p], Count[0] = img_path, Count[0] + 1
                if not exit_event.is_set(): break
            working_on[thread_num] = "Done"

        global threads  # Made a global variable so as to make it gracefully terminate on KeyboardInterrupt
        threads = [threading.Thread(target=helper, daemon=True,
                                    args=(page_queue, images, dl_handler, path_handler, i, working_on, Count))
                   for i in range(config['threads'])]

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
              '\n' + borders, "\nDone!")

        if config["type"] == 'pdf':
            # Convert to PDF
            print("[ Converting to PDF ]")
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

        print("Completed conversion!")
        print(f'Saved at {path_handler.final_path}')
        # Remove temp images
        print("[ Removing Temp Data ]")
        shutil.rmtree(temp_folder)
        if platform == "win32":
            print("Done!\n")
        else:
            print("Done ✅\n")

        try:
            log.write(f'{log_statement}[SUCCESS] {dl_handler.title}.\n')
        except:
            # In case a unicode character cannot be written to history log.
            log.write(f'{log_statement}[SUCCESS] [LOG ERROR] Title could not be recorded due to bad character.\n')


def get_command(output_folder, temp_folder, log, batch=""):
    input_prompt = "Enter ID(s)/webpage URL(s)/Command: "
    num_input = batch if batch else findall(r"((?:\d+)|(?:help)|(?:open)|(?:done))", input(input_prompt))
    while num_input[0] != "done":
        if num_input[0] == "open":
            open_folder(output_folder)
            print()
        elif num_input[0] == "help":
            show_help()
        else:
            process_queue(num_input, output_folder, temp_folder, log)
        # Ask for more input
        history_log.flush()
        num_input = findall(r"((?:\d+)|(?:help)|(?:open)|(?:done))", input(input_prompt))


def parse_config(log: TextIOWrapper):
    f = open('config.txt').read()

    # Read into a dict
    config = defaultdict(lambda: None, {i: (j or None) for i, j in findall(r'\n([A-Za-z]+) = "(.*)"', f)})

    # Name and output folder check
    if config["path"] is None:
        log.write("No output path has been set, defaulting to cwd")
        config["path"] = os.path.join(os.getcwd(), 'hentai')
    if config["name"] is None:
        log.write("No naming structure has been provided, defaulting to id")
        config["name"] = "{Id}"
    log.write(f'Output folder is {config["path"]}')
    log.write(f'File structure is", {config["name"]}')

    # File format
    if config['type'] is None or config['type'].lower() not in ('pdf', 'cbt', 'cbz', 'cbr', 'img'):
        config['type'] = 'pdf'
    log.write(f'Doujin will be saved as a {config["type"].upper()} file.')

    # Threads
    if config["threads"] is None:
        config["threads"] = 1
    else:
        config["threads"] = int(config["threads"])
    log.write(f'Threads for downloading: {config["threads"]}')

    # Batch downloading parse + check
    batch = None
    if config["batch"] is None:
        log.write("Batch downloading has been turned off")
    else:
        log.write("Batch downloading has been turned on")
        print("Downloading from inputs provided in file at:", config["batch"])
        if os.path.exists(config['batch']):
            batch = findall(r"\d+", open(config['batch']).read())
            print("\nDownloading the following ids:", *batch, sep="\n")
            os.system("pause")
            # Cleanup
            open('config.txt', 'w').write(sub(r'batch = ".*"', r'batch = ""', f))
        else:
            print('Such a file {} does not exist, skipping batch download'.format(config['batch']))
    config["batch"] = batch

    return dict(config)


if __name__ == "__main__":
    # Start program
    print("[ nhentai downloader ]\n")

    # Made a global variable so as to gracefully terminate on KeyboardInterrupt. See below
    threads = []

    # Log messages should go to log.
    log_file = open('console.log', 'w')

    if not os.path.exists('config.txt'):
        open('config.txt', 'w').write(default_config)
    config = parse_config(log_file)
    

    output_folder = config['path']
    all_temp = os.path.join(output_folder, 'temp')
    history_log = open('history.log', 'a+')
    history_log.write(f'{datetime.datetime.now()} || Script Started')
    history_log.write(f'{datetime.datetime.now()} || Config: {config}')

    exit_event = threading.Event()
    exit_event.set()

    try:
        if config['batch']:
            get_command(output_folder, all_temp, history_log, config['batch'])
            config['batch'] = None
        else:
            print("Enter 'help' to see usage and commands\n")
            get_command(output_folder, all_temp, history_log)
    except KeyboardInterrupt:
        exit_event.clear()
        print("\n\nWaiting for threads to terminate")
        for i in threads: i.join()
        print("Terminated successfully")
    if os.path.exists(all_temp):
        shutil.rmtree(all_temp)

    history_log.close()
    print("\n---Program End---")
