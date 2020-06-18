#### nh-pdf-downloader
*_IMPORTATN UPDATE (6/18): nhentai has recently updated their website that changes the webpage structure of a given doujin. This project has been updated for the new changes. If your previous download of this repo did not work, please redownload / reclown now. Thank you_*
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
#### Build
> Use Pyinstaller and Anaconda to build
```
$ pip install pyinstaller
$ pyinstaller __main__.py
```

## Running the Script
> Navigate to the repo directory on your local machine. Then execute the following:
```
$ python3 __main__.py
```

## Running the build
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
* Use a (or multiple) doujin ID number(s) (which can be found in the URL; for instance, ```152969```).
* Enter those number when prompted (if multiple, separate by space).
* The program will download and covert all images into a pdf and save it in a subfolder where the python script is.
```
- nh-pdf-downloader/
    - hentai/
        - example1.pdf
        - example2.pdf
    - __main__.py
```
> _Note: as the images are being downloaded, a temporary folder is created to store the images. this folder will be deleted upon completion._
* When you are done, enter ```done``` to exit script

## Feature Request and Planned Features
Feel free to request features. 
#### Planned Features
- [x] ~Enter multiple numbers at once (and let the script download all)~
- [ ] Create a config file that would allow the user to specify an output folder (and call it whatever they want)
- [ ] Add CBR/CBZ support
- [ ] Add config for automatically putting downloaded PDF into a subfolder named after its parody, author, or language.
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
