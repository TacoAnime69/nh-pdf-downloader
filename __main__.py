# nhentai downloader
# Date modified: January 18, 2020

from lxml import html
from PIL import Image
import requests, os, shutil, sys


def problem_char_rm(address: str, char_set: list) -> str:
    """
    Function to remove problematic characters of a path.
    Any characters that causes the "windows can't create this path because it 
    contains illegal characters" should be removed here

    Parameters
    ----------
    address : str
        The path string
    char_set : list
        A list of characters that can potentially cause issues

    Returns
    -------
    str
        The address with the characters removed
    """
    result = address
    for char in char_set:
        # go through each character in the set and replace with nothing
        result = result.replace(char, "")
    return result


if __name__ == "__main__":
    # Start program
    print(f"[ nhentai downloader pdf ]\n")
    input_prompt = "Enter number or enter 'done': "
    num_input = input(input_prompt).split()
    currPos = 1
    while num_input[0] != "done":
        if (num_input[0] == "open"):
            # TODO open explorer / files on hentai folder
            pass
        else:
            for _num_ in num_input:
                # Get doujin info
                print(f"🟠 Fetching [{_num_} : {currPos} / {len(num_input)}]...")
                gallery_link = f"https://nhentai.net/g/{_num_}/"
                page = requests.get(gallery_link)
                tree = html.fromstring(page.content)
                title, pages = ["", ""]
                try:
                    # if the page doesn't exist, the following will throw an error
                    title = str(tree.xpath('//div[@id="info"]/h1/text()')[0])
                    title = problem_char_rm(title, ['*', ':', '?', '.', '"', '|', '/', '\\'])
                    pages, dump = str(tree.xpath('//div[@id="info"]/div/text()')[0]).split()
                except:
                    print("Hentai not found.\n")
                    break
                print(f"Title: {title}")
                print(f"Pages: {pages}")

                # Check to see if file exist
                final_path = f"hentai/{title}.pdf"
                if os.path.exists(final_path):
                    print("File already exist. Aborting Download.\n")
                    break
                
                # Begin download images
                print("🟡 Downloading...")
                path = os.path.join(os.getcwd(), f"temp-{title}")
                output_path = os.path.join(os.getcwd(), 'hentai')
                os.mkdir(path)
                if not os.path.exists(output_path):
                    os.mkdir(output_path)
                images = []
                for p in range(int(pages)):
                    # Fetch each image link of the gallery
                    sys.stdout.write("\rDownloading page {}/{}...".format(p+1, pages))
                    curr_page = f"https://nhentai.net/g/{_num_}/{p+1}/"
                    page = requests.get(curr_page)
                    tree = html.fromstring(page.content)
                    img_link = tree.xpath('//img[@class="fit-horizontal"]/@src')
                    # Save image to temp folder
                    img_file = os.path.join(f"temp-{title}", f"{p+1}.jpg")
                    temp_img = open(img_file, 'wb')
                    temp_img.write(requests.get(img_link[0]).content)
                    temp_img.close()
                    # Add to list of images for conversion later
                    images.append(Image.open(img_file))
                    sys.stdout.flush()
                print("Done ✅")

                # Convert to PDF
                print("🔵 Converting to PDF...")
                converted = []
                for img in images:
                    converted.append(img.convert('RGB'))
                first_page = converted[0]
                converted.remove(first_page)
                first_page.save(final_path, save_all=True, append_images=converted)
                print("Completed conversion ✅")

                # Remove temp images
                print("🟣 Removing Temp Data...")
                shutil.rmtree(path)
                print("Done ✅\n")

        # Ask for more input
        num_input = input(input_prompt).split()
    print("---Program End---")
