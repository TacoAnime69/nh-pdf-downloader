# nhentai PDF Downloader
> Downloads and coverts any doujin/manga from nhentai to PDF

## Installation
#### Clone
- Clone this repo to your local machine using ```https://github.com/TacoAnime69/nh-pdf-downloader```
#### Setup
> update and install packages
```
$ pip3 install --upgrade pip
$ pip3 install -r requirements.txt
```

## Running the Script
> Navigate to the repo directory on your local machine. Then execute the following:
```
$ python3 __main__.py
```

## Build
> Use Pyinstaller and Anaconda to build
```
$ pip install pyinstaller
$ pyinstaller __main__.py
```

#### Running the build
_Windows_
> Navigate to the dist directory ```cd dist\__main__\```
```
$ __main__.exe
```
_MacOS or Linux_
> Navigate to the dist directory ```cd dist/__main__/```
```
$ __main__.out
```

## Usage
```
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
        Note: If a doujin has the same name as an already downloaded item, then it will skip that download.
              If a doujin has a name that is too long, a warning will appear and prompt to enter a new name.
	
    Usage:
        Enter ID(s)/webpage URL(s)/Command: [ID number(s)/webpage URL(s) ... ]
        Example:
        Enter ID(s)/webpage URL(s)/Command: 111111 222222,333333https://nhentai.net/g/444444https://nhentai.net/g/555555

[ Batch Downloading from text file ]
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
        - done : This will end execution of the program. "exit" works as an alternative
        - help : This will display this text
        - open : This will open finder/files/file explorer to the default download folder
        - set  : This is used to update the value of/add a parameter to the config file from the console itself
        Usage: set <config parameter> "<value>"

    [ Threads ]
        - Set this option in the config file to specify how many pages of the same doujin are to be downloaded at once.
        - Recommended max threads is 4.

    [ Type ]
        - Set this option in the config file to specify the file type that the doujins to be saved as(pdf, cbt, cbz, cbt, img i.e unpacked).

```
> _Note: A config file will be created automatically if it does not exist in the same folder as the script._
 
> _Note: as the images are being downloaded, a temporary folder is created to store the images. this folder will be deleted upon completion._
* When you are done, enter ```done``` to exit script

## Feature Request and Planned Features
Feel free to request features. 
#### Planned Features
- [x] ~Enter multiple numbers at once (and let the script download all)~
- [x] Create a config file that would allow the user to specify an output folder (and call it whatever they want)
- [x] Add CBR/CBZ support
- [ ] Add config for automatically putting downloaded PDF into a sub-folder named after its parody, author, or language.
#### Considering
> Features that will be added if enough people request them
- A simple user interface
- A Google Chrome / Firefox / Edge extension that would connect the script and direct download from the page

## Contributing
You are welcome to contribute to this as you'd like!

## Support
*__Before reaching out for support, please read the [FAQ](https://github.com/TacoAnime69/nh-pdf-downloader/wiki/FAQ)!__*

Feel free to reach out if you have any questions!
> If you want to report a bug, please check out __Issues__ and only use email.
- Email: hentai.boi@outlook.com
- Twitter at [@TacoAnime69](https://twitter.com/TacoAnime69)
