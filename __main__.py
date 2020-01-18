# nhentai downloader
# Date modified: January 18, 2020

from lxml import html
from PIL import Image
import requests, os, shutil


if __name__ == "__main__":
    print(f"[ nhentai downloader pdf ]")
    input_prompt = "Enter number or enter 'done': "
    num_input = input(input_prompt)
    while num_input != "done":
        # Get doujin info
        print("--- Fetching ---")
        gallery_link = f"https://nhentai.net/g/{num_input}/"
        page = requests.get(gallery_link)
        tree = html.fromstring(page.content)
        title, pages = ["", ""]
        try:
            title = str(tree.xpath('//div[@id="info"]/h1/text()')[0]).replace("*", '')
            pages, dump = str(tree.xpath('//div[@id="info"]/div/text()')[0]).split()
        except:
            print("Hentai not found.\n")
            num_input = input(input_prompt)
            break
        print(f"Title: {title}")
        print(f"Pages: {pages}")

        # Begin download images
        print("--- Downloading ---")
        path = os.path.join(os.getcwd(), f"temp-{title}")
        output_path = os.path.join(os.getcwd(), 'hentai')
        os.mkdir(path)
        os.mkdir(output_path)
        images = []
        for p in range(int(pages)):
            print(f"Page {p+1}/{pages}...")
            curr_page = f"https://nhentai.net/g/{num_input}/{p+1}/"
            page = requests.get(curr_page)
            tree = html.fromstring(page.content)
            img_link = tree.xpath('//img[@class="fit-horizontal"]/@src')
            img_file = os.path.join(f"temp-{title}", f"{p+1}.jpg")
            temp_img = open(img_file, 'wb')
            temp_img.write(requests.get(img_link[0]).content)
            temp_img.close()
            images.append(Image.open(img_file))

        # Convert to PDF
        print("--- Converting to PDF ---")
        converted = []
        for img in images:
            converted.append(img.convert('RGB'))
        first_page = converted[0]
        converted.remove(first_page)
        first_page.save(f"hentai/{title}.pdf", save_all=True, append_images=converted)

        # Remove temp images
        print("--- Removing Temp Data ---")
        shutil.rmtree(path)
        print("Done!\n")

        # Ask for more input
        num_input = input(input_prompt)
    print("---Program End---")
