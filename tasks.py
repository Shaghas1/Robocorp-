from robocorp import browser
from robocorp.tasks import task
from RPA.Tables import Tables
from RPA.HTTP import HTTP
from RPA.PDF import PDF
from RPA.Archive import Archive


@task
def order_robot_from_RobotSpareBin():
    """
    Order robots from RobotSpareBin Industries and
    save the order and screenshot in a zip file. 
    """
    browser.configure(slowmo=800)
    open_robot_order_website()
    download_csv_file()
    fill_the_form()
    archive_receipts()


def open_robot_order_website():
    """Open the website and clicks on pop up"""
    browser.goto("https://robotsparebinindustries.com/#/robot-order")
    page = browser.page()
    page.click('text=OK')

def download_csv_file():
    """Download the csv file"""
    http = HTTP()
    http.download("https://robotsparebinindustries.com/orders.csv", overwrite=True)

def close_annoying_modal():
    page = browser.page()
    page.click('text=OK')

def order_another_robot():
    page = browser.page()
    page.click("#order-another")

def submit_order(row):
    page = browser.page()
    part_dict = {"1" : "Roll-a-thor head","2" : "Peanut crusher head",
        "3" : "D.A.V.E head","4" : "Andy Roid head", "5" : "Spanner mate head",
        "6" : "Drillbit 2000 head"}
    page.select_option("#head", part_dict.get(row["Head"]))
    page.click('//*[@id="root"]/div/div[1]/div/div[1]/form/div[2]/div/div[{0}]/label'.format(row["Body"]))
    page.fill("input[placeholder='Enter the part number for the legs']", row["Legs"])
    page.fill("#address", row["Address"])
    while True:
        page.click("#order")
        order_another = page.query_selector("#order-another")
        if order_another:
            pdf_path = store_receipt_as_pdf(int(row["Order number"]))
            screenshot_path = screenshot_robot(int(row["Order number"]))
            embed_screenshot_to_receipt(screenshot_path, pdf_path)
            order_another_robot()
            close_annoying_modal()
            break

def fill_the_form():
    csv_file = Tables()
    robot_orders = csv_file.read_table_from_csv("orders.csv")
    for row in robot_orders:
        submit_order(row)
          

def store_receipt_as_pdf(order_number):
    page = browser.page()
    order_receipt_html = page.locator("#receipt").inner_html()
    pdf = PDF()
    pdf_path = "output/receipts/{0}.pdf".format(order_number)
    pdf.html_to_pdf(order_receipt_html, pdf_path)
    return pdf_path


def screenshot_robot(order_number):
    page = browser.page()
    screenshot_path = "output/screenshots/{0}.png".format(order_number)
    page.locator("#robot-preview-image").screenshot(path=screenshot_path)
    return screenshot_path

def embed_screenshot_to_receipt(screenshot_path, pdf_path):
    pdf = PDF()
    pdf.add_watermark_image_to_pdf(image_path=screenshot_path, 
                                   source_path=pdf_path, 
                                   output_path=pdf_path)
    
def archive_receipts():
    lib = Archive()
    lib.archive_folder_with_zip("./output/receipts", "./output/receipts.zip")
