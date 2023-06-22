from fpdf import FPDF


class ShoppingListPDF(FPDF):
    """
    Кастомная реализация класса FPDF.
    Прописан header и footer, показывающий номер и количество страниц,
    а так же название проекта, откуда был скачан pdf-файл.
    """

    def header(self):
        self.add_font(
            'DejaVu', '',
            'static/fonts/DejaVuSansCondensed.ttf',
            uni=True
        )
        self.set_font('DejaVu', '', 16)
        self.cell(200, 10, txt='Ваш список покупок:', ln=1, align="C")

    def footer(self):
        self.set_y(-15)
        self.set_font("DejaVu", "", 12)
        self.cell(0, 10,
                  f"Страница {self.page_no()} из {self.alias_nb_pages()}",
                  align="C")
        self.cell(0, 10, 'Foodgram', align="R")


def generate_pdf(queryset):
    """
    Функция, по генерации pdf-файла из отфильтрованного
    django queryset. dest='S' подразумевает возврат файла
    в строковом представлении, response в view функции отвечает
    за сигнатуру.

    :param queryset:
    :return: string
    """
    pdf = ShoppingListPDF(orientation='P', unit='mm', format='A4')
    pdf.add_page()
    pdf.add_font(
        'DejaVu', '',
        'static/fonts/DejaVuSansCondensed.ttf',
        uni=True
    )
    pdf.set_font('DejaVu', '', 16)
    for ingredient in queryset:
        pdf.cell(w=0, h=10, ln=1,
                 txt=(f'{ingredient["ingredient__name"]}'
                      f' - {str(ingredient["total_amount"])}'
                      f' {ingredient["ingredient__measurement_unit"]}'),
                 align='L')

    result = pdf.output(dest='S').encode('latin-1')

    return result
