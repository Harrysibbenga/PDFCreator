import os
import json
import base64
import pandas as pd
from datetime import date

from flask import Flask, request, abort
from fpdf import FPDF
from flask_cors import CORS
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import (Mail, Attachment, FileContent, FileName, FileType, Disposition)

app = Flask(__name__)
CORS(app)

# (w:210 mm and h:297 mm) size of A4
pdf_w = 210
pdf_h = 297
logo = 'PCW Logo.png'
title = 'Vehicle MOT Record'


def format_json_object(data_type):
    print(data_type)
    formatted_dict = {}

    for k, v in data_type.items():
        if type(v) == dict:
            for val in v.values():
                # print(k, ":", val)
                formatted_dict[k] = val
        elif type(v) == list:
            # print(k)
            # print([i for i in v])
            formatted_dict[k] = {index: item for index, item in enumerate(v)}
        else:
            # print(k, ':', v)
            formatted_dict[k] = v

    return formatted_dict


class PDF(FPDF):
    # class to use the FPDF library
    def header(self):
        self.add_font('Co', '', '/Volumes/Extreme SSD/Websites/PCW/pdf/Co Headline Corp.ttf', uni=True)
        # logo
        self.image(logo, 160, 8, 40)
        # Arial bold 15
        self.set_font('Co')
        w = self.get_string_width(title) + 6
        self.set_x((pdf_w - w) / 2)
        # Colors of frame, background and text
        self.set_draw_color(255, 255, 255)
        self.set_fill_color(255, 255, 255)
        self.set_text_color(0, 0, 0)
        # Thickness of frame (1 mm)
        self.set_line_width(1)
        # Title
        self.cell(w, 9, title, 1, 1, 'C', 1)
        # Line break
        self.ln(10)

    # Page footer
    def footer(self):
        self.add_font('Co', '', '/Volumes/Extreme SSD/Websites/PCW/pdf/Co Headline Corp.ttf', uni=True)
        # Position at 1.5 cm from bottom
        self.set_y(-15)
        # Arial italic 8
        self.set_font('Co')
        # Page number
        self.cell(0, 10, 'Page ' + str(self.page_no()), 0, 0, 'C')

    def car_info(self, name):
        self.add_font('Co', '', '/Volumes/Extreme SSD/Websites/PCW/pdf/Co Headline Corp.ttf', uni=True)

        self.set_text_color(0, 0, 0)
        # Title
        self.cell(0, 6, 'Vehicle Information', 0, 1, 'L', fill=False)
        # Line break
        self.ln(4)

        # Read text file
        with open(name, 'rb') as fh:
            txt = fh.read().decode('latin-1')
        # Times 12
        self.set_font('Co')
        # Output justified text
        self.set_fill_color(27, 63, 122)
        self.set_draw_color(27, 63, 122)
        self.set_text_color(255, 255, 255)
        self.multi_cell(0, 5, txt, fill=True, align="C")
        # Line break
        self.ln()

    def mot_info(self, name):
        self.add_font('Co', '', '/Volumes/Extreme SSD/Websites/PCW/pdf/Co Headline Corp.ttf', uni=True)
        self.set_text_color(0, 0, 0)
        # Title
        self.cell(0, 6, 'Mot History', 0, 1, 'L', fill=False)
        # Line break
        self.ln(4)
        # Read text file
        with open(name, 'rb') as fh:
            txt = fh.read().decode('latin-1')
        # Times 12
        self.set_font('Co')
        # Output justified text
        self.set_text_color(27, 63, 122)
        self.multi_cell(0, 5, txt)
        # Line break
        self.ln()

    def print_page(self, car_txt, mot_txt):
        self.add_page()
        self.car_info(car_txt)
        self.mot_info(mot_txt)


# noinspection PyPackageRequirements,PyPackageRequirements
@app.route('/create_pdf', methods=['POST'])
def create_pdf():

    today = date.today()
    today = today.strftime("%d-%m-%Y")

    data = request.get_json()

    car_info = data['carDetails']['carInfo']
    mot_info = data['carDetails']['motInfo']

    first_name = data['fname']
    last_name = data['lname']
    phone = data['phone']
    message = data['message']
    email = data['email']
    subject = data['subject']
    services = data['services']

    services = ','.join(services)

    car_dict = format_json_object(car_info)
    mot_dict = format_json_object(mot_info)

    df_car = pd.DataFrame.from_dict([car_dict])
    df_mot = pd.DataFrame.from_dict(mot_dict)

    name = str(df_car['Description'][0]) + '-' + str(df_car['reg'][0]) + '-' + str(today) + '.pdf'
    type(name)

    with open('car.txt', 'w') as f:
        f.write('\n')
        f.write(str(df_car['Description'][0]))
        f.write('\n')
        f.write('\n')
        f.write('Registration : ' + str(df_car['reg'][0]))
        f.write('\t')
        f.write('\t')
        f.write('\t')
        f.write('\t')
        f.write('Registration Year : ' + str(df_car['RegistrationYear'][0]))
        f.write('\n')
        f.write('\n')
        f.write('Colour : ' + str(df_car['Colour'][0]))
        f.write('\t')
        f.write('\t')
        f.write('\t')
        f.write('\t')
        f.write('Car Make : ' + str(df_car['CarMake'][0]))
        f.write('\n')
        f.write('\n')
        f.write('Car Model : ' + str(df_car['CarModel'][0]))
        f.write('\n')
        f.write('\n')
        f.write('Body Style : ' + str(df_car['BodyStyle'][0]))
        f.write('\n')
        f.write('\n')
        f.write('Number Of Doors : ' + str(df_car['NumberOfDoors'][0]))
        f.write('\t')
        f.write('\t')
        f.write('\t')
        f.write('\t')
        f.write('Transmission : ' + str(df_car['Transmission'][0]))
        f.write('\t')
        f.write('\t')
        f.write('\t')
        f.write('\t')
        f.write('Fuel Type : ' + str(df_car['FuelType'][0]))
        f.write('\n')
        f.write('\n')
        f.write('Engine Code : ' + str(df_car['EngineCode'][0]))
        f.write('\t')
        f.write('\t')
        f.write('\t')
        f.write('\t')
        f.write('Engine Number : ' + str(df_car['EngineNumber'][0]))
        f.write('\t')
        f.write('\t')
        f.write('\t')
        f.write('\t')
        f.write('Immobiliser : ' + str(df_car['Immobiliser'][0]))
        f.write('\n')
        f.write('\n')
        f.write('Number Of Seats : ' + str(df_car['NumberOfSeats'][0]))
        f.write('\t')
        f.write('\t')
        f.write('\t')
        f.write('\t')
        f.write('Indicative Value : ' + str(df_car['IndicativeValue'][0]))
        f.write('\t')
        f.write('\t')
        f.write('\t')
        f.write('\t')
        f.write('Driver Side : ' + str(df_car['DriverSide'][0]))
        f.write('\n')
        f.write('\n')
        f.write('Vehicle Insurance Group : ' + str(df_car['VehicleInsuranceGroup'][0]))
        f.write('\t')
        f.write('\t')
        f.write('\t')
        f.write('\t')
        f.write('Vehicle Insurance Group Out Of : ' + str(df_car['VehicleInsuranceGroupOutOf'][0]))
        f.write('\n')
        f.write('\n')
        f.write('Vehicle Identification Number : ' + str(df_car['VehicleIdentificationNumber'][0]))
        f.write('\n')
        f.write('\n')
        f.close()

    with open('mot.txt', 'w') as f:
        f.write('Tax Date : ' + str(df_mot['taxDate'][0]))
        f.write('\n')
        f.write('\n')
        for hist in df_mot[df_mot['history'].notna()]['history']:
            f.write('Test Due Date : ' + str(hist['TestDate']))
            f.write('\n')
            f.write('Expiry Date : ' + str(hist['ExpiryDate']))
            f.write('\n')
            f.write('Result : ' + str(hist['Result']))
            f.write('\n')
            f.write('Odometer : ' + str(hist['Odometer']))
            f.write('\n')
            f.write('Test Number : ' + str(hist['TestNumber']))
            f.write('\n')
            f.write('FailureReasons : ' + str(hist['FailureReasons']))
            f.write('\n')
            f.write('Advisories : ' + str(hist['Advisories']))
            f.write('\n')
            f.write('\n')
        f.close()
    try:
        # creation of an A4 pdf page in portrait measured in millimeters
        pdf = PDF(orientation='P', unit='mm', format='A4')
        pdf.set_title(title)
        pdf.set_author('PCW Website')
        pdf.print_page('car.txt', 'mot.txt')
        pdf.output(name, 'F')
    except Exception as e:
        print(e)

    message = Mail(
        from_email=email,
        to_emails='torque.webdev@gmail.com',
        subject=subject,
        html_content=
        f'''
        <strong>First name</strong>: {first_name}, <strong>Last name</strong>: {last_name}

        <strong>Phone</strong>: {phone}
        
        <strong>Services</strong>: {services}

        <strong>Message</strong>: {message}
        ''')

    with open(name, 'rb') as f:
        data = f.read()
        f.close()

    encoded_file = base64.b64encode(data).decode()

    attached_file = Attachment(
        FileContent(encoded_file),
        FileName(name),
        FileType('application/pdf'),
        Disposition('attachment')
    )

    message.attachment = attached_file
    try:
        sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)
        if os.path.exists(name):
            os.remove(name)
    except Exception as e:
        # if os.path.exists(name):
        #     os.remove(name)
        print(e)
        return abort(401, e)

    return "Message Sent, Someone will be in touch soon", 201


@app.route('/test')
def test():
    f = open('data.json')
    data = json.load(f)

    mot_dict = {}
    car_dict = {}

    for k, v in data['motInfo'].items():
        if type(v) == dict:
            for val in v.values():
                # print(k, ":", val)
                mot_dict[k] = val
        elif type(v) == list:
            # print(k)
            # print([i for i in v])
            mot_dict[k] = {index: item for index, item in enumerate(v)}
        else:
            # print(k, ':', v)
            mot_dict[k] = v

    for k, v in data['carInfo'].items():
        if type(v) == dict:
            for val in v.values():
                # print(k, ":", val)
                car_dict[k] = val
        elif type(v) == list:
            # print(k)
            # print([i for i in v])
            car_dict[k] = {index: item for index, item in enumerate(v)}
        else:
            # print(k, ':', v)
            car_dict[k] = v

    df_car = pd.DataFrame.from_dict([car_dict])
    df_mot = pd.DataFrame.from_dict(mot_dict)

    with open('car.txt', 'w') as f:
        f.write('\n')
        f.write(str(df_car['Description'][0]))
        f.write('\n')
        f.write('\n')
        f.write('Registration : ' + str(df_car['reg'][0]))
        f.write('\t')
        f.write('\t')
        f.write('\t')
        f.write('\t')
        f.write('Registration Year : ' + str(df_car['RegistrationYear'][0]))
        f.write('\n')
        f.write('\n')
        f.write('Colour : ' + str(df_car['Colour'][0]))
        f.write('\t')
        f.write('\t')
        f.write('\t')
        f.write('\t')
        f.write('Car Make : ' + str(df_car['CarMake'][0]))
        f.write('\n')
        f.write('\n')
        f.write('Car Model : ' + str(df_car['CarModel'][0]))
        f.write('\n')
        f.write('\n')
        f.write('Body Style : ' + str(df_car['BodyStyle'][0]))
        f.write('\n')
        f.write('\n')
        f.write('Number Of Doors : ' + str(df_car['NumberOfDoors'][0]))
        f.write('\t')
        f.write('\t')
        f.write('\t')
        f.write('\t')
        f.write('Transmission : ' + str(df_car['Transmission'][0]))
        f.write('\t')
        f.write('\t')
        f.write('\t')
        f.write('\t')
        f.write('Fuel Type : ' + str(df_car['FuelType'][0]))
        f.write('\n')
        f.write('\n')
        f.write('Engine Code : ' + str(df_car['EngineCode'][0]))
        f.write('\t')
        f.write('\t')
        f.write('\t')
        f.write('\t')
        f.write('Engine Number : ' + str(df_car['EngineNumber'][0]))
        f.write('\t')
        f.write('\t')
        f.write('\t')
        f.write('\t')
        f.write('Immobiliser : ' + str(df_car['Immobiliser'][0]))
        f.write('\n')
        f.write('\n')
        f.write('Number Of Seats : ' + str(df_car['NumberOfSeats'][0]))
        f.write('\t')
        f.write('\t')
        f.write('\t')
        f.write('\t')
        f.write('Indicative Value : ' + str(df_car['IndicativeValue'][0]))
        f.write('\t')
        f.write('\t')
        f.write('\t')
        f.write('\t')
        f.write('Driver Side : ' + str(df_car['DriverSide'][0]))
        f.write('\n')
        f.write('\n')
        f.write('Vehicle Insurance Group : ' + str(df_car['VehicleInsuranceGroup'][0]))
        f.write('\t')
        f.write('\t')
        f.write('\t')
        f.write('\t')
        f.write('Vehicle Insurance Group Out Of : ' + str(df_car['VehicleInsuranceGroupOutOf'][0]))
        f.write('\n')
        f.write('\n')
        f.write('Vehicle Identification Number : ' + str(df_car['VehicleIdentificationNumber'][0]))
        f.write('\n')
        f.write('\n')

    with open('mot.txt', 'w') as f:
        f.write('Tax Date : ' + str(df_mot['taxDate'][0]))
        f.write('\n')
        f.write('\n')
        for hist in df_mot[df_mot['history'].notna()]['history']:
            f.write('Test Due Date : ' + str(hist['TestDate']))
            f.write('\n')
            f.write('Expiry Date : ' + str(hist['ExpiryDate']))
            f.write('\n')
            f.write('Result : ' + str(hist['Result']))
            f.write('\n')
            f.write('Odometer : ' + str(hist['Odometer']))
            f.write('\n')
            f.write('Test Number : ' + str(hist['TestNumber']))
            f.write('\n')
            f.write('FailureReasons : ' + str(hist['FailureReasons']))
            f.write('\n')
            f.write('Advisories : ' + str(hist['Advisories']))
            f.write('\n')
            f.write('\n')

    # creation of an A4 pdf page in portrait measured in millimeters
    pdf = PDF(orientation='P', unit='mm', format='A4')
    pdf.set_title(title)
    pdf.set_author('PCW Website')
    pdf.print_page('car.txt', 'mot.txt')
    pdf.output('test.pdf', 'F')

    message = Mail(
        from_email='harry@torquetogether.com',
        to_emails='harry@torque.racing',
        subject='Sending with Twilio SendGrid is Fun',
        html_content='<strong>and easy to do anywhere, even with Python</strong>')

    with open('test.pdf', 'rb') as f:
        data = f.read()
        f.close()

    encoded_file = base64.b64encode(data).decode()

    attached_file = Attachment(
        FileContent(encoded_file),
        FileName('test.pdf'),
        FileType('application/pdf'),
        Disposition('attachment')
    )

    message.attachment = attached_file
    try:
        sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)
    except Exception as e:
        print(e)

    return 'Message Sent'


if __name__ == '__main__':
    app.run(debug=True, port=3000,)
