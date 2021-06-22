class PDFHandler:
    @staticmethod
    def save_to_pdf(images, output_path):
        converted = (img.convert('RGBA').convert('RGB') for img in images)
        first_page = next(converted)
        first_page.save(output_path, save_all=True, append_images=converted)
