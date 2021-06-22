from PIL import Image

class PDFHandler:
    @staticmethod
    def save_to_pdf(images: list, output_path):
        converted = []
        for img in images:
            converted.append(img.convert('RGBA').convert('RGB'))
        first_page = converted[0]
        converted.remove(first_page)
        first_page.save(output_path, save_all=True, append_images=converted)
