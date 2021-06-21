# nhentai downloader
# Date modified: June 20, 2021

from re import findall, sub
from PIL import Image
from lxml import html
from sys import platform
from zipfile import ZipFile
from collections import defaultdict
import requests, os, shutil, datetime, threading

if platform == 'win32':
    import winreg

#Do not edit
defaultconfig="""
#Keys and values are to be provided in a [<key> = "<value>"] format.
#The spaces, = and the quotes are a must. The line is read and is stored
# into a config dict as <key>:<value> pairs where both the key and value are strings.
#Keys may contain only upper/lower english alphabets. Any double quote inside the value 
# must preceeded by a \\(backslash).
#If a line starts with a non alphabetic character then that line is considered commented,
# but preferably use # to indicate comments

#Set file name structure
#Possible identifiers are {Id}, {Name}. Example: *name = "{Id}-{Name}"* will name the file as its id followed by its name with a "-" in between
name = "" 

#Set Path for output folder, defaults to cwd if left blank. Example: *path = ".\hentai"* means a hentai folder where this file file exists or 
# you can just use the absolute filepath
path = "" 

#Set Location of text file containing Ids/webpage URLs. Ids must be separated by any delimiter. URLs need nothing
#It will read the largest consecutive group of numbers as 1 Id hence why Ids must be separated
batch = ""

#Set how many pages are downloaded at once, defaults to 1 if empty. Do not recommend going above 6 threads
threads = ""

#Sets the file type of the final output. Available types are pdf, cbz, cbt, cbz. Case-Sensitive. 
#Defaults to pdf for empty/any other value
type = "pdf"
"""

class DownloadHandler:
    def __init__(self, id_num):
        self.id_num = id_num
        page = requests.get(f'https://nhentai.net/g/{self.id_num}/')
        tree = html.fromstring(page.content)
        try:
            # if the page doesn't exist, the following will throw an error
            title = str(tree.xpath('//div[@id="info"]/h1/span[@class="pretty"]/text()')[0])
            try:
                title += str(tree.xpath('//div[@id="info"]/h1/span[@class="after"]/text()')[0])
            except:
                pass
            self._title = title
            # print(len(tree.xpath('//div[@class="thumb-container"]')))
            self._pages = int(
                len(tree.xpath('//div[@class="thumb-container"]')))
            self._valid = True
            # self._valid = False # DEBUG ONLY
        except:
            self._valid = False
        return

    def save_image(self, at_page, destination):
        curr_page = f"https://nhentai.net/g/{self.id_num}/{at_page}/"
        page = requests.get(curr_page)
        tree = html.fromstring(page.content)
        img_link = tree.xpath('//section[@id="image-container"]/a/img/@src')
        # Save image to temp folder
        img_file = os.path.join(destination, f"{at_page}.png")
        temp_img = open(img_file, 'wb')
        temp_img.write(requests.get(img_link[0]).content)
        temp_img.close()
        if config['type'] != 'pdf': #If the Doujin is to be saved as a CBx file
            Image.open(img_file).save(os.path.join(destination, f"{at_page}.jpg"), quality = 100)
            img_file = f"{at_page}.jpg"
        return img_file

    @property
    def title(self):
        return self._title

    @property
    def valid(self):
        return self._valid

    @property
    def pages(self):
        return self._pages

class PDFHandler:
    def save_to_pdf(self, images, output_path):
        converted = []
        #for img_num, img in enumerate(images): Debug only
        for img in images:
            # print(f'Converting {img_num}')  Debug only
            converted.append(img.convert('RGBA').convert('RGB'))
        first_page = converted[0]
        converted.remove(first_page)
        first_page.save(output_path, save_all=True, append_images=converted)

class PathHandler:
    def __init__(self, folder_path: str, temp_path: str, name: str, id_num: int):
        self.path_dir = folder_path
        self.__format = config['type']
        self.bad_chars = ['*', ':', '?', '.', '"', '|', '/', '\\', '<', '>']
        fname = config["name"].format(Id = id_num, Name = name)
        self.file_name = self.__problem_char_rm(fname)
        # print(self.__set_path())
        self._final_path = self.__set_path()
        self._temp_path = os.path.join(temp_path, f'temp-{id_num}')

    @property
    def valid(self):
        #This reg key if set to 1 removes the char limit for path
        if platform == 'Win32':
            long_paths_enabled = winreg.QueryValueEx( winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
            r'SYSTEM\CurrentControlSet\Control\FileSystem'), 'LongPathsEnabled')[0] == 1
        else:
            long_paths_enabled = False
        return long_paths_enabled or (len(self._final_path) < 200)

    @property
    def unique(self):
        return not os.path.exists(self._final_path)

    @property
    def temp_path(self):
        return self._temp_path

    @property
    def final_path(self):
        return self._final_path

    def rename_path(self, name):
        self.file_name = self.__problem_char_rm(name)
        self._final_path = self.__set_path()

    def __set_path(self):
        return os.path.join(f'{self.path_dir}', f'{self.file_name}.{self.__format}')

    def __problem_char_rm(self, address: str) -> str:
        """
        Function to remove problematic characters of a path.
        Any characters that causes the "windows can't create this path because it 
        contains illegal characters" should be removed here

        Parameters
        ----------
        address : str
            The path string

        Returns
        -------
        str
            The address with the characters removed
        """
        result = address
        for char in self.bad_chars:
            # go through each character in the set and replace with nothing
            result = result.replace(char, "")
        return result

def open_folder(folder_path: str):
    if platform == "darwin":
        os.system(f'open {folder_path}/')
    elif platform == "win32":
        os.system(f'start {folder_path}\\')

def show_help():
    message = """
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
                  -ID(s) need any non numeric delimiter whether it be whitespace or hypen or mixed, whereas URL(s) 
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
                    batch = ".\\test.txt"
                and all the doujins posted will be downloaded when the script is run
            Note: The batch line in the config.txt will be reset every time the script is executed
                
            [ Other Options ]
            When prompted, you may enter one of the other commands:
            - done : this will end execution of the program
            - help : this will display this text
            - open : this will open finder/files/file explorer to the
                     default download folder

            [ Threads ]
            - Set this option in the config file to specify how many pages of the same doujin are to be downloaded at once

            [ Type ]
            - Set this option in the config file to specify the file type that the doujins to be saved as(pdf, cbt, cbz).
            """
    print(message)

def process_queue(dl_queue, output_folder, temp_folder, log):
    for currPos, id_num in enumerate(dl_queue, 1):
        # Create log statement
        date = datetime.datetime.now()
        log_statement = f'{date} | ID: {id_num} '

        # Get doujin info
        print(f'[ Fetching {id_num} ({currPos} / {len(dl_queue)}) ]')
        dl_handler = DownloadHandler(id_num)
        if not dl_handler.valid:
            print('ERROR - Doujin not found. Skipped\n')
            log_statement += '[ERROR] Doujin not found.\n'
            log.write(log_statement)
            continue
        print(f'Title: {dl_handler.title}')
        print(f'Pages: {dl_handler.pages}')

        # Check to see if file exist
        path_handler = PathHandler(output_folder, temp_folder, dl_handler.title, id_num)
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
        
        #Start dividing pages based on number of threads to assign the downloading tasks
        pages_divide, i = [[] for _ in range(config["threads"])], 0
        for j in range(dl_handler.pages):
            pages_divide[i].append(j+1)
            i += 1
            if i >= len(pages_divide): i = 0
        
        """
        Threading stuff below
        - The working_on variable is used to store a dict and update the screen to show which thread
          is downloading which file at a given time, basically what a thread is working on atm
        - Images was changed into a dict(was a list before) so that the order of pages is maintained
        - The before variable is used to store the no of threads existing before the program creates new
          threads so that once the threads created by the program terminates, the program goes into the 
          next stage. While it is possible to iterate through the list checking if the thread is alive using
          is_alive, I felt that this might be a better solution
        - The threads list stores the threads created
        - The Count list variable stores the number of pages downloaded
        """
        images, working_on, Count = {}, {i:None for i in range(config["threads"])}, [0]
        
        def helper(pages, images, dl_handler, path_handler, thread_num, working_on, Count):
            for p in pages:
                working_on[thread_num] = p #Set which page thread is working on
                # Fetch each image link of the gallery
                img_path = dl_handler.save_image(p, path_handler.temp_path)
                # Add to list of images for conversion later
                images[p], Count[0] = img_path, Count[0] + 1
            working_on[thread_num] = "Done"
        before = threading.active_count()#Keep count of how many threads already existed
        threads = [threading.Thread(
                        target = helper, 
                        args = (pages, images, dl_handler, path_handler, i, working_on, Count)) 
                    for i, pages in enumerate(pages_divide)]
        
        for i in threads: i.start()

        #Prints current download status
        print("|Thread ID : |" + '|'.join("{:>5}".format(i) for i in range(config["threads"]))+'|Dwnl.|Total|Completed%')
        template = "|On Page Num:|" + '{:>5}|'*(config["threads"]+2) + '{:>10}' + '\r'
        old_working_on = {i:working_on[i] for i in working_on}
        print(template.format(*[working_on[i] for i in range(config["threads"])]+[0, dl_handler.pages, 0]), end='')
        
        while threading.active_count() - before: #Check if newly created threads have terminated
            if working_on != old_working_on: #Updates the screen only if a thread moves on to the next page
                print(template.format(*[working_on[i] for i in range(config["threads"])]
                        +[Count[0], dl_handler.pages, '{:.2f}'.format(100*Count[0]/dl_handler.pages)]), end='')
                old_working_on.update(working_on)
        print(template.format(*(['Done' for _ in range(config["threads"])]+[Count[0], dl_handler.pages, '100.00'])))
        print("Done!")

        if config["type"] == 'pdf':
            # Convert to PDF
            print("[ Converting to PDF ]")
            images = [Image.open(images[i+1]) for i in range(dl_handler.pages)]
            pdf_handler = PDFHandler()
            pdf_handler.save_to_pdf(images, path_handler.final_path)
        else:
            print(f'[ Converting to {config["type"].upper()} ]')
            file = ZipFile(path_handler.final_path, 'w')
            cwd = os.getcwd()
            os.chdir(path_handler.temp_path)
            for i in images: 
                newname = f"{images[i]}".zfill(8)
                os.rename(f"{images[i]}", newname)
                file.write(newname)
            os.chdir(cwd)
            file.close()
        
        print("Completed conversion!")

        # Remove temp images
        print("[ Removing Temp Data ]")
        shutil.rmtree(temp_folder)
        print(f'Saved at {path_handler.final_path}')
        if platform == "win32":
            print("Done!\n")
        else:
            print("Done ✅\n")

        try:
            log.write(f'{log_statement}[SUCCESS] {dl_handler.title}.\n')
        except:
            # In case a unicode character cannot be written to history log.
            log.write(f'{log_statement}[SUCCESS] [LOG ERROR] Title could not be recorded due to bad charaacter.\n')

def get_command(output_folder, temp_folder, log, batch = ""):
    input_prompt = "Enter ID(s)/webpage URL(s)/Command: "
    num_input = batch if batch else findall(r"((?:\d+)|(?:help)|(?:open)|(?:done))", input(input_prompt))
    while num_input[0] != "done":
        if num_input[0] == "open":
            open_folder(output_folder)
            print()
        elif num_input[0] == "help": show_help()
        else: process_queue(num_input, output_folder, temp_folder, log)
        # Ask for more input
        history_log.flush()
        num_input = findall(r"((?:\d+)|(?:help)|(?:open)|(?:done))", input(input_prompt))

def parse_config():
    f = open('config.txt').read()
    
    #Read into a dict
    config = defaultdict(lambda: None, {i:(j or None) for i,j in findall(r'\n([A-Za-z]+) = "(.*)"', f)})
    
    #Name and output folder check
    if config["path"] is None: 
        print("No output path has been set, defaulting to cwd")
        config["path"] = os.path.join(os.getcwd(), 'hentai')
    if config["name"] is None:
        print("No naming structure has been provided, defaulting to id")
        config["name"] = "{Id}"
    print()
    print("Output folder is", config["path"])
    print("File structure is", config["name"], "\n")
    
    #File format
    if config['type'] is None or config['type'].lower() not in ('pdf', 'cbt', 'cbz', 'cbr'):
        config['type'] = 'pdf'
    print("Doujin will be saved as a", config['type'].upper(), 'file.')

    #Threads
    if config["threads"] is None: config["threads"] = 1
    else: config["threads"] = int(config["threads"])
    print("Threads for downloading:", config["threads"], '\n')

    #Batch downloading parse + check
    batch = None
    if config["batch"] is None: print("Batch downloading has been turned off")
    else:
        print("Batch downloading has been turned on")
        print("Downloading from inputs provided in file at:", config["batch"])
        if os.path.exists(config['batch']): 
            batch = findall(r"\d+", open(config['batch']).read())
            print("\nDownloading the following ids:", *batch, sep = "\n")
            os.system("pause")
            #Cleanup
            open('config.txt', 'w').write(sub(r'batch = ".*"', r'batch = ""', f))
        else: print('Such a file {} does not exist, skipping batch download'.format(config['batch']))
    print()
    config["batch"] = batch

    return dict(config)

if __name__ == "__main__":
    # Start program
    print("[ nhentai downloader pdf ]\n")
    
    if os.path.exists('config.txt'): config = parse_config()
    else: 
        open('config.txt', 'w').write(defaultconfig)
        config = parse_config()
    
    output_folder = config['path']
    all_temp = os.path.join(output_folder, 'temp')
    history_log = open('history.log', 'a+')
    history_log.write(f'{datetime.datetime.now()} || Script Started')
    history_log.write(f'{datetime.datetime.now()} || Config: {config}')
    
    try:
        if config['batch']: 
            get_command(output_folder, all_temp, history_log, config['batch'])
            config['batch'] = None
        else:
            print("Enter 'help' to see usage and commands\n")
            get_command(output_folder, all_temp, history_log)
    except KeyboardInterrupt:
        print('\n\nStopping all queues (if any).')
    if os.path.exists(all_temp):
        shutil.rmtree(all_temp)

    history_log.close()
    print("\n---Program End---")
